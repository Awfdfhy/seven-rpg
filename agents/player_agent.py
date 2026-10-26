# Seven RPG — Player Agent
# Directive: multi-agent-architect — one responsibility: player character creation only.

import logging
from graphs.state import AgentState

logger = logging.getLogger(__name__)


async def player_node(state: AgentState) -> AgentState:
    logger.info("player_node: creating player character for world=%s", state.get("world_id"))

    player_id = f"player_{state['revision']}"
    state["player_id"] = player_id
    state["context"]["player"] = {
        "id": player_id,
        "name": "Hero",
        "identity_sheet": {},
        "attributes": {},
        "version": 1,
    }
    state["completed_tasks"].append("create_player")
    state["next_agent"] = "scene"
    return state