package com.sevenrpg.domain

/**
 * Extended domain module — includes all RPG systems.
 */
object ExtendedDomainModule {
    fun createExtendedGameState(userId: String): ExtendedGameState {
        return ExtendedGameState(
            gameState = GameState.createInitial(),
            playerProgression = PlayerProgression(),
            worldMap = WorldMap(),
            combatState = null
        )
    }
}