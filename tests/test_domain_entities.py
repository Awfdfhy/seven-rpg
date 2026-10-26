# Seven RPG — Domain Entity Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_domain_entities.py -v

import pytest
from domain.entities import World, PlayerCharacter, Scene, DomainEvent, GameState
from domain.commands import PlayerCommand
from domain.contracts import ValidationResult, Proposal, AIProviderInterface
from domain.reducer import validate_command, validate_proposal, apply_event, create_initial_state


# --- World Tests ---

def test_world_creation():
    """World entity created with correct defaults."""
    world = World(world_id="w1", name="Test World")
    assert world.world_id == "w1"
    assert world.name == "Test World"
    assert world.version == 1
    assert world.isolated is True
    assert world.canon_facts == {}


def test_world_to_dict_and_back():
    """World serialization round-trip."""
    world = World(world_id="w1", name="Test World", canon_facts={"magic": True})
    data = world.to_dict()
    restored = World.from_dict(data)
    assert restored.world_id == world.world_id
    assert restored.name == world.name
    assert restored.canon_facts == world.canon_facts
    assert restored.version == world.version


# --- PlayerCharacter Tests ---

def test_player_creation():
    """Player character entity created with correct defaults."""
    player = PlayerCharacter(player_id="p1", name="Hero", world_id="w1")
    assert player.player_id == "p1"
    assert player.name == "Hero"
    assert player.world_id == "w1"
    assert player.version == 1


def test_player_to_dict_and_back():
    """Player serialization round-trip."""
    player = PlayerCharacter(player_id="p1", name="Hero", world_id="w1", attributes={"strength": 10})
    data = player.to_dict()
    restored = PlayerCharacter.from_dict(data)
    assert restored.attributes == {"strength": 10}


# --- Scene Tests ---

def test_scene_creation():
    """Scene entity created with correct defaults."""
    scene = Scene(scene_id="s1", world_id="w1", player_id="p1")
    assert scene.scene_id == "s1"
    assert scene.world_id == "w1"
    assert scene.player_id == "p1"
    assert scene.canon_facts_loaded is True


# --- DomainEvent Tests ---

def test_event_creation():
    """Domain event created with unique ID."""
    event = DomainEvent.create("narrative_advance", revision_base=1, payload={"text": "hello"})
    assert event.type == "narrative_advance"
    assert event.revision_base == 1
    assert event.authorized is True
    assert event.event_id.startswith("evt_1_")
    assert len(event.event_id.split("_")) >= 3


def test_event_to_dict_and_back():
    """Event serialization round-trip."""
    event = DomainEvent.create("test", revision_base=1, payload={"key": "val"})
    data = event.to_dict()
    restored = DomainEvent.from_dict(data)
    assert restored.event_id == event.event_id
    assert restored.type == event.type


# --- GameState Tests ---

def test_game_state_creation():
    """Game state created with correct defaults."""
    state = create_initial_state("test goal")
    assert state.revision == 1
    assert state.world is None
    assert state.player is None
    assert state.events == []
    assert state.canon_facts == {}


def test_game_state_to_dict_and_back():
    """Game state serialization round-trip."""
    state = create_initial_state("test")
    state.world = World(world_id="w1", name="Test")
    state.player = PlayerCharacter(player_id="p1", name="Hero", world_id="w1")
    data = state.to_dict()
    restored = GameState.from_dict(data)
    assert restored.world.name == "Test"
    assert restored.player.name == "Hero"
    assert restored.revision == state.revision


# --- PlayerCommand Tests ---

def test_command_creation():
    """Player command created with unique ID."""
    cmd = PlayerCommand.create("p1", "s1", "explore forest", revision_base=1)
    assert cmd.action == "explore forest"
    assert cmd.player_id == "p1"
    assert cmd.revision_base == 1
    assert cmd.command_id.startswith("cmd_1_")


# --- Validation Tests ---

def test_validate_command_stale_revision():
    """Stale command revision → invalid."""
    state = create_initial_state("test")
    state.revision = 5
    cmd = PlayerCommand.create("p1", "s1", "action", revision_base=3)
    result = validate_command(cmd, state)
    assert result.is_valid is False
    assert "stale" in result.errors[0]


def test_validate_command_unauthorized_player():
    """Wrong player → invalid."""
    state = create_initial_state("test")
    state.player = PlayerCharacter(player_id="p1", name="Hero", world_id="w1")
    cmd = PlayerCommand.create("p2", "s1", "action", revision_base=1)
    result = validate_command(cmd, state)
    assert result.is_valid is False
    assert "not authorized" in result.errors[0]


def test_validate_command_empty_action():
    """Empty action → invalid."""
    state = create_initial_state("test")
    state.player = PlayerCharacter(player_id="p1", name="Hero", world_id="w1")
    cmd = PlayerCommand.create("p1", "s1", "  ", revision_base=1)
    result = validate_command(cmd, state)
    assert result.is_valid is False
    assert "empty" in result.errors[0]


def test_validate_command_valid():
    """Valid command → valid."""
    state = create_initial_state("test")
    state.revision = 1
    state.player = PlayerCharacter(player_id="p1", name="Hero", world_id="w1")
    cmd = PlayerCommand.create("p1", "s1", "explore", revision_base=1)
    result = validate_command(cmd, state)
    assert result.is_valid is True
    assert result.errors == []


# --- Proposal Validation Tests ---

def test_validate_proposal_unauthorized_mutation():
    """Unauthorized mutation → invalid."""
    state = create_initial_state("test")
    state.revision = 1
    proposal = {"attempts_unauthorized_mutation": True, "events": [], "revision_base": 1}
    result = validate_proposal(proposal, state)
    assert result.is_valid is False
    assert "unauthorized" in result.errors[0]


def test_validate_proposal_stale_revision():
    """Stale proposal revision → invalid."""
    state = create_initial_state("test")
    state.revision = 5
    proposal = {"revision_base": 3, "events": [], "attempts_unauthorized_mutation": False}
    result = validate_proposal(proposal, state)
    assert result.is_valid is False
    assert "stale" in result.errors[0]


def test_validate_proposal_duplicate_event_ids():
    """Duplicate event IDs → invalid."""
    state = create_initial_state("test")
    state.revision = 1
    proposal = {
        "revision_base": 1,
        "events": [
            {"id": "evt_1", "type": "test"},
            {"id": "evt_1", "type": "test2"},
        ],
        "attempts_unauthorized_mutation": False,
    }
    result = validate_proposal(proposal, state)
    assert result.is_valid is False
    assert "duplicate" in result.errors[0]


def test_validate_proposal_valid():
    """Valid proposal → valid."""
    state = create_initial_state("test")
    state.revision = 1
    proposal = {
        "revision_base": 1,
        "events": [{"id": "evt_1", "type": "narrative_advance", "authorized": True}],
        "attempts_unauthorized_mutation": False,
    }
    result = validate_proposal(proposal, state)
    assert result.is_valid is True


# --- Reducer Tests ---

def test_apply_event_valid():
    """Valid event applied → new state with incremented revision."""
    state = create_initial_state("test")
    event = DomainEvent.create("narrative_advance", revision_base=1, payload={"text": "hello"})
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.revision == 2
    assert len(new_state.events) == 1
    assert new_state.events[0].event_id == event.event_id


def test_apply_event_unauthorized():
    """Unauthorized event → rejected, state unchanged."""
    state = create_initial_state("test")
    event = DomainEvent.create("test", revision_base=1, authorized=False)
    new_state, success = apply_event(state, event)
    assert success is False
    assert new_state.revision == state.revision
    assert len(new_state.events) == 0


def test_apply_event_stale_revision():
    """Stale event revision → rejected."""
    state = create_initial_state("test")
    state.revision = 5
    event = DomainEvent.create("test", revision_base=3)
    new_state, success = apply_event(state, event)
    assert success is False
    assert new_state.revision == 5


def test_apply_event_idempotent():
    """Duplicate event ID → idempotent, rejected."""
    state = create_initial_state("test")
    event = DomainEvent.create("test", revision_base=1)
    new_state, success = apply_event(state, event)
    assert success is True
    # Apply same event again
    new_state2, success2 = apply_event(new_state, event)
    assert success2 is False
    assert new_state2.revision == new_state.revision


def test_apply_event_narrative_advance():
    """Narrative advance event updates scene knowledge."""
    state = create_initial_state("test")
    state.scene = Scene(scene_id="s1", world_id="w1", player_id="p1")
    event = DomainEvent.create(
        "narrative_advance",
        revision_base=1,
        payload={"character_knowledge": {"clue": "found"}},
    )
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.scene.character_knowledge == {"clue": "found"}


# --- Proposal Dataclass Tests ---

def test_proposal_creation():
    """Proposal dataclass created correctly."""
    proposal = Proposal(
        type="narrative_response",
        prose="You enter the forest.",
        revision_base=1,
    )
    assert proposal.type == "narrative_response"
    assert proposal.prose == "You enter the forest."
    assert proposal.attempts_unauthorized_mutation is False
    assert proposal.revision_base == 1


def test_proposal_to_dict():
    """Proposal serialization."""
    proposal = Proposal(type="test", prose="hello", revision_base=1)
    data = proposal.to_dict()
    assert data["type"] == "test"
    assert data["prose"] == "hello"
    assert data["revision_base"] == 1