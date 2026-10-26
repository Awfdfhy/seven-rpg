package com.sevenrpg.domain

import java.time.Instant

/**
 * Campaign settings — customization per campaign.
 * Directive: multi-agent-architect — typed domain entity for world configuration.
 */
data class CampaignSettings(
    val campaignSettingsId: String,
    val worldId: String,
    val difficulty: String = "medium", // easy, medium, hard, custom
    val difficultyMultiplier: Double = 1.0,
    val tone: String = "neutral", // dark, heroic, comedic, neutral, custom
    val npcBehavior: String = "neutral", // friendly, neutral, hostile, dynamic
    val startingConditions: Map<String, Any> = emptyMap(),
    val customSettings: Map<String, Any> = emptyMap(),
    val version: Int = 1,
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now()
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "campaignSettingsId" to campaignSettingsId,
            "worldId" to worldId,
            "difficulty" to difficulty,
            "difficultyMultiplier" to difficultyMultiplier,
            "tone" to tone,
            "npcBehavior" to npcBehavior,
            "startingConditions" to startingConditions,
            "customSettings" to customSettings,
            "version" to version,
            "createdAt" to createdAt.toString(),
            "updatedAt" to updatedAt.toString()
        )
    }

    companion object {
        fun fromMap(data: Map<String, Any>): CampaignSettings {
            return CampaignSettings(
                campaignSettingsId = data["campaignSettingsId"] as String,
                worldId = data["worldId"] as String,
                difficulty = data["difficulty"] as? String ?: "medium",
                difficultyMultiplier = data["difficultyMultiplier"] as? Double ?: 1.0,
                tone = data["tone"] as? String ?: "neutral",
                npcBehavior = data["npcBehavior"] as? String ?: "neutral",
                startingConditions = data["startingConditions"] as? Map<String, Any> ?: emptyMap(),
                customSettings = data["customSettings"] as? Map<String, Any> ?: emptyMap(),
                version = data["version"] as? Int ?: 1,
                createdAt = Instant.parse(data["createdAt"] as String),
                updatedAt = Instant.parse(data["updatedAt"] as String)
            )
        }
    }
}
