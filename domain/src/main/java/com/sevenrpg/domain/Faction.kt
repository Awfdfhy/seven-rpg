package com.sevenrpg.domain

/**
 * Faction — organized group with standing and reputation.
 */
data class Faction(
    val factionId: String,
    val name: String,
    val description: String,
    val standing: Int = 0, // -100 to 100
    val isHostile: Boolean = false,
    val isAlly: Boolean = false,
    val territories: List<String> = emptyList()
) {
    fun toMap(): Map<String, Any> = mapOf(
        "factionId" to factionId,
        "name" to name,
        "description" to description,
        "standing" to standing,
        "isHostile" to isHostile,
        "isAlly" to isAlly,
        "territories" to territories
    )

    companion object {
        fun fromMap(data: Map<String, Any>): Faction = Faction(
            factionId = data["factionId"] as String,
            name = data["name"] as String,
            description = data["description"] as String,
            standing = data["standing"] as? Int ?: 0,
            isHostile = data["isHostile"] as? Boolean ?: false,
            isAlly = data["isAlly"] as? Boolean ?: false,
            territories = data["territories"] as? List<String> ?: emptyList()
        )
    }
}

/**
 * Faction standings — all faction relationships.
 */
data class FactionStandings(
    val factions: Map<String, Faction> = emptyMap()
) {
    fun getFaction(factionId: String): Faction? = factions[factionId]

    fun modifyStanding(factionId: String, change: Int): FactionStandings {
        val current = factions[factionId]?.standing ?: 0
        val newStanding = (current + change).coerceIn(-100, 100)
        val updated = factions[factionId]?.copy(standing = newStanding) ?: Faction(
            factionId = factionId,
            name = factionId,
            description = "",
            standing = newStanding
        )
        return copy(factions = factions + (factionId to updated))
    }

    fun getHostileFactions(): List<Faction> = factions.values.filter { it.isHostile }.toList()
    fun getAllyFactions(): List<Faction> = factions.values.filter { it.isAlly }.toList()

    fun toMap(): Map<String, Any> = mapOf(
        "factions" to factions.mapValues { it.value.toMap() }
    )

    companion object {
        fun fromMap(data: Map<String, Any>): FactionStandings = FactionStandings(
            factions = (data["factions"] as? Map<*, *>)
                ?.mapValues { it.value as Map<String, Any> }
                ?.mapValues { Faction.fromMap(it) }
                ?: emptyMap()
        )
    }
}