# Seven RPG — Campaign Settings Domain Entity (Stack-Agnostic)
# Directive: multi-agent-architect — typed domain entity for world configuration.

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"
DIFFICULTY_CUSTOM = "custom"
VALID_DIFFICULTIES = {DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD, DIFFICULTY_CUSTOM}

TONE_DARK = "dark"
TONE_HEROIC = "heroic"
TONE_COMEDIC = "comedic"
TONE_NEUTRAL = "neutral"
TONE_CUSTOM = "custom"
VALID_TONES = {TONE_DARK, TONE_HEROIC, TONE_COMEDIC, TONE_NEUTRAL, TONE_CUSTOM}

NPC_BEHAVIOR_FRIENDLY = "friendly"
NPC_BEHAVIOR_NEUTRAL = "neutral"
NPC_BEHAVIOR_HOSTILE = "hostile"
NPC_BEHAVIOR_DYNAMIC = "dynamic"
VALID_NPC_BEHAVIORS = {NPC_BEHAVIOR_FRIENDLY, NPC_BEHAVIOR_NEUTRAL, NPC_BEHAVIOR_HOSTILE, NPC_BEHAVIOR_DYNAMIC}


@dataclass
class CampaignSettings:
    """Campaign settings — customization per campaign."""
    campaign_settings_id: str
    world_id: str
    difficulty: str = DIFFICULTY_MEDIUM
    difficulty_multiplier: float = 1.0
    tone: str = TONE_NEUTRAL
    npc_behavior: str = NPC_BEHAVIOR_NEUTRAL
    starting_conditions: Dict[str, Any] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_settings_id": self.campaign_settings_id,
            "world_id": self.world_id,
            "difficulty": self.difficulty,
            "difficulty_multiplier": self.difficulty_multiplier,
            "tone": self.tone,
            "npc_behavior": self.npc_behavior,
            "starting_conditions": self.starting_conditions,
            "custom_settings": self.custom_settings,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CampaignSettings":
        return cls(
            campaign_settings_id=data["campaign_settings_id"],
            world_id=data["world_id"],
            difficulty=data.get("difficulty", DIFFICULTY_MEDIUM),
            difficulty_multiplier=data.get("difficulty_multiplier", 1.0),
            tone=data.get("tone", TONE_NEUTRAL),
            npc_behavior=data.get("npc_behavior", NPC_BEHAVIOR_NEUTRAL),
            starting_conditions=data.get("starting_conditions", {}),
            custom_settings=data.get("custom_settings", {}),
            version=data.get("version", 1),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )

    def is_valid(self) -> bool:
        """Validate campaign settings against known enums."""
        if self.difficulty not in VALID_DIFFICULTIES:
            return False
        if self.tone not in VALID_TONES:
            return False
        if self.npc_behavior not in VALID_NPC_BEHAVIORS:
            return False
        if not (0.1 <= self.difficulty_multiplier <= 5.0):
            return False
        return True
