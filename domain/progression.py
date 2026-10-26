# Seven RPG — Domain Progression (Stack-Agnostic)
# Directive: multi-agent-architect — typed progression models independent of UI/provider.

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Progression:
    """Character progression — experience, levels, skill points, attribute points."""
    experience: int = 0
    level: int = 1
    skill_points: int = 0
    attribute_points: int = 0
    total_experience: int = 0

    @property
    def experience_to_next_level(self) -> int:
        """Experience required to reach the next level."""
        return self.level * 1000  # 1000, 2000, 3000, ...

    def add_experience(self, amount: int) -> "Progression":
        """Add experience and handle automatic level ups."""
        if amount <= 0:
            return self

        new_exp = self.experience + amount
        new_total_exp = self.total_experience + amount
        new_level = self.level
        new_skill_points = self.skill_points
        new_attribute_points = self.attribute_points
        remaining_exp = new_exp

        # Process multiple level ups if enough experience
        while remaining_exp >= new_level * 1000:
            remaining_exp -= new_level * 1000
            new_level += 1
            new_skill_points += 1
            new_attribute_points += 1

        return Progression(
            experience=remaining_exp,
            level=new_level,
            skill_points=new_skill_points,
            attribute_points=new_attribute_points,
            total_experience=new_total_exp,
        )

    def spend_skill_points(self, amount: int) -> "Progression":
        """Spend skill points, clamped to available amount."""
        spend = max(0, min(amount, self.skill_points))
        return Progression(
            experience=self.experience,
            level=self.level,
            skill_points=self.skill_points - spend,
            attribute_points=self.attribute_points,
            total_experience=self.total_experience,
        )

    def spend_attribute_points(self, amount: int) -> "Progression":
        """Spend attribute points, clamped to available amount."""
        spend = max(0, min(amount, self.attribute_points))
        return Progression(
            experience=self.experience,
            level=self.level,
            skill_points=self.skill_points,
            attribute_points=self.attribute_points - spend,
            total_experience=self.total_experience,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experience": self.experience,
            "level": self.level,
            "skillPoints": self.skill_points,
            "attributePoints": self.attribute_points,
            "totalExperience": self.total_experience,
            "experienceToNextLevel": self.experience_to_next_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Progression":
        return cls(
            experience=data.get("experience", 0),
            level=data.get("level", 1),
            skill_points=data.get("skillPoints", 0),
            attribute_points=data.get("attributePoints", 0),
            total_experience=data.get("totalExperience", 0),
        )


@dataclass
class Skill:
    """Learned ability."""
    skill_id: str
    name: str
    description: str
    skill_type: str  # active, passive, ultimate
    level: int = 1
    max_level: int = 10
    experience: int = 0
    unlock_level: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skillId": self.skill_id,
            "name": self.name,
            "description": self.description,
            "skillType": self.skill_type,
            "level": self.level,
            "maxLevel": self.max_level,
            "experience": self.experience,
            "unlockLevel": self.unlock_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        return cls(
            skill_id=data["skillId"],
            name=data["name"],
            description=data.get("description", ""),
            skill_type=data.get("skillType", "active"),
            level=data.get("level", 1),
            max_level=data.get("maxLevel", 10),
            experience=data.get("experience", 0),
            unlock_level=data.get("unlockLevel", 1),
        )


@dataclass
class SkillTree:
    """All learned skills."""
    skills: Dict[str, Skill] = field(default_factory=dict)

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)

    def learn_skill(self, skill: Skill) -> "SkillTree":
        """Learn a new skill."""
        return SkillTree(skills={**self.skills, skill.skill_id: skill})

    def upgrade_skill(self, skill_id: str) -> "SkillTree":
        """Upgrade an existing skill by 1 level."""
        current = self.skills.get(skill_id)
        if current is None or current.level >= current.max_level:
            return self
        upgraded = Skill(
            skill_id=current.skill_id,
            name=current.name,
            description=current.description,
            skill_type=current.skill_type,
            level=current.level + 1,
            max_level=current.max_level,
            experience=current.experience,
            unlock_level=current.unlock_level,
        )
        return SkillTree(skills={**self.skills, skill_id: upgraded})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillTree":
        skills_data = data.get("skills", {})
        skills = {k: Skill.from_dict(v) for k, v in skills_data.items()}
        return cls(skills=skills)


@dataclass
class CharacterLevel:
    """Level up result — what changed when a character leveled up."""
    old_level: int
    new_level: int
    skill_points_gained: int
    attribute_points_gained: int
    unlocked_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "oldLevel": self.old_level,
            "newLevel": self.new_level,
            "skillPointsGained": self.skill_points_gained,
            "attributePointsGained": self.attribute_points_gained,
            "unlockedSkills": self.unlocked_skills,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterLevel":
        return cls(
            old_level=data.get("oldLevel", 1),
            new_level=data.get("newLevel", 1),
            skill_points_gained=data.get("skillPointsGained", 0),
            attribute_points_gained=data.get("attributePointsGained", 0),
            unlocked_skills=data.get("unlockedSkills", []),
        )
