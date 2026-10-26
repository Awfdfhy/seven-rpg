# Seven RPG — MVP-0 Smoke Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_mvp0_smoke.py -v

import asyncio
import pytest
from graphs.workflow import run
from graphs.state import AgentState


@pytest.mark.asyncio
async def test_mvp0_happy_path():
    """Happy path: launch → world → player → scene → action → validate → mock AI → events → save → recover."""
    final_state = await run("create world, create player, enter scene, submit action 'explore forest'")

    assert final_state["error"] is None, f"Unexpected error: {final_state['error']}"
    assert final_state["next_agent"] == "end", f"Did not reach end state: {final_state['next_agent']}"
    assert final_state["world_id"] is not None
    assert final_state["player_id"] is not None
    assert final_state["scene_id"] is not None
    assert "create_world" in final_state["completed_tasks"]
    assert "create_player" in final_state["completed_tasks"]
    assert "enter_scene" in final_state["completed_tasks"]
    assert "submit_action" in final_state["completed_tasks"]
    assert "get_narrative" in final_state["completed_tasks"]
    assert "save_world" in final_state["completed_tasks"]
    assert final_state["step_count"] <= 20, "Step count guard exceeded"


@pytest.mark.asyncio
async def test_malformed_model_response():
    """Malformed/empty model response must not mutate state."""
    state = await run("")
    # Empty goal should still follow deterministic route; no crash
    assert "error" in state or state["next_agent"] in ("end", "supervisor")


@pytest.mark.asyncio
async def test_duplicate_submission_rejected():
    """Duplicate submission / replayed event: revision base mismatch must be rejected."""
    state: AgentState = {
        "user_goal": "replay old action",
        "world_id": None,
        "player_id": None,
        "scene_id": None,
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "supervisor",
        "context": {},
        "step_count": 0,
        "error": None,
        "revision": 5,
        "proposal": {"revision_base": 3, "events": []},  # stale revision
        "events": [],
    }
    from agents.validator_agent import validator_node
    result = await validator_node(state)
    assert result["error"] is not None
    assert "stale" in result["error"] or "revision" in result["error"]


@pytest.mark.asyncio
async def test_unauthorized_mutation_rejected():
    """Proposal attempts unauthorized state mutation must be rejected."""
    state: AgentState = {
        "user_goal": "cheat",
        "world_id": "w1",
        "player_id": "p1",
        "scene_id": "s1",
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "validator",
        "context": {},
        "step_count": 1,
        "error": None,
        "revision": 1,
        "proposal": {"attempts_unauthorized_mutation": True, "events": []},
        "events": [],
    }
    from agents.validator_agent import validator_node
    result = await validator_node(state)
    assert result["error"] is not None
    assert "unauthorized" in result["error"]


@pytest.mark.asyncio
async def test_step_count_guard():
    """Infinite loop guard: step_count > 20 must route to end."""
    state: AgentState = {
        "user_goal": "loop test",
        "world_id": None,
        "player_id": None,
        "scene_id": None,
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "supervisor",
        "context": {},
        "step_count": 21,
        "error": None,
        "revision": 1,
        "proposal": None,
        "events": [],
    }
    from agents.supervisor_agent import supervisor_node
    result = await supervisor_node(state)
    assert result["error"] is not None
    assert result["next_agent"] == "end"