# Seven RPG — Action Agent
# Directive: multi-agent-architect — one responsibility: player action submission only.
# Player controls consequential choices; AI never speaks for the character.

import logging
from graphs.state import AgentState

logger = logging.getLogger(__name__)


async def action_node(state: AgentState) -> AgentState:
    logger.info("action_node: submitting player action")

    # MVP-0: player action comes from user_goal; typed command recorded
    state["context"]["player_action"] = {
        "action": state["user_goal"],
        "revision_base": state["revision"],
        "player_id": state.get("player_id"),
        "scene_id": state.get("scene_id"),
    }
    state["completed_tasks"].append("submit_action")
    state["next_agent"] = "validator"
    return state