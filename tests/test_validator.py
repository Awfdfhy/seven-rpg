# Seven RPG — Validator Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_validator.py -v

import pytest
from agents.validator_agent import validator_node, _has_duplicate_event_ids, _player_not_authorized
from graphs.state import AgentState


def make_state(overrides: dict | None = None) -> AgentState:
    base: AgentState = {
        "user_goal": "test action",
        "world_id": "world_1",
        "player_id": "player_1",
        "scene_id": "scene_1",
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "validator",
        "context": {},
        "step_count": 1,
        "error": None,
        "revision": 5,
        "proposal": None,
        "events": [],
    }
    if overrides:
        base.update(overrides)
    return base


def test_validator_no_proposal_routes_to_ai_provider():
    """No proposal yet → route to ai_provider."""
    state = make_state()
    result = asyncio.run(validator_node(state))
    assert result["next_agent"] == "ai_provider"
    assert "validate_action" in result["completed_tasks"]


def test_validator_proposal_not_dict_rejected():
    """Proposal not a typed object → rejected."""
    state = make_state({"proposal": "not a dict"})
    result = asyncio.run(validator_node(state))
    assert result["error"] is not None
    assert "not a typed object" in result["error"]
    assert result["next_agent"] == "end"


def test_validator_unauthorized_mutation_rejected():
    """Unauthorized mutation attempt → rejected."""
    state = make_state({
        "proposal": {"attempts_unauthorized_mutation": True, "events": []}
    })
    result = asyncio.run(validator_node(state))
    assert result["error"] is not None
    assert "unauthorized" in result["error"]
    assert result["next_agent"] == "end"


def test_validator_stale_revision_rejected():
    """Stale revision base → rejected."""
    state = make_state({
        "proposal": {"revision_base": 3, "events": []}  # current is 5
    })
    result = asyncio.run(validator_node(state))
    assert result["error"] is not None
    assert "stale" in result["error"] or "revision" in result["error"]


def test_validator_duplicate_event_ids_rejected():
    """Duplicate event IDs → rejected."""
    state = make_state({
        "proposal": {
            "revision_base": 5,
            "events": [
                {"id": "evt_1", "type": "test"},
                {"id": "evt_1", "type": "test2"},  # duplicate
            ],
        }
    })
    result = asyncio.run(validator_node(state))
    assert result["error"] is not None
    assert "duplicate" in result["error"]


def test_validator_valid_proposal_routes_to_supervisor():
    """Valid proposal → route back to supervisor."""
    state = make_state({
        "proposal": {
            "player_id": "player_1",
            "revision_base": 5,
            "events": [{"event_id": "evt_1", "type": "narrative_advance", "authorized": True}],
            "attempts_unauthorized_mutation": False,
        }
    })
    result = asyncio.run(validator_node(state))
    assert result["error"] is None
    assert result["next_agent"] == "supervisor"


def test_has_duplicate_event_ids():
    """Helper: duplicate detection."""
    assert _has_duplicate_event_ids([{"id": "a"}, {"id": "b"}]) is False
    assert _has_duplicate_event_ids([{"id": "a"}, {"id": "a"}]) is True
    assert _has_duplicate_event_ids([]) is False


def test_player_not_authorized():
    """Helper: player authorization check."""
    state = make_state({"player_id": "player_1", "scene_id": "scene_1"})
    proposal = {"player_id": "player_2"}  # different player
    assert _player_not_authorized(state, proposal) is True

    proposal2 = {"player_id": "player_1"}  # same player
    assert _player_not_authorized(state, proposal2) is False


# Async test helper
import asyncio


def asyncio_test(coro):
    return asyncio.run(coro)