package com.sevenrpg.domain

/**
 * AI proposal — untrusted output, never mutates state directly.
 * Directive: multi-agent-architect — AI returns proposals + prose only.
 */
data class Proposal(
    val type: String,
    val prose: String, // narrative text only — not authoritative state
    val events: List<Map<String, Any>> = emptyList(),
    val attemptsUnauthorizedMutation: Boolean = false,
    val revisionBase: Int = 1,
    val provider: String = "mock",
    val callId: String? = null
) {
    fun toMap(): Map<String, Any> {
        val result = linkedMapOf<String, Any>(
            "type" to type,
            "prose" to prose,
            "events" to events,
            "attemptsUnauthorizedMutation" to attemptsUnauthorizedMutation,
            "revisionBase" to revisionBase,
            "provider" to provider
        )
        callId?.let { result["callId"] = it }
        return result
    }
}