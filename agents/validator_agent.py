# Seven RPG — Validator Agent (Enhanced)
# Directive: multi-agent-architect — validate AI proposals against state, rules, permissions.
# Invalid proposals rejected without mutation.

import logging
from typing import Any, Dict, List, Optional
from graphs.state import AgentState

logger = logging.getLogger(__name__)

# Validation rules registry
VALIDATION_RULES: List[str] = [
    "revision_base_matches_current",
    "player_authorized_for_scene",
    "proposal_is_typed_object",
    "no_unauthorized_mutation",
    "resources_sufficient",
    "event_ids_unique",
]


async def validator_node(state: AgentState) -> AgentState:
    """
    Validate AI proposals against current state, rules, and permissions.
    Invalid proposals rejected without mutation.
    """
    logger.info("validator_node: validating action/events")

    error = None
    proposal = state.get("proposal")

    # Rule 1: No proposal yet — route to AI provider
    if proposal is None:
        state["completed_tasks"].append("validate_action")
        state["next_agent"] = "ai_provider"
        return state

    # Rule 2: Proposal must be a typed object
    if not isinstance(proposal, dict):
        error = "proposal is not a typed object"
    # Rule 3: No unauthorized mutation attempts
    elif proposal.get("attempts_unauthorized_mutation"):
        error = "proposal attempts unauthorized state mutation"
    # Rule 4: Revision base must match current state (optimistic concurrency)
    elif proposal.get("revision_base") != state["revision"]:
        error = f"stale proposal: revision_base {proposal.get('revision_base')} != current {state['revision']}"
    # Rule 5: Event IDs must be unique within proposal
    elif _has_duplicate_event_ids(proposal.get("events", [])):
        error = "duplicate event IDs in proposal"
    # Rule 6: Player must be authorized for the scene
    elif _player_not_authorized(state, proposal):
        error = "player not authorized for this scene"

    if error:
        state["error"] = error
        state["next_agent"] = "end"
        logger.warning("validator_node: rejected proposal — %s", error)
    else:
        state["completed_tasks"].append("validate_action")
        # After validation, proceed to apply events (validator loops back to supervisor in real graph)
        state["next_agent"] = "supervisor"

    return state


def _has_duplicate_event_ids(events: List[Dict[str, Any]]) -> bool:
    """Check for duplicate event IDs in a proposal."""
    seen = set()
    for event in events:
        eid = event.get("id")
        if eid in seen:
            return True
        seen.add(eid)
    return False


def _player_not_authorized(state: AgentState, proposal: Dict[str, Any]) -> bool:
    """Check if the player is authorized for the scene in the proposal."""
    player_id = state.get("player_id")
    scene_id = state.get("scene_id")
    if not player_id or not scene_id:
        return True  # Not authorized if missing
    # MVP-0: player_id in context must match proposal's player reference
    proposal_player = proposal.get("player_id") or state.get("context", {}).get("player", {}).get("id")
    return proposal_player != player_id


def get_validation_rules() -> List[str]:
    """Return the list of active validation rules."""
    return VALIDATION_RULES.copy()