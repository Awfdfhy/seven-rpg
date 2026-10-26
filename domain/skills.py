# Seven RPG — Skill Check System (RPG-08-04)
# Directive: multi-agent-architect — deterministic dice mechanics, stack-agnostic domain logic.
# Integrates with character stats and combat.

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Dice utilities
# ---------------------------------------------------------------------------

def roll_die(sides: int) -> int:
    """Roll a single die with the given number of sides (1..sides)."""
    if sides < 1:
        raise ValueError(f"Die sides must be >= 1, got {sides}")
    return random.randint(1, sides)


def roll_d20() -> int:
    """Convenience wrapper: roll a 20-sided die."""
    return roll_die(20)


def roll_damage(num_dice: int = 1, die_sides: int = 6, modifier: int = 0) -> int:
    """
    Roll damage dice (e.g. 2d6+3).
    Returns the sum of all dice plus the flat modifier.
    """
    total = sum(roll_die(die_sides) for _ in range(num_dice))
    return total + modifier


# ---------------------------------------------------------------------------
# Skill definitions
# ---------------------------------------------------------------------------

# Canonical skill registry.  Each skill maps to the attribute key it uses
# for its modifier calculation.
SKILL_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "acrobatics":        {"attribute": "dexterity", "description": "Balance, tumbling, aerial maneuvers."},
    "arcana":            {"attribute": "intelligence", "description": "Knowledge of magic lore and traditions."},
    "athletics":         {"attribute": "strength", "description": "Climb, jump, swim, lift, and brute force."},
    "deception":         {"attribute": "charisma", "description": "Mislead with words or gestures."},
    "history":           {"attribute": "intelligence", "description": "Recall lore about events, people, and places."},
    "insight":           {"attribute": "wisdom", "description": "Discern intent from body language and speech."},
    "intimidation":      {"attribute": "charisma", "description": "Frighten others through threats or presence."},
    "investigation":     {"attribute": "intelligence", "description": "Find clues, deduce answers, follow tracks."},
    "medicine":          {"attribute": "wisdom", "description": "Diagnose illness, stabilize the dying, treat wounds."},
    "nature":            {"attribute": "intelligence", "description": "Recall lore about terrain, plants, animals, weather."},
    "perception":        {"attribute": "wisdom", "description": "Notice hidden objects, sounds, or details."},
    "performance":       {"attribute": "charisma", "description": "Delight an audience with music, dance, oratory."},
    "persuasion":        {"attribute": "charisma", "description": "Influence others with tact and social grace."},
    "sleight_of_hand":   {"attribute": "dexterity", "description": "Pick pockets, palm objects, hide items."},
    "stealth":           {"attribute": "dexterity", "description": "Hide, move quietly, avoid notice."},
    "survival":          {"attribute": "wisdom", "description": "Follow tracks, find food, avoid natural hazards."},
    # Combat-specific pseudo-skills
    "melee_attack":      {"attribute": "strength", "description": "Close-quarters weapon attack roll."},
    "ranged_attack":     {"attribute": "dexterity", "description": "Ranged weapon or projectile attack roll."},
    "spell_attack":      {"attribute": "intelligence", "description": "Magical attack roll (spellcasting modifier)."},
    "spell_save_dc":     {"attribute": "intelligence", "description": "Difficulty class for saving throws vs. your spells."},
    "initiative":        {"attribute": "dexterity", "description": "Reaction speed to determine turn order."},
}


# ---------------------------------------------------------------------------
# Domain entities
# ---------------------------------------------------------------------------

@dataclass
class SkillDefinition:
    """Typed wrapper around a skill definition."""
    name: str
    attribute: str
    description: str = ""

    @classmethod
    def from_registry(cls, name: str) -> "SkillDefinition":
        if name not in SKILL_DEFINITIONS:
            raise KeyError(f"Unknown skill: {name!r}. Valid skills: {sorted(SKILL_DEFINITIONS)}")
        defn = SKILL_DEFINITIONS[name]
        return cls(name=name, attribute=defn["attribute"], description=defn["description"])

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "attribute": self.attribute, "description": self.description}


@dataclass
class SkillCheck:
    """
    Represents a single skill check attempt.
    Does NOT perform the roll — `SkillCheckResult.perform()` does that,
    keeping the check itself serializable / deterministic-before-roll.
    """
    check_id: str
    skill_name: str
    modifier: int = 0
    difficulty_class: int = 10
    advantage: int = 0  # -1 disadvantage, 0 normal, +1 advantage
    player_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "skill_name": self.skill_name,
            "modifier": self.modifier,
            "difficulty_class": self.difficulty_class,
            "advantage": self.advantage,
            "player_id": self.player_id,
        }

    @classmethod
    def create(cls, skill_name: str, modifier: int = 0, difficulty_class: int = 10,
               advantage: int = 0, player_id: str = "") -> "SkillCheck":
        import uuid
        check_id = f"chk_{uuid.uuid4().hex[:8]}"
        return cls(
            check_id=check_id,
            skill_name=skill_name,
            modifier=modifier,
            difficulty_class=difficulty_class,
            advantage=advantage,
            player_id=player_id,
        )


@dataclass
class SkillCheckResult:
    """Outcome of a SkillCheck."""
    check: SkillCheck
    roll: int = 0
    secondary_roll: Optional[int] = None  # used when advantage/disadvantage
    total: int = 0
    success: bool = False
    natural_20: bool = False
    natural_1: bool = False
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check.to_dict(),
            "roll": self.roll,
            "secondary_roll": self.secondary_roll,
            "total": self.total,
            "success": self.success,
            "natural_20": self.natural_20,
            "natural_1": self.natural_1,
            "message": self.message,
        }

    @classmethod
    def perform(cls, check: SkillCheck) -> "SkillCheckResult":
        """
        Execute the skill check deterministically w.r.t. randomness.
        Natural 1 always fails; natural 20 always succeeds (critical).
        Advantage: roll 2d20, take higher.
        Disadvantage: roll 2d20, take lower.
        """
        primary = roll_d20()
        secondary: Optional[int] = None

        if check.advantage > 0:
            secondary = roll_d20()
            effective = max(primary, secondary)
        elif check.advantage < 0:
            secondary = roll_d20()
            effective = min(primary, secondary)
        else:
            effective = primary

        total = effective + check.modifier
        nat20 = primary == 20
        nat1 = primary == 1
        success = total >= check.difficulty_class

        # Critical success/failure overrides
        if nat20:
            success = True
            msg = f"Critical success! Natural 20 + {check.modifier} = {total} (DC {check.difficulty_class})"
        elif nat1:
            success = False
            msg = f"Critical failure! Natural 1 + {check.modifier} = {total} (DC {check.difficulty_class})"
        elif success:
            msg = f"Success! {effective} + {check.modifier} = {total} >= DC {check.difficulty_class}"
        else:
            msg = f"Failure. {effective} + {check.modifier} = {total} < DC {check.difficulty_class}"

        return cls(
            check=check,
            roll=primary,
            secondary_roll=secondary,
            total=total,
            success=success,
            natural_20=nat20,
            natural_1=nat1,
            message=msg,
        )


# ---------------------------------------------------------------------------
# Combat helpers
# ---------------------------------------------------------------------------

@dataclass
class CombatAttack:
    """
    Structured combat attack — resolved into a SkillCheck (attack roll)
    plus optional damage roll.
    """
    attack_id: str
    attacker_id: str
    target_id: str
    attack_type: str = "melee"  # melee | ranged | spell
    attack_bonus: int = 0
    damage_dice: int = 1
    damage_sides: int = 6
    damage_bonus: int = 0
    target_ac: int = 10
    target_save_dc: Optional[int] = None  # if set, target makes a save instead of AC

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_id": self.attack_id,
            "attacker_id": self.attacker_id,
            "target_id": self.target_id,
            "attack_type": self.attack_type,
            "attack_bonus": self.attack_bonus,
            "damage_dice": self.damage_dice,
            "damage_sides": self.damage_sides,
            "damage_bonus": self.damage_bonus,
            "target_ac": self.target_ac,
            "target_save_dc": self.target_save_dc,
        }

    @classmethod
    def create(cls, attacker_id: str, target_id: str, attack_type: str = "melee",
               attack_bonus: int = 0, damage_dice: int = 1, damage_sides: int = 6,
               damage_bonus: int = 0, target_ac: int = 10,
               target_save_dc: Optional[int] = None) -> "CombatAttack":
        import uuid
        attack_id = f"atk_{uuid.uuid4().hex[:8]}"
        return cls(
            attack_id=attack_id,
            attacker_id=attacker_id,
            target_id=target_id,
            attack_type=attack_type,
            attack_bonus=attack_bonus,
            damage_dice=damage_dice,
            damage_sides=damage_sides,
            damage_bonus=damage_bonus,
            target_ac=target_ac,
            target_save_dc=target_save_dc,
        )

    def resolve(self) -> Dict[str, Any]:
        """
        Resolve the attack into a structured dict.
        If target_save_dc is provided, the target makes a saving throw;
        otherwise the attacker makes an attack roll against target_ac.
        """
        if self.target_save_dc is not None:
            # Target makes a saving throw against the DC
            save_skill = "spell_save_dc" if self.attack_type == "spell" else "fortitude_save"
            # Default to wisdom save for spells
            if self.attack_type == "spell":
                save_skill = "spell_save_dc"
            else:
                save_skill = "fortitude_save"

            # We treat the save as a skill check where the target must roll UNDER the DC
            # Actually, in typical RPGs, the target rolls to MEET or EXCEED the DC.
            # For saves vs effects: target rolls and must meet/exceed the DC to SUCCEED (negate).
            # Let's treat it the same as a skill check for consistency.
            save_check = SkillCheck.create(
                skill_name=save_skill,
                modifier=0,  # will be set by caller
                difficulty_class=self.target_save_dc or 10,
                player_id=self.target_id,
            )
            return {
                "type": "saving_throw",
                "save_check": save_check.to_dict(),
                "damage": roll_damage(self.damage_dice, self.damage_sides, self.damage_bonus),
            }

        # Attack roll vs AC
        attack_skill = {
            "melee": "melee_attack",
            "ranged": "ranged_attack",
            "spell": "spell_attack",
        }.get(self.attack_type, "melee_attack")

        attack_check = SkillCheck.create(
            skill_name=attack_skill,
            modifier=self.attack_bonus,
            difficulty_class=self.target_ac,
            player_id=self.attacker_id,
        )
        result = SkillCheckResult.perform(attack_check)
        damage = roll_damage(self.damage_dice, self.damage_sides, self.damage_bonus) if result.success else 0

        return {
            "type": "attack_roll",
            "attack_result": result.to_dict(),
            "damage": damage,
            "hit": result.success,
        }


# ---------------------------------------------------------------------------
# Stat integration helpers
# ---------------------------------------------------------------------------

# Standard attribute-to-modifier mapping (D&D 5e-style: (score - 10) // 2)
ATTRIBUTE_MODIFIER_MAP: Dict[str, int] = {
    "strength": 0,
    "dexterity": 0,
    "constitution": 0,
    "intelligence": 0,
    "wisdom": 0,
    "charisma": 0,
}


def get_attribute_modifier(attributes: Dict[str, Any], attribute_name: str) -> int:
    """
    Convert an ability score to its modifier.
    Default modifier is 0 if the attribute is missing or invalid.
    Formula: (score - 10) // 2
    """
    score = attributes.get(attribute_name, 10)
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 10
    if score < 1:
        score = 1
    if score > 30:
        score = 30
    return (score - 10) // 2


def build_skill_modifier(attributes: Dict[str, Any], skill_name: str,
                         proficiency_bonus: int = 0) -> int:
    """
    Compute the total modifier for a skill check:
        ability_modifier + proficiency_bonus
    """
    if skill_name not in SKILL_DEFINITIONS:
        raise KeyError(f"Unknown skill: {skill_name!r}")
    attr = SKILL_DEFINITIONS[skill_name]["attribute"]
    ability_mod = get_attribute_modifier(attributes, attr)
    return ability_mod + proficiency_bonus


def build_skill_check_from_character(character_attributes: Dict[str, Any],
                                     skill_name: str,
                                     proficiency_bonus: int = 0,
                                     difficulty_class: int = 10,
                                     advantage: int = 0,
                                     player_id: str = "") -> SkillCheck:
    """
    Factory: build a fully-formed SkillCheck from character attributes.
    """
    modifier = build_skill_modifier(character_attributes, skill_name, proficiency_bonus)
    return SkillCheck.create(
        skill_name=skill_name,
        modifier=modifier,
        difficulty_class=difficulty_class,
        advantage=advantage,
        player_id=player_id,
    )
