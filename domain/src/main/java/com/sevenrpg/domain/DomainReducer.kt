package com.sevenrpg.domain

import kotlin.collections.toMap

/**
 * Deterministic reducer — apply an event to state.
 * Directive: multi-agent-architect — invalid events rejected without mutation.
 * Pure function: same state + same event → same result every time.
 */
object DomainReducer {

    /**
     * Validate a player command against current state, rules, and permissions.
     */
    fun validateCommand(command: PlayerCommand, state: GameState): ValidationResult {
        val errors = mutableListOf<String>()

        if (command.revisionBase != state.revision) {
            errors.add("stale command: revisionBase ${command.revisionBase} != current ${state.revision}")
        }

        if (state.player != null && command.playerId != state.player!!.playerId) {
            errors.add("player not authorized for this scene")
        }

        if (command.action.isBlank()) {
            errors.add("action text cannot be empty")
        }

        return ValidationResult(isValid = errors.isEmpty(), errors = errors)
    }

    /**
     * Validate an AI proposal against current state, rules, permissions.
     * Invalid proposals rejected without mutation.
     */
    fun validateProposal(proposal: Map<String, Any>, state: GameState): ValidationResult {
        val errors = mutableListOf<String>()

        if (!proposal.containsKey("type")) {
            errors.add("proposal is not a typed object")
            return ValidationResult(isValid = false, errors = errors)
        }

        if (proposal["attemptsUnauthorizedMutation"] == true) {
            errors.add("proposal attempts unauthorized state mutation")
        }

        if (proposal["revisionBase"] != state.revision) {
            errors.add("stale proposal: revisionBase ${proposal["revisionBase"]} != current ${state.revision}")
        }

        // Check for duplicate event IDs (idempotency)
        val events = proposal["events"] as? List<*> ?: emptyList<Any>()
        val seenIds = mutableSetOf<String>()
        for (event in events) {
            val eventMap = event as? Map<String, Any> ?: continue
            val eid = eventMap["eventId"] as? String
            if (eid != null) {
                if (eid in seenIds) {
                    errors.add("duplicate event ID: $eid")
                }
                seenIds.add(eid)
            }
        }

        return ValidationResult(isValid = errors.isEmpty(), errors = errors)
    }

    /**
     * Deterministic reducer — apply an event to state.
     * Returns (newState, success). Invalid events rejected without mutation.
     */
    fun applyEvent(state: GameState, event: DomainEvent): Pair<GameState, Boolean> {
        // Validate event authorization
        if (!event.authorized) {
            return Pair(state, false)
        }

        // Validate revision base (optimistic concurrency)
        if (event.revisionBase != state.revision) {
            return Pair(state, false)
        }

        // Check for duplicate event ID (idempotency)
        if (state.events.any { it.eventId == event.eventId }) {
            return Pair(state, false) // Idempotent — already applied
        }

        // Create new state (immutable update pattern)
        val newState = state.copy(
            events = state.events + event,
            revision = state.revision + 1,
            confirmedEventLog = state.confirmedEventLog + event
        )

        // Apply event type-specific logic
        val finalState = when (event.type) {
            "narrative_advance" -> {
                val payload = event.payload
                val charKnowledge = (payload["characterKnowledge"] as? Map<String, Any>) ?: emptyMap()
                val canonFacts = (payload["canonFacts"] as? Map<String, Any>) ?: emptyMap()
                newState.copy(
                    scene = state.scene?.copy(
                        characterKnowledge = state.scene?.characterKnowledge?.plus(charKnowledge) ?: charKnowledge
                    ),
                    canonFacts = state.canonFacts.plus(canonFacts)
                )
            }
            "attribute_change" -> {
                val payload = event.payload
                val attributes = (payload["attributes"] as? Map<String, Any>) ?: emptyMap()
                newState.copy(
                    player = state.player?.copy(
                        attributes = state.player?.attributes?.plus(attributes) ?: attributes
                    )
                )
            }
            "world_created" -> {
                val payload = event.payload
                val canonFacts = (payload["canonFacts"] as? Map<String, Any>) ?: emptyMap()
                newState.copy(
                    world = state.world?.copy(canonFacts = state.world?.canonFacts?.plus(canonFacts) ?: canonFacts)
                )
            }
            "campaign_settings_updated" -> {
                val payload = event.payload
                val settingsMap = payload["campaignSettings"] as? Map<String, Any>
                val settings = settingsMap?.let { CampaignSettings.fromMap(it) }
                newState.copy(campaignSettings = settings)
            }
            else -> newState
        }

        return Pair(finalState, true)
    }
}