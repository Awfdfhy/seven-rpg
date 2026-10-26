package com.sevenrpg.domain

/**
 * Domain module — wire domain components together.
 * Directive: multi-agent-architect — domain independent of UI and provider SDKs.
 */
object DomainModule {
    fun createMockProvider(): AIProvider {
        return MockAIProvider(seed = "seven-rpg-mvp-0")
    }

    fun createInitialState(): GameState {
        return GameState.createInitial()
    }

    fun createCampaignSettings(
        worldId: String,
        difficulty: String = "medium",
        tone: String = "neutral",
        npcBehavior: String = "neutral",
        startingConditions: Map<String, Any> = emptyMap(),
        customSettings: Map<String, Any> = emptyMap()
    ): CampaignSettings {
        return CampaignSettings(
            campaignSettingsId = "cs_${worldId}_${System.currentTimeMillis()}",
            worldId = worldId,
            difficulty = difficulty,
            tone = tone,
            npcBehavior = npcBehavior,
            startingConditions = startingConditions,
            customSettings = customSettings
        )
    }
}