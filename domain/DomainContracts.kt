package com.sevenrpg.domain

/**
 * Domain contracts — stack-agnostic definitions.
 * Directive: multi-agent-architect — typed domain entities independent of UI/provider.
 *
 * These contracts define the boundary between:
 * 1. Domain (pure Kotlin, no UI/AI dependency)
 * 2. UI (Android Views/Compose)
 * 3. AI Provider (Mock → Real after contract test)
 *
 * Data flow:
 * User Action → PlayerCommand → validateCommand →
 *   → AI Provider (mock) → Proposal → validateProposal →
 *   → applyEvent → GameState → Atomic Save → Recover
 */