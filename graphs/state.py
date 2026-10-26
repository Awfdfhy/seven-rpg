# Seven RPG — Agent State Schema (TypedDict)
# Directive: multi-agent-architect — one typed state shared across all nodes.
# One agent = one responsibility. No combined planning+coding+testing in one node.

from typing import TypedDict, List, Dict, Optional, Any


class AgentState(TypedDict):
    """Typed state passed through the LangGraph graph.

    Guards:
      - step_count prevents infinite routing loops.
      - error holds last failure for recovery decisions.
      - next_agent validated against an allowlist before routing.
    """
    user_goal: str
    world_id: Optional[str]
    player_id: Optional[str]
    scene_id: Optional[str]
    tasks: List[str]
    completed_tasks: List[str]
    next_agent: str
    context: Dict[str, Any]
    step_count: int
    error: Optional[str]
    revision: int          # optimistic concurrency base for save/apply
    proposal: Optional[Dict[str, Any]]  # AI proposal awaiting validation
    events: List[Dict[str, Any]]        # applied domain events