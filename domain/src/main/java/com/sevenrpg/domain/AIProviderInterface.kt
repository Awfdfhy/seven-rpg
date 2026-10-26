package com.sevenrpg.domain

/**
 * Interface for AI providers — replaceable, declares capabilities.
 * Directive: multi-agent-architect — AI runtime returns proposals, domain engine validates.
 */
interface AIProvider {
    fun generateNarrative(goal: String, context: Map<String, Any>, revision: Int): Proposal
    fun cancel(callId: String): Boolean
    fun declareCapabilities(): AIProviderCapabilities
}

data class AIProviderCapabilities(
    val provider: String,
    val streaming: Boolean = false,
    val cancellation: Boolean = true,
    val structuredOutput: Boolean = true,
    val timeoutSupport: Boolean = true,
    val retrySupport: Boolean = true,
    val maxRevisionBase: Int = 1000000
)