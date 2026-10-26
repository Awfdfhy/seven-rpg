# Seven RPG — Supervisor Agent
# Directive: multi-agent-architect — supervisor validates routing against allowlist.
# Never trust unvalidated LLM routing decisions.

import logging
from typing import Any
from graphs.state import AgentState

logger = logging.getLogger(__name__)

ALLOWED_AGENTS = {"world", "player", "scene", "action", "validator", "ai_provider", "saver", "end"}

DELEGATION_PROMPT = """
You are the Seven RPG supervisor. Decide the next agent based on current state.
Available agents: world, player, scene, action, validator, ai_provider, saver, end.
Respond with ONLY the agent name.

Goal: {goal}
Completed: {completed}
Context keys: {context}
Step count: {step_count}
"""

async def supervisor_node(state: AgentState) -> AgentState:
    state["step_count"] += 1
    logger.info("supervisor_node: step=%d next_agent=%s", state["step_count"], state.get("next_agent"))

    # If previous node set an error, route to end to stop safely
    if state.get("error"):
        state["next_agent"] = "end"
        return state

    # Guard against infinite loops
    if state["step_count"] > 20:
        state["error"] = "max step count exceeded"
        state["next_agent"] = "end"
        return state

    # In a real implementation, call LLM here and validate output against ALLOWED_AGENTS.
    # For MVP-0 with deterministic mock, the workflow is hardcoded:
    next_agent = _deterministic_route(state)

    # Validate against allowlist (security requirement)
    if next_agent not in ALLOWED_AGENTS:
        logger.warning("supervisor_node: invalid route '%s', forcing end", next_agent)
        state["error"] = f"invalid route: {next_agent}"
        state["next_agent"] = "end"
    else:
        state["next_agent"] = next_agent

    return state


def _deterministic_route(state: AgentState) -> str:
    """MVP-0 deterministic routing until LLM integration is contract-tested."""
    completed = set(state["completed_tasks"])
    goal = state["user_goal"]

    if "create_world" not in completed:
        return "world"
    if "create_player" not in completed:
        return "player"
    if "enter_scene" not in completed:
        return "scene"
    if "submit_action" not in completed:
        return "action"
    if "validate_action" not in completed:
        return "validator"
    if "get_narrative" not in completed:
        return "ai_provider"
    if "apply_events" not in completed:
        return "validator"
    if "save_world" not in completed:
        return "saver"
    return "end"