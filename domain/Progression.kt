package com.sevenrpg.domain

/**
 * Character progression — experience, levels, skill points.
 */
data class Progression(
    val experience: Int = 0,
    val level: Int = 1,
    val skillPoints: Int = 0,
    val attributePoints: Int = 0,
    val totalExperience: Int = 0
) {
    val experienceToNextLevel: Int get() = level * 1000 // 1000, 2000, 3000...

    fun addExperience(amount: Int): Progression {
        val newExp = experience + amount
        val newTotalExp = totalExperience + amount
        var newLevel = level
        var newSkillPoints = skillPoints
        var newAttributePoints = attributePoints
        var remainingExp = newExp

        while (remainingExp >= experienceToNextLevel) {
            remainingExp -= experienceToNextLevel
            newLevel++
            newSkillPoints += 1
            newAttributePoints += 1
        }

        return copy(
            experience = remainingExp,
            level = newLevel,
            skillPoints = newSkillPoints,
            attributePoints = newAttributePoints,
            totalExperience = newTotalExp
        )
    }

    fun spendSkillPoints(amount: Int): Progression =
        copy(skillPoints = skillPoints - amount.coerceIn(0, skillPoints))

    fun spendAttributePoints(amount: Int): Progression =
        copy(attributePoints = attributePoints - amount.coerceIn(0, attributePoints))

    fun toMap(): Map<String, Any> = mapOf(
        "experience" to experience,
        "level" to level,
        "skillPoints" to skillPoints,
        "attributePoints" to attributePoints,
        "totalExperience" to totalExperience
    )

    companion object {
        fun fromMap(data: Map<String, Any>): Progression = Progression(
            experience = data["experience"] as? Int ?: 0,
            level = data["level"] as? Int ?: 1,
            skillPoints = data["skillPoints"] as? Int ?: 0,
            attributePoints = data["attributePoints"] as? Int ?: 0,
            totalExperience = data["totalExperience"] as? Int ?: 0
        )
    }
}

/**
 * Skill — learned ability.
 */
data class Skill(
    val skillId: String,
    val name: String,
    val description: String,
    val skillType: String, // active, passive, ultimate
    val level: Int = 1,
    val maxLevel: Int = 10,
    val experience: Int = 0,
    val unlockLevel: Int = 1
) {
    fun toMap(): Map<String, Any> = mapOf(
        "skillId" to skillId,
        "name" to name,
        "description" to description,
        "skillType" to skillType,
        "level" to level,
        "maxLevel" to maxLevel,
        "experience" to experience,
        "unlockLevel" to unlockLevel
    )

    companion object {
        fun fromMap(data: Map<String, Any>): Skill = Skill(
            skillId = data["skillId"] as String,
            name = data["name"] as String,
            description = data["description"] as String,
            skillType = data["skillType"] as String,
            level = data["level"] as? Int ?: 1,
            maxLevel = data["maxLevel"] as? Int ?: 10,
            experience = data["experience"] as? Int ?: 0,
            unlockLevel = data["unlockLevel"] as? Int ?: 1
        )
    }
}

/**
 * Skill tree — all learned skills.
 */
data class SkillTree(
    val skills: Map<String, Skill> = emptyMap()
) {
    fun getSkill(skillId: String): Skill? = skills[skillId]

    fun learnSkill(skill: Skill): SkillTree =
        copy(skills = skills + (skill.skillId to skill))

    fun upgradeSkill(skillId: String): SkillTree {
        val current = skills[skillId] ?: return this
        if (current.level >= current.maxLevel) return this
        return copy(skills = skills + (skillId to current.copy(level = current.level + 1)))
    }

    fun toMap(): Map<String, Any> = mapOf(
        "skills" to skills.mapValues { it.value.toMap() }
    )

    companion object {
        fun fromMap(data: Map<String, Any>): SkillTree = SkillTree(
            skills = (data["skills"] as? Map<*, *>)
                ?.mapValues { it.value as Map<String, Any> }
                ?.mapValues { Skill.fromMap(it) }
                ?: emptyMap()
        )
    }
}