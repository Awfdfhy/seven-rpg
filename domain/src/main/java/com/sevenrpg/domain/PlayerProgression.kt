package com.sevenrpg.domain

/**
 * Complete player progression state — combines all progression systems.
 */
data class PlayerProgression(
    val attributes: Attributes = Attributes(),
    val skills: SkillTree = SkillTree(),
    val progression: Progression = Progression(),
    val inventory: Inventory = Inventory(),
    val quests: QuestLog = QuestLog(),
    val relationships: RelationshipNetwork = RelationshipNetwork(),
    val factions: FactionStandings = FactionStandings()
) {
    fun toMap(): Map<String, Any> = mapOf(
        "attributes" to attributes.toMap(),
        "skills" to skills.toMap(),
        "progression" to progression.toMap(),
        "inventory" to inventory.toMap(),
        "quests" to quests.toMap(),
        "relationships" to relationships.toMap(),
        "factions" to factions.toMap()
    )

    companion object {
        fun fromMap(data: Map<String, Any>): PlayerProgression = PlayerProgression(
            attributes = Attributes.fromMap(data["attributes"] as? Map<String, Any> ?: emptyMap()),
            skills = SkillTree.fromMap(data["skills"] as? Map<String, Any> ?: emptyMap()),
            progression = Progression.fromMap(data["progression"] as? Map<String, Any> ?: emptyMap()),
            inventory = Inventory.fromMap(data["inventory"] as? Map<String, Any> ?: emptyMap()),
            quests = QuestLog.fromMap(data["quests"] as? Map<String, Any> ?: emptyMap()),
            relationships = RelationshipNetwork.fromMap(data["relationships"] as? Map<String, Any> ?: emptyMap()),
            factions = FactionStandings.fromMap(data["factions"] as? Map<String, Any> ?: emptyMap())
        )
    }
}