package com.sevenrpg.domain

import java.time.Instant
import java.util.UUID

/**
 * Immutable domain event — applied to mutate state.
 * Directive: multi-agent-architect — deterministic events, never mutated directly.
 */
data class DomainEvent(
    val eventId: String,
    val type: String,
    val revisionBase: Int,
    val authorized: Boolean = true,
    val payload: Map<String, Any> = emptyMap(),
    val timestamp: Instant = Instant.now()
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "eventId" to eventId,
            "type" to type,
            "revisionBase" to revisionBase,
            "authorized" to authorized,
            "payload" to payload,
            "timestamp" to timestamp.toString()
        )
    }

    companion object {
        fun create(
            eventType: String,
            revisionBase: Int,
            payload: Map<String, Any>? = null,
            authorized: Boolean = true
        ): DomainEvent {
            return DomainEvent(
                eventId = "evt_${revisionBase}_${UUID.randomUUID().toString().substring(0, 8)}",
                type = eventType,
                revisionBase = revisionBase,
                authorized = authorized,
                payload = payload ?: emptyMap()
            )
        }

        fun fromMap(data: Map<String, Any>): DomainEvent {
            return DomainEvent(
                eventId = data["eventId"] as String,
                type = data["type"] as String,
                revisionBase = data["revisionBase"] as Int,
                authorized = data["authorized"] as? Boolean ?: true,
                payload = data["payload"] as? Map<String, Any> ?: emptyMap(),
                timestamp = (data["timestamp"] as? String)?.let { runCatching { Instant.parse(it) }.getOrNull() } ?: Instant.EPOCH
            )
        }
    }
}