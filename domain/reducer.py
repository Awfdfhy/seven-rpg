# Seven RPG — Domain Reducer (Stack-Agnostic)
# Directive: multi-agent-architect — deterministic reducer, invalid events rejected without mutation.
# Pure function: same state + same event → same result every time.

from typing import Any, Dict, List, Tuple
from domain.entities import GameState, DomainEvent, World, PlayerCharacter, Scene
from domain.commands import PlayerCommand
from domain.contracts import ValidationResult
from domain.progression import Progression, Skill, SkillTree


def validate_command(command: PlayerCommand, state: GameState) -> ValidationResult:
    """
    Validate a player command against current state, rules, and permissions.
    Rules:
      1. command.revision_base == state.revision — else stale
      2. command.player_id matches state.player.player_id — else unauthorized
      3. Action text must not be empty
      4. Resources sufficient (placeholder for MVP-0)
    """
    errors: List[str] = []

    if command.revision_base != state.revision:
        errors.append(f"stale command: revision_base {command.revision_base} != current {state.revision}")

    if state.player and command.player_id != state.player.player_id:
        errors.append("player not authorized for this scene")

    if not command.action or not command.action.strip():
        errors.append("action text cannot be empty")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )


def validate_proposal(proposal: dict, state: GameState) -> ValidationResult:
    """
    Validate an AI proposal against current state, rules, permissions.
    Invalid proposals rejected without mutation.
    """
    errors: List[str] = []

    if not isinstance(proposal, dict):
        errors.append("proposal is not a typed object")
        return ValidationResult(is_valid=False, errors=errors)

    if proposal.get("attempts_unauthorized_mutation"):
        errors.append("proposal attempts unauthorized state mutation")

    if proposal.get("revision_base") != state.revision:
        errors.append(
            f"stale proposal: revision_base {proposal.get('revision_base')} != current {state.revision}"
        )

    # Check for duplicate event IDs
    events = proposal.get("events", [])
    seen_ids = set()
    for event in events:
        eid = event.get("id")
        if eid in seen_ids:
            errors.append(f"duplicate event ID: {eid}")
        seen_ids.add(eid)

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )


def apply_event(state: GameState, event: DomainEvent) -> Tuple[GameState, bool]:
    """
    Deterministic reducer — apply an event to state.
    Returns (new_state, success). Invalid events rejected without mutation.
    """
    # Validate event authorization
    if not event.authorized:
        return state, False

    # Validate revision base (optimistic concurrency)
    if event.revision_base != state.revision:
        return state, False

    # Check for duplicate event ID (idempotency)
    for existing in state.events:
        if existing.event_id == event.event_id:
            return state, False  # Idempotent — already applied

    # Create new state (immutable update pattern)
    import copy
    new_state = copy.deepcopy(state)
    new_state.events.append(event)
    new_state.revision += 1
    new_state.confirmed_event_log.append(event)

    # Apply event type-specific logic
    if event.type == "narrative_advance":
        # Narrative advance — update scene knowledge from payload
        payload = event.payload or {}
        if new_state.scene:
            new_state.scene.character_knowledge.update(payload.get("character_knowledge", {}))
        new_state.canon_facts.update(payload.get("canon_facts", {}))

    elif event.type == "attribute_change":
        payload = event.payload or {}
        if new_state.player:
            new_state.player.attributes.update(payload.get("attributes", {}))

    elif event.type == "inventory_add":
        payload = event.payload or {}
        # Inventory logic would go here (post-MVP-0)
        pass

    elif event.type == "world_created":
        payload = event.payload or {}
        if new_state.world:
            new_state.world.canon_facts.update(payload.get("canon_facts", {}))

    elif event.type == "campaign_settings_updated":
        payload = event.payload or {}
        from domain.campaign_settings import CampaignSettings
        settings_data = payload.get("campaign_settings")
        if settings_data:
            new_state.campaign_settings = CampaignSettings.from_dict(settings_data)

    elif event.type == "skill_check":
        payload = event.payload or {}
        new_state.combat_log.append({
            "type": "skill_check",
            "result": payload.get("result"),
            "timestamp": event.timestamp,
        })

    elif event.type == "combat_attack":
        payload = event.payload or {}
        new_state.combat_log.append({
            "type": "combat_attack",
            "attacker_id": payload.get("attacker_id"),
            "target_id": payload.get("target_id"),
            "hit": payload.get("hit", False),
            "damage": payload.get("damage", 0),
            "timestamp": event.timestamp,
        })
        # Update active_combat if present
        if payload.get("combat_id"):
            combat = new_state.active_combat.get(payload["combat_id"], {})
            combat.setdefault("participants", set()).add(payload.get("attacker_id"))
            combat.setdefault("participants", set()).add(payload.get("target_id"))
            combat["last_action"] = event.timestamp
            new_state.active_combat[payload["combat_id"]] = combat

    elif event.type == "combat_start":
        payload = event.payload or {}
        combat_id = payload.get("combat_id", "")
        if combat_id:
            new_state.active_combat[combat_id] = {
                "participants": list(payload.get("participants", [])),
                "started_at": event.timestamp,
                "round": 1,
            }

    elif event.type == "combat_end":
        payload = event.payload or {}
        combat_id = payload.get("combat_id", "")
        if combat_id and combat_id in new_state.active_combat:
            del new_state.active_combat[combat_id]

    elif event.type == "skill_cooldown_set":
        payload = event.payload or {}
        skill = payload.get("skill_name", "")
        cooldown = payload.get("cooldown", 0)
        if skill:
            new_state.skill_cooldowns[skill] = cooldown

    elif event.type == "skill_cooldown_clear":
        payload = event.payload or {}
        skill = payload.get("skill_name", "")
        if skill and skill in new_state.skill_cooldowns:
            del new_state.skill_cooldowns[skill]

    # --- RPG-08-02: Character progression events ---
    elif event.type == "experience_gained":
        payload = event.payload or {}
        amount = payload.get("amount", 0)
        if new_state.player and amount > 0:
            current = _get_progression(new_state)
            new_progression = current.add_experience(amount)
            new_state = _set_progression(new_state, new_progression)

    elif event.type == "skill_learned":
        payload = event.payload or {}
        skill_id = payload.get("skillId")
        name = payload.get("name", skill_id)
        skill_type = payload.get("skillType", "active")
        if new_state.player and skill_id:
            current_tree = SkillTree.from_dict(new_state.player.progression.get("skills", {}))
            skill = Skill(skill_id=skill_id, name=name, description="", skill_type=skill_type)
            new_tree = current_tree.learn_skill(skill)
            prog_dict = dict(new_state.player.progression)
            prog_dict["skills"] = new_tree.to_dict()
            new_state.player.progression = prog_dict

    elif event.type == "skill_upgraded":
        payload = event.payload or {}
        skill_id = payload.get("skillId")
        if new_state.player and skill_id:
            current_tree = SkillTree.from_dict(new_state.player.progression.get("skills", {}))
            new_tree = current_tree.upgrade_skill(skill_id)
            prog_dict = dict(new_state.player.progression)
            prog_dict["skills"] = new_tree.to_dict()
            new_state.player.progression = prog_dict

    elif event.type == "attribute_increased":
        payload = event.payload or {}
        attribute = payload.get("attribute")
        if new_state.player and attribute:
            current = new_state.player.attributes
            new_attrs = dict(current)
            new_attrs[attribute] = new_attrs.get(attribute, 10) + 1
            new_state.player.attributes = new_attrs

    return new_state, True


def create_initial_state(user_goal: str) -> GameState:
    """Create initial empty game state for a new session."""
    return GameState(
        revision=1,
        events=[],
        confirmed_event_log=[],
    )


def _get_progression(state: GameState) -> Progression:
    """Extract Progression from state.player.progression dict."""
    if state.player and state.player.progression:
        return Progression.from_dict(state.player.progression)
    return Progression()


def _set_progression(state: GameState, progression: Progression) -> GameState:
    """Return a new state with progression dict updated on player."""
    import copy
    new_state = copy.deepcopy(state)
    if new_state.player:
        new_state.player.progression = progression.to_dict()
    return new_state