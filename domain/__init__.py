# Seven RPG — Domain Layer (Stack-Agnostic)
# Directive: multi-agent-architect — domain independent of UI and provider SDKs.
# These models can be ported to any tech stack (Flutter, React Native, Kotlin, Swift, etc.)

from domain.entities import World, PlayerCharacter, Scene, DomainEvent, GameState, create_initial_state
from domain.campaign_settings import CampaignSettings
from domain.commands import PlayerCommand
from domain.contracts import ValidationResult, Proposal, AIProviderInterface
from domain.progression import Progression, Skill, SkillTree, CharacterLevel
from domain.reducer import apply_event, validate_command
from domain.session import (
    SessionCheckpoint,
    SessionTimeline,
    ReplaySnapshot,
)
from domain.replay import (
    ReplayEngine,
    load_timeline,
    save_timeline,
    record_checkpoint,
)

__all__ = [
    "World",
    "PlayerCharacter",
    "Scene",
    "DomainEvent",
    "GameState",
    "create_initial_state",
    "CampaignSettings",
    "PlayerCommand",
    "ValidationResult",
    "Proposal",
    "AIProviderInterface",
    "Progression",
    "Skill",
    "SkillTree",
    "CharacterLevel",
    "apply_event",
    "validate_command",
    "SessionCheckpoint",
    "SessionTimeline",
    "ReplaySnapshot",
    "ReplayEngine",
    "load_timeline",
    "save_timeline",
    "record_checkpoint",
]