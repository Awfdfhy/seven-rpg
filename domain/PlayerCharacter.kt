package com.sevenrpg.domain

/**
 * Player character entity — unique within a world.
 * Directive: multi-agent-architect — typed domain entities independent of UI/provider.
 */
data class PlayerCharacter(
    val playerId: String,
    val name: String,
    val identitySheet: Map<String, Any> = emptyMap(),
    val attributes: Map<String, Any> = emptyMap(),
    val version: Int = 1,
    val worldId: String = ""
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "playerId" to playerId,
            "name" to name,
            "identitySheet" to identitySheet,
            "attributes" to attributes,
            "version" to version,
            "worldId" to worldId
        )
    }

    companion object {
        fun fromMap(data: Map<String, Any>): PlayerCharacter {
            return PlayerCharacter(
                playerId = data["playerId"] as String,
                name = data["name"] as String,
                identitySheet = data["identitySheet"] as? Map<String, Any> ?: emptyMap(),
                attributes = data["attributes"] as? Map<String, Any> ?: emptyMap(),
                version = data["version"] as? Int ?: 1,
                worldId = data["worldId"] as? String ?: ""
            )
        }
    }
}