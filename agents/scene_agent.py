# Seven RPG — Scene Agent
# Directive: multi-agent-architect — one responsibility: scene entry only.

import logging
from graphs.state import AgentState

logger = logging.getLogger(__name__)


async def scene_node(state: AgentState) -> AgentState:
    logger.info("scene_node: entering scene for player=%s", state.get("player_id"))

    scene_id = f"scene_{state['revision']}"
    state["scene_id"] = scene_id
    state["context"]["scene"] = {
        "id": scene_id,
        "world_id": state.get("world_id"),
        "player_id": state.get("player_id"),
        "canon_facts_loaded": True,
        "character_knowledge": {},
    }
    state["completed_tasks"].append("enter_scene")
    state["next_agent"] = "action"
    return state