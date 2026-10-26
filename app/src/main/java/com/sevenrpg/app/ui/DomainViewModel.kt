package com.sevenrpg.app.ui

import androidx.lifecycle.ViewModel
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.MockAIProvider

/**
 * ViewModel for Seven RPG — holds game state and domain logic.
 * Directive: multi-agent-architect — ViewModel holds state, domain logic in reducers.
 */
class DomainViewModel : ViewModel() {

    private val aiProvider = DomainModule.createMockProvider()
    private var _gameState = GameState.createInitial()
    val gameState: GameState
        get() = _gameState

    fun updateState(newState: GameState) {
        _gameState = newState
    }

    fun getMockProvider(): com.sevenrpg.domain.AIProvider {
        return aiProvider
    }
}