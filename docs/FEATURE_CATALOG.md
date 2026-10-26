# Seven RPG — Feature Catalog (MVP-0)

**Version:** 1.0  
**Date:** 2026-10-25  
**Status:** Draft — awaiting stack decision (ADR-0001)  
**Directive:** Every feature has stable ID, priority, dependencies, acceptance tests, owner, status, evidence. No feature is complete because documentation exists.

---

## Feature ID Convention
`F-{domain}-{number}` where domain ∈ {CORE, WORLD, PLAYER, AI, DATA, UI, ANDROID, SECURITY}

---

## MVP-0 Core Features

| ID | Feature | Priority | Dependencies | Acceptance Tests | Owner | Status | Evidence |
|----|---------|----------|--------------|------------------|-------|--------|----------|
| F-CORE-001 | App launch and existing save recovery | P0 | None | Launch succeeds; existing save loads identical state; no crash on first run | Platform | Pending | BOOTSTRAP_REPORT.md MVP-0 |
| F-CORE-002 | World creation | P0 | F-CORE-001 | New world created with versioned schema; isolated from other worlds | Domain | Pending | GENESIS_PLAN.md G4 |
| F-CORE-003 | Player character creation | P0 | F-CORE-002 | PC created with identity sheet; attributes validated | Domain | Pending | GENESIS_PLAN.md G4 |
| F-CORE-004 | Scene entry | P0 | F-CORE-003 | User enters a scene; canonical facts loaded; character knowledge separated | Domain | Pending | GENESIS_PLAN.md G4 |
| F-CORE-005 | Player action submission | P0 | F-CORE-004 | Action submitted; typed command created; revision base recorded | Domain | Pending | GENESIS_PLAN.md G4 |
| F-CORE-006 | Action validation | P0 | F-CORE-005 | Action validated against current state, player agency, rules, resources | Domain | Pending | MASTER_PROMPT.md §7 |
| F-CORE-007 | Structured narrative from mock AI provider | P0 | F-CORE-006 | Deterministic mock returns proposal + prose; malformed output handled gracefully | AI | Pending | MASTER_PROMPT.md §9 |
| F-CORE-008 | Domain event validation | P0 | F-CORE-007 | Proposed events validated; illegal/unauthorized events rejected without mutation | Domain | Pending | MASTER_PROMPT.md §7 |
| F-CORE-009 | Apply legal domain events | P0 | F-CORE-008 | Only authorized events mutate state; event IDs + idempotency enforced | Domain | Pending | MASTER_PROMPT.md §7 |
| F-CORE-010 | Atomic save | P0 | F-CORE-009 | Save written atomically; corruption on partial write prevented | Data | Pending | GENESIS_PLAN.md G3 |
| F-CORE-011 | Force-stop / reopen recovery | P0 | F-CORE-010 | App force-stopped and reopened; world + character state identical | Platform | Pending | GENESIS_PLAN.md G4 |
| F-CORE-012 | Adversarial failure cases | P0 | F-CORE-001..F-CORE-011 | All failure cases in BOOTSTRAP_REPORT.md §4 tested (malformed, illegal, duplicate, cancel, stale, corrupt, migration, offline, RTL/LTR) | QA | Pending | BOOTSTRAP_REPORT.md §4 |

---

## Post-MVP-0 Features (deferred until after MVP-0 gates pass)

| ID | Feature | Priority | Dependencies | Status |
|----|---------|----------|--------------|--------|
| F-WORLD-001 | Map / world travel | P1 | F-CORE-012 | Deferred |
| F-WORLD-002 | Quests | P1 | F-WORLD-001 | Deferred |
| F-PLAYER-001 | Attributes and checks | P1 | F-CORE-012 | Deferred |
| F-PLAYER-002 | Inventory / equipment | P1 | F-PLAYER-001 | Deferred |
| F-PLAYER-003 | Relationships / factions | P1 | F-PLAYER-002 | Deferred |
| F-AI-001 | Real AI provider (replaceable) | P1 | F-CORE-012 | Deferred — mock only until contract tested |
| F-UI-001 | Design tokens + shared components | P1 | F-CORE-012 | Deferred |
| F-UI-002 | Arabic RTL / English LTR screens | P1 | F-UI-001 | Deferred |
| F-ANDROID-001 | Android release gates | P1 | F-CORE-012 | Deferred |

---

## Non-Features (explicitly out of scope for MVP-0)

- General AI assistant / chatbot
- Coding agent / productivity suite
- Real AI provider credentials in client bundle
- Legacy code copy or destructive migration
- Merge to `main` or public release without owner approval
