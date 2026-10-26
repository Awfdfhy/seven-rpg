# Seven RPG — Campaign Settings Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_campaign_settings.py -v

import pytest
from dataclasses import replace
from domain.campaign_settings import (
    CampaignSettings,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
    DIFFICULTY_CUSTOM,
    TONE_DARK,
    TONE_HEROIC,
    TONE_COMEDIC,
    TONE_NEUTRAL,
    TONE_CUSTOM,
    NPC_BEHAVIOR_FRIENDLY,
    NPC_BEHAVIOR_NEUTRAL,
    NPC_BEHAVIOR_HOSTILE,
    NPC_BEHAVIOR_DYNAMIC,
)
from domain.entities import GameState, World, PlayerCharacter, Scene
from domain.reducer import apply_event, create_initial_state


# --- CampaignSettings Creation Tests ---

def test_campaign_settings_creation_defaults():
    settings = CampaignSettings(campaign_settings_id="cs_1", world_id="w1")
    assert settings.campaign_settings_id == "cs_1"
    assert settings.world_id == "w1"
    assert settings.difficulty == DIFFICULTY_MEDIUM
    assert settings.difficulty_multiplier == 1.0
    assert settings.tone == TONE_NEUTRAL
    assert settings.npc_behavior == NPC_BEHAVIOR_NEUTRAL
    assert settings.starting_conditions == {}
    assert settings.custom_settings == {}
    assert settings.version == 1


def test_campaign_settings_creation_custom():
    settings = CampaignSettings(
        campaign_settings_id="cs_2",
        world_id="w2",
        difficulty=DIFFICULTY_HARD,
        difficulty_multiplier=2.0,
        tone=TONE_DARK,
        npc_behavior=NPC_BEHAVIOR_HOSTILE,
        starting_conditions={"initial_gold": 50, "starting_items": ["sword"]},
        custom_settings={"permadeath": True},
        version=3,
    )
    assert settings.difficulty == DIFFICULTY_HARD
    assert settings.difficulty_multiplier == 2.0
    assert settings.tone == TONE_DARK
    assert settings.npc_behavior == NPC_BEHAVIOR_HOSTILE
    assert settings.starting_conditions["initial_gold"] == 50
    assert settings.custom_settings["permadeath"] is True
    assert settings.version == 3


def test_campaign_settings_to_dict_and_back():
    settings = CampaignSettings(
        campaign_settings_id="cs_3",
        world_id="w3",
        difficulty=DIFFICULTY_EASY,
        tone=TONE_COMEDIC,
        npc_behavior=NPC_BEHAVIOR_FRIENDLY,
        starting_conditions={"health": 100},
        custom_settings={"hud_mode": "minimal"},
    )
    data = settings.to_dict()
    restored = CampaignSettings.from_dict(data)
    assert restored.campaign_settings_id == settings.campaign_settings_id
    assert restored.world_id == settings.world_id
    assert restored.difficulty == DIFFICULTY_EASY
    assert restored.tone == TONE_COMEDIC
    assert restored.npc_behavior == NPC_BEHAVIOR_FRIENDLY
    assert restored.starting_conditions == {"health": 100}
    assert restored.custom_settings == {"hud_mode": "minimal"}


# --- Validation Tests ---

def test_campaign_settings_validation_valid():
    settings = CampaignSettings(campaign_settings_id="cs_v1", world_id="w1")
    assert settings.is_valid() is True


def test_campaign_settings_validation_invalid_difficulty():
    settings = CampaignSettings(campaign_settings_id="cs_v2", world_id="w1", difficulty="extreme")
    assert settings.is_valid() is False


def test_campaign_settings_validation_invalid_tone():
    settings = CampaignSettings(campaign_settings_id="cs_v3", world_id="w1", tone="melancholy")
    assert settings.is_valid() is False


def test_campaign_settings_validation_invalid_npc_behavior():
    settings = CampaignSettings(campaign_settings_id="cs_v4", world_id="w1", npc_behavior="confused")
    assert settings.is_valid() is False


def test_campaign_settings_validation_invalid_multiplier():
    settings = CampaignSettings(campaign_settings_id="cs_v5", world_id="w1", difficulty_multiplier=10.0)
    assert settings.is_valid() is False
    settings2 = CampaignSettings(campaign_settings_id="cs_v6", world_id="w1", difficulty_multiplier=0.01)
    assert settings2.is_valid() is False


# --- GameState Integration Tests ---

def test_game_state_with_campaign_settings():
    state = create_initial_state("test")
    settings = CampaignSettings(campaign_settings_id="cs_gs1", world_id="w1", difficulty=DIFFICULTY_HARD)
    state = replace(state, campaign_settings=settings)
    assert state.campaign_settings is not None
    assert state.campaign_settings.difficulty == DIFFICULTY_HARD


def test_game_state_serialization_with_campaign_settings():
    state = create_initial_state("test")
    settings = CampaignSettings(
        campaign_settings_id="cs_gs2",
        world_id="w2",
        tone=TONE_DARK,
        starting_conditions={"gold": 100},
    )
    state = replace(
        state,
        world=World(world_id="w1", name="Test World"),
        player=PlayerCharacter(player_id="p1", name="Hero", world_id="w1"),
        campaign_settings=settings,
    )
    data = state.to_dict()
    restored = GameState.from_dict(data)
    assert restored.campaign_settings is not None
    assert restored.campaign_settings.difficulty == DIFFICULTY_MEDIUM
    assert restored.campaign_settings.tone == TONE_DARK
    assert restored.campaign_settings.starting_conditions["gold"] == 100
    assert restored.world.name == "Test World"
    assert restored.player.name == "Hero"


# --- Reducer Tests ---

def test_apply_event_campaign_settings_updated():
    state = create_initial_state("test")
    settings = CampaignSettings(
        campaign_settings_id="cs_red1",
        world_id="w1",
        difficulty=DIFFICULTY_EASY,
        tone=TONE_HEROIC,
    )
    event = type("FakeEvent", (), {
        "event_id": "evt_1_1",
        "type": "campaign_settings_updated",
        "revision_base": 1,
        "authorized": True,
        "payload": {"campaign_settings": settings.to_dict()},
    })()
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.revision == 2
    assert new_state.campaign_settings is not None
    assert new_state.campaign_settings.difficulty == DIFFICULTY_EASY
    assert new_state.campaign_settings.tone == TONE_HEROIC


def test_apply_event_campaign_settings_updated_rejected_stale():
    state = create_initial_state("test")
    state.revision = 5
    event = type("FakeEvent", (), {
        "event_id": "evt_5_1",
        "type": "campaign_settings_updated",
        "revision_base": 3,
        "authorized": True,
        "payload": {"campaign_settings": {"campaign_settings_id": "cs", "world_id": "w1"}},
    })()
    new_state, success = apply_event(state, event)
    assert success is False
    assert new_state.revision == 5


def test_apply_event_campaign_settings_updated_rejected_unauthorized():
    state = create_initial_state("test")
    event = type("FakeEvent", (), {
        "event_id": "evt_1_1",
        "type": "campaign_settings_updated",
        "revision_base": 1,
        "authorized": False,
        "payload": {"campaign_settings": {"campaign_settings_id": "cs", "world_id": "w1"}},
    })()
    new_state, success = apply_event(state, event)
    assert success is False
    assert new_state.campaign_settings is None


# --- Custom Settings Tests ---

def test_campaign_settings_custom_extensibility():
    settings = CampaignSettings(
        campaign_settings_id="cs_custom1",
        world_id="w1",
        difficulty=DIFFICULTY_CUSTOM,
        custom_settings={
            "custom_difficulty_name": "Nightmare",
            "enemy_level_boost": 3,
            "weather_enabled": True,
            "day_night_cycle": "realistic",
        },
    )
    assert settings.is_valid() is True
    assert settings.custom_settings["custom_difficulty_name"] == "Nightmare"
    assert settings.custom_settings["enemy_level_boost"] == 3
    assert settings.custom_settings["weather_enabled"] is True


def test_campaign_settings_starting_conditions():
    settings = CampaignSettings(
        campaign_settings_id="cs_start1",
        world_id="w1",
        starting_conditions={
            "initial_gold": 200,
            "starting_items": ["healing_potion", "map", "torch"],
            "reputation": {"villagers": 10, "guards": -20},
            "level": 3,
            "health": 85,
        },
    )
    assert settings.starting_conditions["initial_gold"] == 200
    assert len(settings.starting_conditions["starting_items"]) == 3
    assert settings.starting_conditions["reputation"]["villagers"] == 10
