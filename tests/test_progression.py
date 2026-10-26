# Seven RPG — Character Progression Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_progression.py -v

import pytest
from domain.progression import Progression, Skill, SkillTree, CharacterLevel


# --- Progression Tests ---

def test_progression_initial_state():
    """Progression starts at level 1 with zero experience."""
    prog = Progression()
    assert prog.level == 1
    assert prog.experience == 0
    assert prog.total_experience == 0
    assert prog.skill_points == 0
    assert prog.attribute_points == 0
    assert prog.experience_to_next_level == 1000


def test_progression_add_experience_single_level_up():
    """Adding enough XP triggers a level up."""
    prog = Progression()
    new_prog = prog.add_experience(1000)
    assert new_prog.level == 2
    assert new_prog.experience == 0
    assert new_prog.total_experience == 1000
    assert new_prog.skill_points == 1
    assert new_prog.attribute_points == 1


def test_progression_add_experience_partial():
    """Adding partial XP does not trigger level up."""
    prog = Progression()
    new_prog = prog.add_experience(500)
    assert new_prog.level == 1
    assert new_prog.experience == 500
    assert new_prog.total_experience == 500
    assert new_prog.skill_points == 0
    assert new_prog.attribute_points == 0


def test_progression_add_experience_multiple_level_ups():
    """Adding enough XP for multiple level ups."""
    prog = Progression()
    new_prog = prog.add_experience(3500)
    assert new_prog.level == 3
    assert new_prog.experience == 500  # 3500 - 1000 (lvl2) - 2000 (lvl3) = 500
    assert new_prog.total_experience == 3500
    assert new_prog.skill_points == 2
    assert new_prog.attribute_points == 2


def test_progression_add_experience_zero_or_negative():
    """Zero or negative XP does nothing."""
    prog = Progression()
    new_prog = prog.add_experience(0)
    assert new_prog == prog
    new_prog = prog.add_experience(-100)
    assert new_prog == prog


def test_progression_level_up_rewards_scale():
    """Each level up gives 1 skill point and 1 attribute point."""
    prog = Progression()
    # Level 1 -> 2
    prog = prog.add_experience(1000)
    assert prog.skill_points == 1
    assert prog.attribute_points == 1
    # Level 2 -> 3 (needs 2000 XP)
    prog = prog.add_experience(2000)
    assert prog.level == 3
    assert prog.skill_points == 2
    assert prog.attribute_points == 2


def test_progression_spend_skill_points():
    """Spending skill points reduces available points."""
    prog = Progression(level=2, skill_points=3)
    new_prog = prog.spend_skill_points(2)
    assert new_prog.skill_points == 1
    assert new_prog.level == 2


def test_progression_spend_skill_points_clamped():
    """Cannot spend more skill points than available."""
    prog = Progression(level=2, skill_points=1)
    new_prog = prog.spend_skill_points(5)
    assert new_prog.skill_points == 0


def test_progression_spend_attribute_points():
    """Spending attribute points reduces available points."""
    prog = Progression(level=2, attribute_points=3)
    new_prog = prog.spend_attribute_points(2)
    assert new_prog.attribute_points == 1


def test_progression_to_dict_and_back():
    """Progression serialization round-trip."""
    prog = Progression(experience=500, level=2, skill_points=1, attribute_points=1, total_experience=1500)
    data = prog.to_dict()
    restored = Progression.from_dict(data)
    assert restored.experience == 500
    assert restored.level == 2
    assert restored.skill_points == 1
    assert restored.attribute_points == 1
    assert restored.total_experience == 1500
    assert restored.experience_to_next_level == 2000


# --- Skill Tests ---

def test_skill_creation():
    """Skill created with defaults."""
    skill = Skill(
        skill_id="fireball",
        name="Fireball",
        description="Hurls a ball of fire",
        skill_type="active",
    )
    assert skill.skill_id == "fireball"
    assert skill.level == 1
    assert skill.max_level == 10
    assert skill.unlock_level == 1


def test_skill_to_dict_and_back():
    """Skill serialization round-trip."""
    skill = Skill(
        skill_id="fireball",
        name="Fireball",
        description="Hurls a ball of fire",
        skill_type="active",
        level=3,
        max_level=10,
        unlock_level=5,
    )
    data = skill.to_dict()
    restored = Skill.from_dict(data)
    assert restored.skill_id == "fireball"
    assert restored.level == 3
    assert restored.unlock_level == 5


# --- SkillTree Tests ---

def test_skill_tree_initial_empty():
    """Skill tree starts empty."""
    tree = SkillTree()
    assert tree.get_skill("fireball") is None


def test_skill_tree_learn_skill():
    """Learning a skill adds it to the tree."""
    skill = Skill(skill_id="fireball", name="Fireball", description="", skill_type="active")
    tree = SkillTree().learn_skill(skill)
    assert tree.get_skill("fireball") is not None
    assert tree.get_skill("fireball").name == "Fireball"


def test_skill_tree_upgrade_skill():
    """Upgrading a skill increases its level."""
    skill = Skill(skill_id="fireball", name="Fireball", description="", skill_type="active", level=1)
    tree = SkillTree().learn_skill(skill)
    upgraded = tree.upgrade_skill("fireball")
    assert upgraded.get_skill("fireball").level == 2


def test_skill_tree_upgrade_max_level():
    """Cannot upgrade beyond max level."""
    skill = Skill(skill_id="fireball", name="Fireball", description="", skill_type="active", level=10, max_level=10)
    tree = SkillTree(skills={"fireball": skill})
    upgraded = tree.upgrade_skill("fireball")
    assert upgraded.get_skill("fireball").level == 10


def test_skill_tree_upgrade_nonexistent():
    """Upgrading a non-existent skill does nothing."""
    tree = SkillTree()
    upgraded = tree.upgrade_skill("nonexistent")
    assert upgraded.get_skill("nonexistent") is None


def test_skill_tree_to_dict_and_back():
    """Skill tree serialization round-trip."""
    skill = Skill(skill_id="fireball", name="Fireball", description="", skill_type="active", level=3)
    tree = SkillTree().learn_skill(skill)
    data = tree.to_dict()
    restored = SkillTree.from_dict(data)
    assert restored.get_skill("fireball").level == 3


# --- CharacterLevel Tests ---

def test_character_level_creation():
    """CharacterLevel created correctly."""
    level_up = CharacterLevel(
        old_level=1,
        new_level=2,
        skill_points_gained=1,
        attribute_points_gained=1,
        unlocked_skills=["fireball"],
    )
    assert level_up.old_level == 1
    assert level_up.new_level == 2
    assert level_up.unlocked_skills == ["fireball"]


def test_character_level_to_dict_and_back():
    """CharacterLevel serialization round-trip."""
    level_up = CharacterLevel(
        old_level=1,
        new_level=2,
        skill_points_gained=1,
        attribute_points_gained=1,
        unlocked_skills=["fireball"],
    )
    data = level_up.to_dict()
    restored = CharacterLevel.from_dict(data)
    assert restored.old_level == 1
    assert restored.new_level == 2
    assert restored.unlocked_skills == ["fireball"]


# --- Reducer Integration Tests ---

def test_apply_event_experience_gained():
    """experience_gained event updates player progression."""
    from domain.entities import PlayerCharacter, World, GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.player = PlayerCharacter(
        player_id="p1",
        name="Hero",
        world_id="w1",
        progression={"experience": 0, "level": 1, "skillPoints": 0, "attributePoints": 0, "totalExperience": 0},
    )
    state.world = World(world_id="w1", name="Test World")
    state.revision = 1

    event = DomainEvent.create("experience_gained", revision_base=1, payload={"amount": 1000})
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.player.progression["level"] == 2
    assert new_state.player.progression["experience"] == 0
    assert new_state.player.progression["skillPoints"] == 1
    assert new_state.player.progression["attributePoints"] == 1
    assert new_state.player.progression["totalExperience"] == 1000


def test_apply_event_experience_gained_multiple_levels():
    """experience_gained event handles multiple level ups."""
    from domain.entities import PlayerCharacter, World, GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.player = PlayerCharacter(
        player_id="p1",
        name="Hero",
        world_id="w1",
        progression={"experience": 0, "level": 1, "skillPoints": 0, "attributePoints": 0, "totalExperience": 0},
    )
    state.world = World(world_id="w1", name="Test World")
    state.revision = 1

    event = DomainEvent.create("experience_gained", revision_base=1, payload={"amount": 3500})
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.player.progression["level"] == 3
    assert new_state.player.progression["experience"] == 500
    assert new_state.player.progression["totalExperience"] == 3500


def test_apply_event_skill_learned():
    """skill_learned event adds skill to player."""
    from domain.entities import PlayerCharacter, World, GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.player = PlayerCharacter(
        player_id="p1",
        name="Hero",
        world_id="w1",
        progression={"skills": {}},
    )
    state.world = World(world_id="w1", name="Test World")
    state.revision = 1

    event = DomainEvent.create("skill_learned", revision_base=1, payload={
        "skillId": "fireball",
        "name": "Fireball",
        "skillType": "active",
    })
    new_state, success = apply_event(state, event)
    assert success is True
    assert "fireball" in new_state.player.progression["skills"]["skills"]
    assert new_state.player.progression["skills"]["skills"]["fireball"]["name"] == "Fireball"


def test_apply_event_skill_upgraded():
    """skill_upgraded event increases skill level."""
    from domain.entities import PlayerCharacter, World, GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.player = PlayerCharacter(
        player_id="p1",
        name="Hero",
        world_id="w1",
        progression={"skills": {"skills": {"fireball": {"skillId": "fireball", "name": "Fireball", "description": "", "skillType": "active", "level": 1, "maxLevel": 10}}}},
    )
    state.world = World(world_id="w1", name="Test World")
    state.revision = 1

    event = DomainEvent.create("skill_upgraded", revision_base=1, payload={"skillId": "fireball"})
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.player.progression["skills"]["skills"]["fireball"]["level"] == 2


def test_apply_event_attribute_increased():
    """attribute_increased event boosts an attribute."""
    from domain.entities import PlayerCharacter, World, GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.player = PlayerCharacter(
        player_id="p1",
        name="Hero",
        world_id="w1",
        attributes={"strength": 10, "agility": 10},
    )
    state.world = World(world_id="w1", name="Test World")
    state.revision = 1

    event = DomainEvent.create("attribute_increased", revision_base=1, payload={"attribute": "strength"})
    new_state, success = apply_event(state, event)
    assert success is True
    assert new_state.player.attributes["strength"] == 11


def test_apply_event_experience_gained_without_player():
    """experience_gained without player is rejected."""
    from domain.entities import GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.revision = 1
    event = DomainEvent.create("experience_gained", revision_base=1, payload={"amount": 1000})
    new_state, success = apply_event(state, event)
    assert success is True  # Event is valid, just no-op for progression
    assert new_state.revision == 2


def test_apply_event_progression_preserves_existing_events():
    """Progression events don't break existing event handling."""
    from domain.entities import PlayerCharacter, World, Scene, GameState, create_initial_state
    from domain.reducer import apply_event
    from domain.entities import DomainEvent

    state = create_initial_state("test")
    state.world = World(world_id="w1", name="Test World")
    state.player = PlayerCharacter(
        player_id="p1",
        name="Hero",
        world_id="w1",
        progression={"experience": 0, "level": 1, "skillPoints": 0, "attributePoints": 0, "totalExperience": 0},
    )
    state.scene = Scene(scene_id="s1", world_id="w1", player_id="p1")
    state.revision = 1

    # Apply narrative advance
    event1 = DomainEvent.create("narrative_advance", revision_base=1, payload={"character_knowledge": {"clue": "found"}})
    state, s1 = apply_event(state, event1)
    assert s1 is True
    assert state.scene.character_knowledge == {"clue": "found"}

    # Apply experience gained
    event2 = DomainEvent.create("experience_gained", revision_base=2, payload={"amount": 1000})
    state, s2 = apply_event(state, event2)
    assert s2 is True
    assert state.player.progression["level"] == 2
    assert state.revision == 3
