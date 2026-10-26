# Seven RPG — Saver Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_saver.py -v

import json
import os
import tempfile
from pathlib import Path

from agents.saver_agent import SAVE_DIR, ensure_save_dirs, load_save, list_saves, saver_node
from graphs.state import AgentState


def setup_tmp_save_dir(monkeypatch):
    """Redirect SAVE_DIR to a temp directory for isolated testing."""
    tmp = Path(tempfile.mkdtemp())
    monkeypatch.setattr("agents.saver_agent.SAVE_DIR", tmp)
    monkeypatch.setattr("agents.saver_agent.BACKUP_DIR", tmp / "backups")
    monkeypatch.setattr("agents.saver_agent.CORRUPT_DIR", tmp / "corrupt")
    ensure_save_dirs()
    return tmp


def test_saver_atomic_save(monkeypatch):
    """Atomic save creates file with correct payload."""
    tmp = setup_tmp_save_dir(monkeypatch)

    state: AgentState = {
        "user_goal": "test",
        "world_id": "world_test",
        "player_id": "player_test",
        "scene_id": "scene_test",
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "saver",
        "context": {},
        "step_count": 1,
        "error": None,
        "revision": 1,
        "proposal": None,
        "events": [{"id": "evt_1", "type": "test"}],
    }

    import asyncio
    result = asyncio.run(saver_node(state))

    assert result["error"] is None
    assert result["next_agent"] == "end"
    assert "save_world" in result["completed_tasks"]

    save_file = tmp / "world_world_test.json"
    assert save_file.exists()

    with open(save_file, "r", encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["world_id"] == "world_test"
    assert payload["revision"] == 1
    assert len(payload["events"]) == 1


def test_saver_backup_previous_version(monkeypatch):
    """Backup created when overwriting existing save."""
    tmp = setup_tmp_save_dir(monkeypatch)

    save_file = tmp / "world_world_backup.json"
    save_file.write_text('{"revision": 1, "old": true}', encoding="utf-8")

    state: AgentState = {
        "user_goal": "test",
        "world_id": "world_backup",
        "player_id": "player_test",
        "scene_id": "scene_test",
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "saver",
        "context": {},
        "step_count": 1,
        "error": None,
        "revision": 2,
        "proposal": None,
        "events": [],
    }

    import asyncio
    result = asyncio.run(saver_node(state))

    assert result["error"] is None
    backup_files = list((tmp / "backups").glob("world_world_backup_*.json"))
    assert len(backup_files) == 1


def test_load_save_nonexistent(monkeypatch):
    """Loading nonexistent world returns None."""
    tmp = setup_tmp_save_dir(monkeypatch)
    assert load_save("nonexistent") is None


def test_load_save_corrupt(monkeypatch):
    """Loading corrupt file returns None and moves to corrupt dir."""
    tmp = setup_tmp_save_dir(monkeypatch)
    save_file = tmp / "world_corrupt.json"
    save_file.write_text("{invalid json", encoding="utf-8")

    result = load_save("corrupt")
    assert result is None
    assert not save_file.exists()  # moved to corrupt
    corrupt_files = list((tmp / "corrupt").glob("corrupt_corrupt_*.json"))
    assert len(corrupt_files) == 1


def test_list_saves(monkeypatch):
    """List saved world IDs."""
    tmp = setup_tmp_save_dir(monkeypatch)
    (tmp / "world_alpha.json").write_text("{}", encoding="utf-8")
    (tmp / "world_beta.json").write_text("{}", encoding="utf-8")

    saves = list_saves()
    assert "alpha" in saves
    assert "beta" in saves
    assert len(saves) == 2