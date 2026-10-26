# Seven RPG — Player Commands (Stack-Agnostic)
# Directive: multi-agent-architect — typed commands, player controls consequential choices.

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class PlayerCommand:
    """Typed player command — untrusted text parsed into structured command."""
    command_id: str
    player_id: str
    scene_id: str
    action: str          # player-submitted, untrusted text
    revision_base: int   # state revision this command is based on
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "command_id": self.command_id,
            "player_id": self.player_id,
            "scene_id": self.scene_id,
            "action": self.action,
            "revision_base": self.revision_base,
            "timestamp": self.timestamp,
        }

    @classmethod
    def create(cls, player_id: str, scene_id: str, action: str, revision_base: int) -> "PlayerCommand":
        """Factory to create a new command with unique ID."""
        return cls(
            command_id=f"cmd_{revision_base}_{uuid.uuid4().hex[:8]}",
            player_id=player_id,
            scene_id=scene_id,
            action=action,
            revision_base=revision_base,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerCommand":
        return cls(
            command_id=data["command_id"],
            player_id=data["player_id"],
            scene_id=data["scene_id"],
            action=data["action"],
            revision_base=data["revision_base"],
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )