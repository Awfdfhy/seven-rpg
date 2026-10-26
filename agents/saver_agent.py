# Seven RPG — Saver Agent (Enhanced)
# Directive: multi-agent-architect — one responsibility: atomic save only.
# Save boundaries, backup, corruption recovery defined before persistence.

import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from graphs.state import AgentState

logger = logging.getLogger(__name__)

# MVP-0: Save directory configuration (stack-agnostic path, overridden after stack selection)
SAVE_DIR = Path(os.getenv("SEVEN_RPG_SAVE_DIR", "./saves"))
BACKUP_DIR = SAVE_DIR / "backups"
CORRUPT_DIR = SAVE_DIR / "corrupt"


def ensure_save_dirs() -> None:
    """Create save, backup, and corrupt directories if they don't exist."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    CORRUPT_DIR.mkdir(parents=True, exist_ok=True)


async def saver_node(state: AgentState) -> AgentState:
    """
    Atomic save for world and player state.
    MVP-0: Write to temp file, fsync, atomic rename; backup previous version.
    """
    logger.info(
        "saver_node: atomic save for world=%s player=%s revision=%d",
        state.get("world_id"),
        state.get("player_id"),
        state.get("revision"),
    )

    ensure_save_dirs()

    save_payload = {
        "world_id": state.get("world_id"),
        "player_id": state.get("player_id"),
        "scene_id": state.get("scene_id"),
        "revision": state.get("revision"),
        "events": state.get("events", []),
        "context": state.get("context", {}),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "save_version": 1,
    }

    world_id = state.get("world_id", "unknown")
    save_file = SAVE_DIR / f"world_{world_id}.json"
    backup_file = BACKUP_DIR / f"world_{world_id}_{state.get('revision', 0)}.json"

    # Backup previous version if it exists
    if save_file.exists():
        shutil.copy2(save_file, backup_file)
        logger.info("saver_node: backed up previous save to %s", backup_file)

    # Atomic write: temp file -> fsync -> atomic rename
    temp_file = None
    try:
        # Write to temp file in same directory (ensures atomic rename on same filesystem)
        fd, temp_path = tempfile.mkstemp(dir=SAVE_DIR, suffix=".tmp")
        temp_file = Path(temp_path)

        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(save_payload, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        # Atomic rename
        temp_file.replace(save_file)
        logger.info("saver_node: atomic save completed to %s", save_file)

        state["context"]["last_save"] = save_payload
        state["context"]["save_file"] = str(save_file)
        state["context"]["backup_file"] = str(backup_file)
        state["completed_tasks"].append("save_world")
        state["next_agent"] = "end"

    except Exception as exc:  # noqa: BLE001
        logger.exception("saver_node: save failed — %s", exc)
        # Move corrupted temp file to corrupt dir for inspection
        if temp_file and temp_file.exists():
            corrupt_file = CORRUPT_DIR / f"corrupt_{uuid.uuid4().hex[:8]}.json"
            shutil.move(str(temp_file), str(corrupt_file))
            logger.warning("saver_node: moved corrupt temp to %s", corrupt_file)

        state["error"] = f"save failed: {exc}"
        state["next_agent"] = "end"

    return state


def load_save(world_id: str) -> Optional[Dict[str, Any]]:
    """Load a saved world state. Returns None if not found or corrupt."""
    save_file = SAVE_DIR / f"world_{world_id}.json"
    if not save_file.exists():
        return None

    try:
        with open(save_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("saver_node: corrupt save file %s — %s", save_file, exc)
        # Move corrupt file to corrupt dir
        corrupt_file = CORRUPT_DIR / f"corrupt_{world_id}_{uuid.uuid4().hex[:8]}.json"
        shutil.move(str(save_file), str(corrupt_file))
        return None


def list_saves() -> list[str]:
    """List all saved world IDs."""
    if not SAVE_DIR.exists():
        return []
    return [f.stem.replace("world_", "") for f in SAVE_DIR.glob("world_*.json")]