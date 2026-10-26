# Seven RPG — MVP-0 Runner Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_mvp0_runner.py -v

import pytest
from mvp0_runner import MVP0Runner


def test_mvp0_runner_complete_journey():
    """MVP-0 runner completes all 11 steps successfully."""
    runner = MVP0Runner()
    result = runner.run()

    assert result["success"] is True
    assert result["error"] is None
    assert result["steps_completed"] == 11
    assert result["final_revision"] == 2  # Started at 1, one event applied
    assert result["world_id"] == "world_mvp_0"
    assert result["player_id"] == "player_mvp_0"
    assert result["scene_id"] == "scene_mvp_0_1"
    assert result["events_count"] == 1

    # Verify log contains all expected steps
    log_text = "\n".join(result["log"])
    assert "Launch" in log_text
    assert "Create World" in log_text
    assert "Create Player" in log_text
    assert "Enter Scene" in log_text
    assert "Submit Action" in log_text
    assert "Validate Action" in log_text
    assert "Get Narrative" in log_text
    assert "Validate Proposal" in log_text
    assert "Apply Events" in log_text
    assert "Save" in log_text
    assert "Recover" in log_text


def test_mvp0_runner_deterministic():
    """MVP-0 runner produces same result on repeated runs."""
    result1 = MVP0Runner().run()
    result2 = MVP0Runner().run()

    assert result1["success"] == result2["success"]
    assert result1["final_revision"] == result2["final_revision"]
    assert result1["events_count"] == result2["events_count"]
    assert result1["world_id"] == result2["world_id"]
    assert result1["player_id"] == result2["player_id"]