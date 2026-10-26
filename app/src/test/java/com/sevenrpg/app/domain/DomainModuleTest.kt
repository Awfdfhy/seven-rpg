package com.sevenrpg.app.domain

import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.MockAIProvider
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class DomainModuleTest {

    @Test
    fun `create mock provider should return MockAIProvider`() {
        val provider = DomainModule.createMockProvider()
        assertTrue(provider is MockAIProvider)
    }

    @Test
    fun `create initial state should return empty GameState`() {
        val state = DomainModule.createInitialState()
        assertEquals(1, state.revision)
        assertEquals(0, state.events.size)
        assertEquals(null, state.world)
        assertEquals(null, state.player)
    }

    @Test
    fun `mock provider declare capabilities`() {
        val provider = DomainModule.createMockProvider()
        val caps = provider.declareCapabilities()
        assertEquals("mock", caps.provider)
        assertTrue(caps.cancellation)
        assertTrue(caps.structuredOutput)
        assertTrue(caps.timeoutSupport)
        assertTrue(caps.retrySupport)
    }

    @Test
    fun `create campaign settings should return valid settings`() {
        val settings = DomainModule.createCampaignSettings(
            worldId = "w1",
            difficulty = "hard",
            tone = "dark",
            npcBehavior = "hostile",
            startingConditions = mapOf("gold" to 50),
            customSettings = mapOf("permadeath" to true)
        )
        assertEquals("w1", settings.worldId)
        assertEquals("hard", settings.difficulty)
        assertEquals("dark", settings.tone)
        assertEquals("hostile", settings.npcBehavior)
        assertEquals(50, settings.startingConditions["gold"])
        assertEquals(true, settings.customSettings["permadeath"])
    }
}