package com.sevenrpg.domain

/**
 * Character relationship — NPC or faction standing.
 */
data class CharacterRelationship(
    val targetId: String,
    val targetName: String,
    val relationshipType: String, // npc, faction, group
    val standing: Int = 0, // -100 to 100
    val trustLevel: Int = 0, // 0 to 100
    val knownFacts: List<String> = emptyList(),
    val rumors: List<String> = emptyList()
) {
    fun toMap(): Map<String, Any> = mapOf(
        "targetId" to targetId,
        "targetName" to targetName,
        "relationshipType" to relationshipType,
        "standing" to standing,
        "trustLevel" to trustLevel,
        "knownFacts" to knownFacts,
        "rumors" to rumors
    )

    companion object {
        fun fromMap(data: Map<String, Any>): CharacterRelationship = CharacterRelationship(
            targetId = data["targetId"] as String,
            targetName = data["targetName"] as String,
            relationshipType = data["relationshipType"] as String,
            standing = data["standing"] as? Int ?: 0,
            trustLevel = data["trustLevel"] as? Int ?: 0,
            knownFacts = data["knownFacts"] as? List<String> ?: emptyList(),
            rumors = data["rumors"] as? List<String> ?: emptyList()
        )
    }
}

/**
 * Relationship network — all character relationships.
 */
data class RelationshipNetwork(
    val relationships: Map<String, CharacterRelationship> = emptyMap()
) {
    fun getRelationship(targetId: String): CharacterRelationship? =
        relationships[targetId]

    fun addOrUpdate(relationship: CharacterRelationship): RelationshipNetwork =
        copy(relationships = relationships + (relationship.targetId to relationship))

    fun modifyStanding(targetId: String, change: Int): RelationshipNetwork {
        val current = relationships[targetId]?.standing ?: 0
        val newStanding = (current + change).coerceIn(-100, 100)
        val updated = relationships[targetId]?.copy(standing = newStanding) ?: CharacterRelationship(
            targetId = targetId,
            targetName = targetId,
            relationshipType = "unknown",
            standing = newStanding
        )
        return addOrUpdate(updated)
    }

    fun toMap(): Map<String, Any> = mapOf(
        "relationships" to relationships.mapValues { it.value.toMap() }
    )

    companion object {
        fun fromMap(data: Map<String, Any>): RelationshipNetwork = RelationshipNetwork(
            relationships = (data["relationships"] as? Map<*, *>)
                ?.mapValues { it.value as Map<String, Any> }
                ?.mapValues { CharacterRelationship.fromMap(it) }
                ?: emptyMap()
        )
    }
}