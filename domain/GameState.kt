package com.sevenrpg.domain

/**
 * Aggregate root — current authoritative game state.
 * Directive: multi-agent-architect — single source of truth for game state.
 */
data class GameState(
    val world: World? = null,
    val player: PlayerCharacter? = null,
    val scene: Scene? = null,
    val events: List<DomainEvent> = emptyList(),
    val revision: Int = 1,
    val canonFacts: Map<String, Any> = emptyMap(),
    val confirmedEventLog: List<DomainEvent> = emptyList(),
    val characterKnowledge: Map<String, Any> = emptyMap(),
    val characterBeliefs: Map<String, Any> = emptyMap(),
    val rumors: List<Map<String, Any>> = emptyList(),
    val summaries: List<Map<String, Any>> = emptyList(),
    val campaignSettings: CampaignSettings? = null
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "world" to world?.toMap(),
            "player" to player?.toMap(),
            "scene" to scene?.toMap(),
            "events" to events.map { it.toMap() },
            "revision" to revision,
            "canonFacts" to canonFacts,
            "campaignSettings" to campaignSettings?.toMap()
        )
    }

    companion object {
        fun fromMap(data: Map<String, Any>): GameState {
            return GameState(
                world = data["world"]?.let { World.fromMap(it as Map<String, Any>) },
                player = data["player"]?.let { PlayerCharacter.fromMap(it as Map<String, Any>) },
                scene = data["scene"]?.let { Scene.fromMap(it as Map<String, Any>) },
                events = (data["events"] as? List<*>)
                    ?.map { DomainEvent.fromMap(it as Map<String, Any>) }
                    ?: emptyList(),
                revision = data["revision"] as? Int ?: 1,
                canonFacts = data["canonFacts"] as? Map<String, Any> ?: emptyMap(),
                campaignSettings = data["campaignSettings"]?.let { CampaignSettings.fromMap(it as Map<String, Any>) }
            )
        }

        fun createInitial(userGoal: String = ""): GameState {
            return GameState(
                revision = 1,
                events = emptyList(),
                confirmedEventLog = emptyList()
            )
        }
    }
}