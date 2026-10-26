# Seven RPG — World Agent
# Directive: multi-agent-architect — one responsibility: world creation only.

import logging
from graphs.state import AgentState

logger = logging.getLogger(__name__)


async def world_node(state: AgentState) -> AgentState:
    logger.info("world_node: creating world for goal=%s", state["user_goal"][:50])

    # MVP-0: deterministic world creation (no AI mutation of state)
    world_id = f"world_{state['revision']}"
    state["world_id"] = world_id
    state["context"]["world"] = {
        "id": world_id,
        "name": "New World",
        "canon_facts": {},
        "version": 1,
        "isolated": True,
    }
    state["completed_tasks"].append("create_world")
    state["next_agent"] = "player"
    return state