package com.sevenrpg.domain

import java.time.Instant

/**
 * Result of validating a command or proposal.
 * Directive: codex-fable5 — evidence-first validation.
 */
data class ValidationResult(
    val isValid: Boolean,
    val errors: List<String> = emptyList(),
    val warnings: List<String> = emptyList(),
    val validatedAt: Instant = Instant.now()
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "isValid" to isValid,
            "errors" to errors,
            "warnings" to warnings,
            "validatedAt" to validatedAt.toString()
        )
    }
}