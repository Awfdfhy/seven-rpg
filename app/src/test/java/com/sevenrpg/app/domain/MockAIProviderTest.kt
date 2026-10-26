package com.sevenrpg.app.domain

import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.MockAIProvider
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class MockAIProviderTest {

    @Test
    fun `generate narrative should return Proposal`() {
        val provider = DomainModule.createMockProvider()
        val proposal = provider.generateNarrative(
            goal = "explore forest",
            context = mapOf("worldId" to "w1", "playerId" to "p1"),
            revision = 1
        )
        assertFalse(proposal.attemptsUnauthorizedMutation)
        assertEquals(1, proposal.revisionBase)
        assertEquals(1, proposal.events.size)
        assertTrue(proposal.prose.isNotEmpty())
    }

    @Test
    fun `mock provider cancel should return true`() {
        val provider = DomainModule.createMockProvider()
        assertTrue(provider.cancel("test_call_id"))
    }

    @Test
    fun `mock provider should be deterministic`() {
        val provider1 = DomainModule.createMockProvider()
        val provider2 = DomainModule.createMockProvider()
        val p1 = provider1.generateNarrative("test", mapOf(), 1)
        val p2 = provider2.generateNarrative("test", mapOf(), 1)
        assertEquals(p1.prose, p2.prose)
    }
}