package com.sevenrpg.domain


/**
 * Deterministic mock AI provider for MVP-0 testing.
 * Directive: codex-fable5 — deterministic mock for tests; real providers replaceable.
 * Replaceable by a real provider after contract tests pass (G5).
 */
class MockAIProvider(private val seed: String = "mock-default") : AIProvider {
    private var callCount = 0
    private var lastRequest: Map<String, Any>? = null

    override fun generateNarrative(
        goal: String,
        context: Map<String, Any>,
        revision: Int
    ): Proposal {
        callCount++
        lastRequest = mapOf(
            "goal" to goal.take(80),
            "contextKeys" to context.keys,
            "revision" to revision
        )

        // Deterministic narrative based on goal hash (no randomness)
        val narrativeSeed = (goal.hashCode() * revision.hashCode()) % 1000
        val proseTemplates = listOf(
            "العالم يستجيب لإجراءتك: $goal",
            "الشخصية تتحرك في المشهد وتكتشف أدلة جديدة.",
            "يحدث تحول غير متوقع في الأحداث بناءً على خيارك.",
            "المخزون يتغير بعد تنفيذ الإجراء.",
            "علاقات الشخصيات تتطور استجابةً لقرارك."
        )
        val prose = proseTemplates[narrativeSeed.absoluteValue % proseTemplates.size].replace("{goal}", goal.take(50))

        // Deterministic event proposal
        val eventId = "evt_${revision}_${callCount}_${Integer.toHexString(goal.hashCode())}"
        return Proposal(
            type = "narrative_response",
            prose = prose,
            events = listOf(
                mapOf(
                    "eventId" to eventId,
                    "type" to "narrative_advance",
                    "revisionBase" to revision,
                    "authorized" to true,
                    "payload" to mapOf(
                        "description" to prose,
                        "derivedFrom" to goal.take(50)
                    )
                )
            ),
            attemptsUnauthorizedMutation = false,
            revisionBase = revision,
            provider = "mock",
            callId = callCount.toString()
        )
    }

    override fun cancel(callId: String): Boolean {
        return true
    }

    override fun declareCapabilities(): AIProviderCapabilities {
        return AIProviderCapabilities(
            provider = "mock",
            streaming = false,
            cancellation = true,
            structuredOutput = true,
            timeoutSupport = true,
            retrySupport = true,
            maxRevisionBase = 1000000
        )
    }
}