# Seven RPG — AI Provider Agent
# Directive: multi-agent-architect — AI returns proposals + prose only; never mutates state.
# Directive: tokenwise — model-fallback routing (mock for MVP-0; real provider after contract test).

import logging
from graphs.state import AgentState

logger = logging.getLogger(__name__)

# Model fallback tiers (tokenwise routing taxonomy)
MODEL_TIERS = {
    "mechanical": "haiku",      # simple saves, format, lookups
    "scoped_reasoning": "sonnet",  # single-file refactor, narrative generation
    "synthesis": "opus",        # architecture decisions, multi-file
}


async def ai_provider_node(state: AgentState) -> AgentState:
    logger.info("ai_provider_node: generating narrative proposal")

    # MVP-0: deterministic mock provider (replaceable after contract test)
    user_goal = state["user_goal"]
    context = state.get("context", {})

    # Deterministic mock response (no real LLM call until stack selected + contract tested)
    proposal = {
        "type": "narrative_response",
        "prose": f"Mock narrative response to: {user_goal[:80]}",
        "events": [
            {
                "id": f"evt_{state['revision']}_1",
                "type": "narrative_advance",
                "revision_base": state["revision"],
                "authorized": True,
            }
        ],
        "attempts_unauthorized_mutation": False,
    }

    state["proposal"] = proposal
    state["context"]["narrative"] = proposal["prose"]
    state["completed_tasks"].append("get_narrative")
    state["next_agent"] = "validator"
    return state


def select_model_tier(task_class: str) -> str:
    """tokenwise: return cheapest model tier that can handle the task class."""
    return MODEL_TIERS.get(task_class, "sonnet")