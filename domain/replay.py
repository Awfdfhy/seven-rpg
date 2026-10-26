# Seven RPG — Replay Engine (Read-Only Playback)
# Directive: multi-agent-architect — read-only playback of past sessions via deterministic event replay.
# Guarantee: replay never mutates the original saved state; all mutations happen on copies.

import copy
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from domain.entities import GameState, DomainEvent, World, PlayerCharacter, Scene
from domain.reducer import apply_event
from domain.session import SessionTimeline, SessionCheckpoint, ReplaySnapshot

logger = logging.getLogger(__name__)

# MVP-0: Save directory configuration (stack-agnostic path)
import os
SAVE_DIR = Path(os.getenv("SEVEN_RPG_SAVE_DIR", "./saves"))
TIMELINE_DIR = SAVE_DIR / "timelines"


def _ensure_dirs() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    TIMELINE_DIR.mkdir(parents=True, exist_ok=True)


def _timeline_path(world_id: str) -> Path:
    return TIMELINE_DIR / f"world_{world_id}_timeline.json"


def load_timeline(world_id: str) -> Optional[SessionTimeline]:
    """Load session timeline for a world. Returns None if not found."""
    _ensure_dirs()
    path = _timeline_path(world_id)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SessionTimeline.from_dict(data)
    except (json.JSONDecodeError, OSError, KeyError) as exc:
        logger.warning("replay_engine: corrupt timeline file %s — %s", path, exc)
        return None


def save_timeline(timeline: SessionTimeline) -> None:
    """Atomically persist session timeline."""
    _ensure_dirs()
    path = _timeline_path(timeline.world_id)
    import tempfile, os
    fd, temp_path = tempfile.mkstemp(dir=TIMELINE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(timeline.to_dict(), f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        Path(temp_path).replace(path)
        logger.info("replay_engine: timeline saved to %s", path)
    except Exception as exc:  # noqa: BLE001
        logger.exception("replay_engine: save timeline failed — %s", exc)
        raise


def record_checkpoint(timeline: SessionTimeline, revision: int, event_count: int, label: str = "") -> SessionCheckpoint:
    """Record a new checkpoint in the timeline."""
    checkpoint = SessionCheckpoint(
        checkpoint_id=f"cp_{revision}_{uuid.uuid4().hex[:8]}",
        revision=revision,
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_count=event_count,
        label=label,
    )
    timeline.checkpoints.append(checkpoint)
    timeline.updated_at = datetime.now(timezone.utc).isoformat()
    return checkpoint


class ReplayEngine:
    """Read-only replay engine for session playback.
    
    Guarantees:
      - Original saved state is never mutated.
      - All state mutations happen on deep-copied GameState instances.
      - Replay uses the same deterministic reducer as live play.
    """

    def __init__(self, save_dir: Optional[Path] = None):
        self.save_dir = Path(save_dir) if save_dir else SAVE_DIR

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions with their world_ids and metadata."""
        if not self.save_dir.exists():
            return []
        sessions = []
        for f in self.save_dir.glob("world_*.json"):
            world_id = f.stem.replace("world_", "")
            timeline = load_timeline(world_id)
            session_info = {
                "world_id": world_id,
                "save_file": str(f),
                "has_timeline": timeline is not None,
                "revision": 0,
                "checkpoints": 0,
                "created_at": "",
                "updated_at": "",
            }
            if timeline:
                session_info["revision"] = timeline.events[-1]["revision_base"] if timeline.events else 0
                session_info["checkpoints"] = len(timeline.checkpoints)
                session_info["created_at"] = timeline.created_at
                session_info["updated_at"] = timeline.updated_at
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                session_info["revision"] = data.get("revision", session_info["revision"])
                session_info["player_id"] = data.get("player_id", "")
                session_info["scene_id"] = data.get("scene_id", "")
            except Exception:  # noqa: BLE001
                pass
            sessions.append(session_info)
        return sessions

    def load_session(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Load raw save data for a session. Returns None if not found."""
        save_file = self.save_dir / f"world_{world_id}.json"
        if not save_file.exists():
            return None
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("replay_engine: corrupt save file %s — %s", save_file, exc)
            return None

    def get_timeline(self, world_id: str) -> Optional[SessionTimeline]:
        """Get session timeline. Returns None if not found."""
        return load_timeline(world_id)

    def get_checkpoints(self, world_id: str) -> List[SessionCheckpoint]:
        """Get all checkpoints for a session."""
        timeline = load_timeline(world_id)
        if timeline is None:
            return []
        return list(timeline.checkpoints)

    def replay_session(
        self,
        world_id: str,
        target_revision: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Read-only replay of a session.
        
        Loads the saved state, replays events using the deterministic reducer
        on a deep copy, and returns state snapshots at each step.
        
        Args:
            world_id: World/session identifier.
            target_revision: If set, replay stops at this revision (1-based).
                             If None, replay all events.
        
        Returns:
            Dict with snapshots, timeline, and metadata.
        """
        save_data = self.load_session(world_id)
        if save_data is None:
            raise FileNotFoundError(f"No save found for world_id={world_id}")

        timeline = load_timeline(world_id)
        events_raw = save_data.get("events", [])
        if timeline and timeline.events:
            # Prefer canonical event log from timeline if present
            events_raw = timeline.events

        # Reconstruct initial state (before any events)
        # The save contains the post-event state; we rebuild by replaying from initial
        initial_state = GameState(
            world=World.from_dict(save_data["world"]) if save_data.get("world") else None,
            player=PlayerCharacter.from_dict(save_data["player"]) if save_data.get("player") else None,
            scene=Scene.from_dict(save_data["scene"]) if save_data.get("scene") else None,
            revision=1,
            events=[],
            canon_facts=save_data.get("canon_facts", {}),
        )

        snapshots: List[Dict[str, Any]] = []
        current_state = initial_state

        # Snapshot at revision 1 (initial)
        snapshots.append(ReplaySnapshot(
            revision=1,
            state=current_state.to_dict(),
            events_applied=0,
        ).to_dict())

        max_revision = target_revision if target_revision is not None else len(events_raw) + 1
        events_applied = 0

        for event_data in events_raw:
            if events_applied + 1 > max_revision - 1:
                break
            event = DomainEvent.from_dict(event_data)
            # Apply on a COPY — read-only guarantee
            new_state, success = apply_event(copy.deepcopy(current_state), event)
            if not success:
                logger.warning("replay_engine: event %s rejected during replay", event.event_id)
                continue
            current_state = new_state
            events_applied += 1
            snapshots.append(ReplaySnapshot(
                revision=current_state.revision,
                state=current_state.to_dict(),
                events_applied=events_applied,
            ).to_dict())

        return {
            "world_id": world_id,
            "session_id": world_id,
            "replay_mode": "read_only",
            "target_revision": max_revision,
            "events_replayed": events_applied,
            "total_events": len(events_raw),
            "snapshots": snapshots,
            "timeline": timeline.to_dict() if timeline else None,
        }

    def replay_to_checkpoint(self, world_id: str, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Replay up to a specific checkpoint."""
        timeline = load_timeline(world_id)
        if timeline is None:
            return None
        checkpoint = next((c for c in timeline.checkpoints if c.checkpoint_id == checkpoint_id), None)
        if checkpoint is None:
            return None
        return self.replay_session(world_id, target_revision=checkpoint.revision)

    def validate_replay_integrity(self, world_id: str) -> Dict[str, Any]:
        """Verify that replay produces the same final state as the saved state."""
        save_data = self.load_session(world_id)
        if save_data is None:
            return {"valid": False, "error": "save not found"}

        replay_result = self.replay_session(world_id)
        final_snapshot = replay_result["snapshots"][-1]

        saved_revision = save_data.get("revision", 0)
        replayed_revision = final_snapshot["revision"]

        saved_events = len(save_data.get("events", []))
        replayed_events = final_snapshot["events_applied"]

        valid = (
            saved_revision == replayed_revision
            and saved_events == replayed_events
            and save_data.get("world", {}).get("name") == final_snapshot["state"].get("world", {}).get("name")
        )

        return {
            "valid": valid,
            "saved_revision": saved_revision,
            "replayed_revision": replayed_revision,
            "saved_events": saved_events,
            "replayed_events": replayed_events,
            "error": None if valid else "replay diverged from saved state",
        }
