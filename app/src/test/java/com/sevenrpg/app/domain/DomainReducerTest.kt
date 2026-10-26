package com.sevenrpg.app.domain

import com.sevenrpg.domain.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class DomainReducerTest {

    @Test
    fun `validate command stale revision should be invalid`() {
        val state = GameState.createInitial().copy(revision = 5)
        val cmd = PlayerCommand.create("p1", "s1", "explore forest", revisionBase = 3)
        val result = DomainReducer.validateCommand(cmd, state)
        assertFalse(result.isValid)
        assertEquals(1, result.errors.size)
    }

    @Test
    fun `validate command unauthorized player should be invalid`() {
        val state = GameState.createInitial().copy(
            player = PlayerCharacter(playerId = "p1", name = "Hero", worldId = "w1"),
            revision = 1
        )
        val cmd = PlayerCommand.create("p2", "s1", "action", revisionBase = 1)
        val result = DomainReducer.validateCommand(cmd, state)
        assertFalse(result.isValid)
        assertTrue(result.errors.any { it.contains("not authorized") })
    }

    @Test
    fun `validate command empty action should be invalid`() {
        val state = GameState.createInitial().copy(
            player = PlayerCharacter(playerId = "p1", name = "Hero", worldId = "w1"),
            revision = 1
        )
        val cmd = PlayerCommand.create("p1", "s1", "  ", revisionBase = 1)
        val result = DomainReducer.validateCommand(cmd, state)
        assertFalse(result.isValid)
        assertTrue(result.errors.any { it.contains("empty") })
    }

    @Test
    fun `validate command valid should pass`() {
        val state = GameState.createInitial().copy(
            player = PlayerCharacter(playerId = "p1", name = "Hero", worldId = "w1"),
            revision = 1
        )
        val cmd = PlayerCommand.create("p1", "s1", "explore", revisionBase = 1)
        val result = DomainReducer.validateCommand(cmd, state)
        assertTrue(result.isValid)
        assertEquals(0, result.errors.size)
    }

    @Test
    fun `apply event valid should increment revision`() {
        val state = GameState.createInitial()
        val event = DomainEvent.create("narrative_advance", revisionBase = 1)
        val (newState, success) = DomainReducer.applyEvent(state, event)
        assertTrue(success)
        assertEquals(2, newState.revision)
        assertEquals(1, newState.events.size)
    }

    @Test
    fun `apply event unauthorized should be rejected`() {
        val state = GameState.createInitial()
        val event = DomainEvent.create("test", revisionBase = 1, authorized = false)
        val (newState, success) = DomainReducer.applyEvent(state, event)
        assertFalse(success)
        assertEquals(1, newState.revision)
        assertEquals(0, newState.events.size)
    }

    @Test
    fun `apply event stale revision should be rejected`() {
        val state = GameState.createInitial().copy(revision = 5)
        val event = DomainEvent.create("test", revisionBase = 3)
        val (newState, success) = DomainReducer.applyEvent(state, event)
        assertFalse(success)
        assertEquals(5, newState.revision)
    }

    @Test
    fun `apply event idempotent should reject duplicate`() {
        val state = GameState.createInitial()
        val event = DomainEvent.create("test", revisionBase = 1)
        val (state1, success1) = DomainReducer.applyEvent(state, event)
        assertTrue(success1)
        val (state2, success2) = DomainReducer.applyEvent(state1, event)
        assertFalse(success2)
        assertEquals(state1.revision, state2.revision)
    }

    @Test
    fun `validate proposal unauthorized mutation should be invalid`() {
        val state = GameState.createInitial()
        val proposal = mapOf(
            "type" to "test_proposal",
            "attemptsUnauthorizedMutation" to true,
            "events" to emptyList<Map<String, Any>>(),
            "revisionBase" to 1
        )
        val result = DomainReducer.validateProposal(proposal, state)
        assertFalse(result.isValid)
        assertTrue(result.errors.any { it.contains("unauthorized") })
    }

    @Test
    fun `validate proposal stale revision should be invalid`() {
        val state = GameState.createInitial().copy(revision = 5)
        val proposal = mapOf(
            "type" to "test_proposal",
            "revisionBase" to 3,
            "events" to emptyList<Map<String, Any>>(),
            "attemptsUnauthorizedMutation" to false
        )
        val result = DomainReducer.validateProposal(proposal, state)
        assertFalse(result.isValid)
        assertTrue(result.errors.any { it.contains("stale") })
    }

    @Test
    fun `validate proposal duplicate event ids should be invalid`() {
        val state = GameState.createInitial()
        val proposal = mapOf(
            "type" to "test_proposal",
            "revisionBase" to 1,
            "events" to listOf(
                mapOf("eventId" to "evt_1", "type" to "test"),
                mapOf("eventId" to "evt_1", "type" to "test2")
            ),
            "attemptsUnauthorizedMutation" to false
        )
        val result = DomainReducer.validateProposal(proposal, state)
        assertFalse(result.isValid)
        assertTrue(result.errors.any { it.contains("duplicate") })
    }

    @Test
    fun `validate proposal valid should pass`() {
        val state = GameState.createInitial()
        val proposal = mapOf(
            "type" to "test_proposal",
            "revisionBase" to 1,
            "events" to listOf(mapOf("eventId" to "evt_1", "type" to "narrative_advance", "authorized" to true)),
            "attemptsUnauthorizedMutation" to false
        )
        val result = DomainReducer.validateProposal(proposal, state)
        assertTrue(result.isValid)
        assertEquals(0, result.errors.size)
    }

    @Test
    fun `game state serialization round trip`() {
        val state = GameState.createInitial().copy(
            world = World(worldId = "w1", name = "Test World"),
            player = PlayerCharacter(playerId = "p1", name = "Hero", worldId = "w1"),
            revision = 1
        )
        val map = state.toMap()
        val restored = GameState.fromMap(map)
        assertEquals("Test World", restored.world?.name)
        assertEquals("Hero", restored.player?.name)
        assertEquals(1, restored.revision)
    }

    @Test
    fun `mock provider generates valid proposal`() {
        val provider = DomainModule.createMockProvider()
        val proposal = provider.generateNarrative(
            goal = "explore forest",
            context = mapOf("worldId" to "w1", "playerId" to "p1"),
            revision = 1
        )
        assertFalse(proposal.attemptsUnauthorizedMutation)
        assertEquals(1, proposal.revisionBase)
        assertEquals(1, proposal.events.size)
    }

    @Test
    fun `world serialization round trip`() {
        val world = World(worldId = "w1", name = "Test World", canonFacts = mapOf("magic" to true))
        val map = world.toMap()
        val restored = World.fromMap(map)
        assertEquals("w1", restored.worldId)
        assertEquals("Test World", restored.name)
        assertTrue(restored.canonFacts["magic"] as Boolean)
    }

    @Test
    fun `player character serialization round trip`() {
        val player = PlayerCharacter(playerId = "p1", name = "Hero", worldId = "w1", attributes = mapOf("strength" to 12))
        val map = player.toMap()
        val restored = PlayerCharacter.fromMap(map)
        assertEquals("p1", restored.playerId)
        assertEquals("Hero", restored.name)
        assertEquals(12, restored.attributes["strength"])
    }

    @Test
    fun `campaign settings creation defaults`() {
        val settings = CampaignSettings(campaignSettingsId = "cs_1", worldId = "w1")
        assertEquals("cs_1", settings.campaignSettingsId)
        assertEquals("w1", settings.worldId)
        assertEquals("medium", settings.difficulty)
        assertEquals(1.0, settings.difficultyMultiplier)
        assertEquals("neutral", settings.tone)
        assertEquals("neutral", settings.npcBehavior)
    }

    @Test
    fun `campaign settings serialization round trip`() {
        val settings = CampaignSettings(
            campaignSettingsId = "cs_2",
            worldId = "w2",
            difficulty = "hard",
            tone = "dark",
            npcBehavior = "hostile",
            startingConditions = mapOf("gold" to 50),
            customSettings = mapOf("permadeath" to true)
        )
        val map = settings.toMap()
        val restored = CampaignSettings.fromMap(map)
        assertEquals("cs_2", restored.campaignSettingsId)
        assertEquals("w2", restored.worldId)
        assertEquals("hard", restored.difficulty)
        assertEquals("dark", restored.tone)
        assertEquals("hostile", restored.npcBehavior)
        assertEquals(50, restored.startingConditions["gold"])
        assertEquals(true, restored.customSettings["permadeath"])
    }

    @Test
    fun `game state with campaign settings round trip`() {
        val settings = CampaignSettings(
            campaignSettingsId = "cs_gs1",
            worldId = "w1",
            difficulty = "easy",
            tone = "heroic"
        )
        val state = GameState.createInitial().copy(
            world = World(worldId = "w1", name = "Test World"),
            player = PlayerCharacter(playerId = "p1", name = "Hero", worldId = "w1"),
            campaignSettings = settings
        )
        val map = state.toMap()
        val restored = GameState.fromMap(map)
        assertEquals("Test World", restored.world?.name)
        assertEquals("Hero", restored.player?.name)
        assertNotNull(restored.campaignSettings)
        assertEquals("easy", restored.campaignSettings?.difficulty)
        assertEquals("heroic", restored.campaignSettings?.tone)
    }

    @Test
    fun `apply event campaign settings updated should set state`() {
        val state = GameState.createInitial()
        val settings = CampaignSettings(
            campaignSettingsId = "cs_red1",
            worldId = "w1",
            difficulty = "easy",
            tone = "heroic"
        )
        val event = DomainEvent.create(
            "campaign_settings_updated",
            revisionBase = 1,
            payload = mapOf("campaignSettings" to settings.toMap())
        )
        val (newState, success) = DomainReducer.applyEvent(state, event)
        assertTrue(success)
        assertEquals(2, newState.revision)
        assertNotNull(newState.campaignSettings)
        assertEquals("easy", newState.campaignSettings?.difficulty)
        assertEquals("heroic", newState.campaignSettings?.tone)
    }

    @Test
    fun `apply event campaign settings updated stale revision should reject`() {
        val state = GameState.createInitial().copy(revision = 5)
        val event = DomainEvent.create(
            "campaign_settings_updated",
            revisionBase = 3,
            payload = mapOf("campaignSettings" to mapOf("campaignSettingsId" to "cs", "worldId" to "w1"))
        )
        val (newState, success) = DomainReducer.applyEvent(state, event)
        assertFalse(success)
        assertEquals(5, newState.revision)
    }

    @Test
    fun `apply event campaign settings updated unauthorized should reject`() {
        val state = GameState.createInitial()
        val event = DomainEvent.create(
            "campaign_settings_updated",
            revisionBase = 1,
            payload = mapOf("campaignSettings" to mapOf("campaignSettingsId" to "cs", "worldId" to "w1")),
            authorized = false
        )
        val (newState, success) = DomainReducer.applyEvent(state, event)
        assertFalse(success)
        assertEquals(null, newState.campaignSettings)
    }
}