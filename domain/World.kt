package com.sevenrpg.domain

import java.time.Instant

/**
 * Versioned world entity — isolated per campaign.
 * Directive: multi-agent-architect — typed domain entities independent of UI/provider.
 */
data class World(
    val worldId: String,
    val name: String,
    val canonFacts: Map<String, Any> = emptyMap(),
    val version: Int = 1,
    val isolated: Boolean = true,
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now()
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "worldId" to worldId,
            "name" to name,
            "canonFacts" to canonFacts,
            "version" to version,
            "isolated" to isolated,
            "createdAt" to createdAt.toString(),
            "updatedAt" to updatedAt.toString()
        )
    }

    companion object {
        fun fromMap(data: Map<String, Any>): World {
            return World(
                worldId = data["worldId"] as String,
                name = data["name"] as String,
                canonFacts = data["canonFacts"] as? Map<String, Any> ?: emptyMap(),
                version = data["version"] as? Int ?: 1,
                isolated = data["isolated"] as? Boolean ?: true,
                createdAt = Instant.parse(data["createdAt"] as String),
                updatedAt = Instant.parse(data["updatedAt"] as String)
            )
        }
    }
}