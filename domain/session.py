# Seven RPG — Session Timeline and Checkpoints (Stack-Agnostic)
# Directive: multi-agent-architect — typed session entities for replay and timeline.

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class SessionCheckpoint:
    """A lightweight point-in-time marker for a session."""
    checkpoint_id: str
    revision: int
    timestamp: str
    event_count: int
    label: str = ""
    snapshot: Optional[Dict[str, Any]] = None  # optional state snapshot

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "revision": self.revision,
            "timestamp": self.timestamp,
            "event_count": self.event_count,
            "label": self.label,
            "snapshot": self.snapshot,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionCheckpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            revision=data["revision"],
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            event_count=data.get("event_count", 0),
            label=data.get("label", ""),
            snapshot=data.get("snapshot"),
        )


@dataclass
class SessionTimeline:
    """Session timeline — ordered checkpoints and full confirmed event log."""
    session_id: str
    world_id: str
    player_id: str
    created_at: str
    updated_at: str
    checkpoints: List[SessionCheckpoint] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)  # confirmed events

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "world_id": self.world_id,
            "player_id": self.player_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "events": self.events,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionTimeline":
        return cls(
            session_id=data["session_id"],
            world_id=data["world_id"],
            player_id=data.get("player_id", ""),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            checkpoints=[SessionCheckpoint.from_dict(c) for c in data.get("checkpoints", [])],
            events=data.get("events", []),
        )


@dataclass
class ReplaySnapshot:
    """State snapshot at a specific revision during replay."""
    revision: int
    state: Dict[str, Any]
    events_applied: int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "revision": self.revision,
            "state": self.state,
            "events_applied": self.events_applied,
            "timestamp": self.timestamp,
        }
