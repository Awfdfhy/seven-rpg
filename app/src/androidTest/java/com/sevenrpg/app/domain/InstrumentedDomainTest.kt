package com.sevenrpg.app.domain

import androidx.test.ext.junit.runners.AndroidJUnit4
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState
import org.junit.Test
import org.junit.runner.RunWith
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * Instrumented test — runs on Android device/emulator.
 * Directive: multi-agent-architect — domain logic verified on device.
 */
@RunWith(AndroidJUnit4::class)
class InstrumentedDomainTest {

    @Test
    fun `create initial state on device`() {
        val state = DomainModule.createInitialState()
        assertEquals(1, state.revision)
        assertEquals(0, state.events.size)
    }

    @Test
    fun `mock provider works on device`() {
        val provider = DomainModule.createMockProvider()
        val proposal = provider.generateNarrative(
            goal = "test action",
            context = mapOf("worldId" to "w1", "playerId" to "p1"),
            revision = 1
        )
        assertTrue(proposal.prose.isNotEmpty())
        assertEquals(1, proposal.revisionBase)
    }

    @Test
    fun `game state serialization on device`() {
        val state = GameState.createInitial().copy(
            revision = 5
        )
        val map = state.toMap()
        val restored = GameState.fromMap(map)
        assertEquals(5, restored.revision)
    }
}