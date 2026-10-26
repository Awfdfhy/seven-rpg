package com.sevenrpg.domain

/**
 * Scene entity — player enters a scene to play.
 * Directive: multi-agent-architect — typed domain entities independent of UI/provider.
 */
data class Scene(
    val sceneId: String,
    val worldId: String,
    val playerId: String,
    val canonFactsLoaded: Boolean = true,
    val characterKnowledge: Map<String, Any> = emptyMap()
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "sceneId" to sceneId,
            "worldId" to worldId,
            "playerId" to playerId,
            "canonFactsLoaded" to canonFactsLoaded,
            "characterKnowledge" to characterKnowledge
        )
    }

    companion object {
        fun fromMap(data: Map<String, Any>): Scene {
            return Scene(
                sceneId = data["sceneId"] as String,
                worldId = data["worldId"] as String,
                playerId = data["playerId"] as String,
                canonFactsLoaded = data["canonFactsLoaded"] as? Boolean ?: true,
                characterKnowledge = data["characterKnowledge"] as? Map<String, Any> ?: emptyMap()
            )
        }
    }
}