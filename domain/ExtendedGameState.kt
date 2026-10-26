package com.sevenrpg.domain

/**
 * Extended game state — includes all RPG systems.
 * This extends GameState with full RPG progression.
 */
data class ExtendedGameState(
    val gameState: GameState,
    val playerProgression: PlayerProgression,
    val worldMap: WorldMap,
    val combatState: CombatState? = null
) {
    fun toMap(): Map<String, Any> = mapOf(
        "gameState" to gameState.toMap(),
        "playerProgression" to playerProgression.toMap(),
        "worldMap" to worldMap.toMap(),
        "combatState" to combatState?.toMap()
    )

    companion object {
        fun fromMap(data: Map<String, Any>): ExtendedGameState = ExtendedGameState(
            gameState = GameState.fromMap(data["gameState"] as Map<String, Any>),
            playerProgression = PlayerProgression.fromMap(data["playerProgression"] as Map<String, Any>),
            worldMap = WorldMap.fromMap(data["worldMap"] as Map<String, Any>),
            combatState = data["combatState"]?.let { CombatState.fromMap(it as Map<String, Any>) }
        )
    }
}