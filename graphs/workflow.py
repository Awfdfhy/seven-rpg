# Seven RPG — LangGraph Workflow
# Directive: multi-agent-architect — wire nodes with edges and conditional routing.
# step_count guard prevents infinite loops. Async/await throughout.

import logging
from typing import Any, Optional

try:
    from langgraph.graph import StateGraph, END
    _LANGGRAPH_AVAILABLE = True
except ImportError:  # pragma: no cover
    StateGraph = None  # type: ignore
    END = "end"  # type: ignore
    _LANGGRAPH_AVAILABLE = False

from graphs.state import AgentState
from agents.supervisor_agent import supervisor_node
from agents.world_agent import world_node
from agents.player_agent import player_node
from agents.scene_agent import scene_node
from agents.action_agent import action_node
from agents.validator_agent import validator_node
from agents.ai_provider_agent import ai_provider_node
from agents.saver_agent import saver_node

logger = logging.getLogger(__name__)


def route_next(state: AgentState) -> str:
    """Conditional routing from supervisor. Validated allowlist inside supervisor_node."""
    next_agent = state.get("next_agent", "end")
    logger.info("route_next: routing to %s (step=%d)", next_agent, state.get("step_count", 0))
    return next_agent


def build_graph() -> Any:
    """Build LangGraph. Raises ImportError if langgraph is not installed."""
    if not _LANGGRAPH_AVAILABLE:
        raise ImportError(
            "langgraph is not installed. Install it after stack selection (ADR-0001). "
            "Use mvp0_runner.py for dependency-free MVP-0 execution."
        )
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("world", world_node)
    graph.add_node("player", player_node)
    graph.add_node("scene", scene_node)
    graph.add_node("action", action_node)
    graph.add_node("validator", validator_node)
    graph.add_node("ai_provider", ai_provider_node)
    graph.add_node("saver", saver_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "world": "world",
            "player": "player",
            "scene": "scene",
            "action": "action",
            "validator": "validator",
            "ai_provider": "ai_provider",
            "saver": "saver",
            "end": END,
        },
    )

    # All agents return to supervisor for next routing decision
    graph.add_edge("world", "supervisor")
    graph.add_edge("player", "supervisor")
    graph.add_edge("scene", "supervisor")
    graph.add_edge("action", "supervisor")
    graph.add_edge("validator", "supervisor")
    graph.add_edge("ai_provider", "supervisor")
    graph.add_edge("saver", "supervisor")

    return graph.compile()


async def run(user_goal: str) -> AgentState:
    graph = build_graph()
    initial_state: AgentState = {
        "user_goal": user_goal,
        "world_id": None,
        "player_id": None,
        "scene_id": None,
        "tasks": [],
        "completed_tasks": [],
        "next_agent": "supervisor",
        "context": {},
        "step_count": 0,
        "error": None,
        "revision": 1,
        "proposal": None,
        "events": [],
    }
    return await graph.ainvoke(initial_state)