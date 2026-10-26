# Seven RPG — Bootstrap Report (Phase 0: Verify)

**Date:** 2026-10-25  
**Status:** Planning/bootstrap only — no application runtime built yet.  
**Directive:** codex-fable5 evidence-first — every claim below labeled VERIFIED / INFERRED / ASSUMED / UNKNOWN / BLOCKED.

---

## 1. Repository Provenance

| Field | Value | Confidence | Evidence |
|-------|-------|------------|----------|
| Canonical repository URL | `https://github.com/Awfdfhy/seven-ai-true` | VERIFIED | GitHub README page fetched |
| Owner | `Awfdfhy` | VERIFIED | GitHub navigation breadcrumb |
| Default branch | `main` | VERIFIED | CURRENT_STATUS.md |
| Staging branch | `greenfield/seven-rpg-bootstrap-20261024` | VERIFIED | CURRENT_STATUS.md |
| HEAD commit SHA (staging) | `db763b5a81975994f01d4b0dc3e434b23c33d0db` | VERIFIED | GitHub tree URL |
| Visibility | Public (inferred from fetchable URL) | INFERRED | URL accessible without auth |
| Working tree state | Clean (documentation only under greenfield/) | VERIFIED | CURRENT_STATUS.md |
| Files editable in this bootstrap | Only `greenfield/` documentation | VERIFIED | CURRENT_STATUS.md |

**Legacy untouched evidence:** VERIFIED. CURRENT_STATUS.md states: "No legacy source files were intentionally changed" and "The change is intended to add only documentation beneath greenfield/."

**Desired final home:** Separate repository `Awfdfhy/seven-rpg` — NOT created yet. BLOCKED pending owner creation.

---

## 2. Source Register (known requirements & historical findings)

| ID | Source | Requirement / Finding | Confidence | Evidence | Status |
|----|--------|----------------------|------------|----------|--------|
| R-001 | greenfield/README.md | Seven RPG = independent mobile-first RPG, not a general assistant | VERIFIED | README Non-negotiable boundaries | Active |
| R-002 | greenfield/README.md | Player controls consequential choices unless delegated | VERIFIED | README / AGENTS.md | Active |
| R-003 | greenfield/README.md | AI output = untrusted proposal text only | VERIFIED | README Non-negotiable boundaries | Active |
| R-004 | greenfield/README.md | Separate Canon, events, knowledge, beliefs, rumors, summaries, suggestions | VERIFIED | README Non-negotiable boundaries | Active |
| R-005 | greenfield/AGENTS.md | Deterministic rules for inventory, health, combat, progression, time, relationships, permissions | VERIFIED | AGENTS.md Game integrity | Active |
| R-006 | greenfield/AGENTS.md | Versioned, recoverable, exportable world/campaign data | VERIFIED | AGENTS.md Game integrity | Active |
| R-007 | greenfield/AGENTS.md | Arabic RTL and English LTR first-class | VERIFIED | AGENTS.md Engineering rules | Active |
| R-008 | greenfield/GENESIS_PLAN.md | G0-G9 gates defined (Repository, Product contract, Stack, Data contracts, MVP-0 slice, AI runtime, RPG systems, UI convergence, Android readiness, Release candidate) | VERIFIED | GENESIS_PLAN.md | Active |
| R-009 | greenfield/MASTER_PROMPT.md | MVP-0 journey: launch → create world → create PC → enter scene → submit action → validate → mock provider → legal events → save → force-stop/reopen → recover | VERIFIED | MASTER_PROMPT.md Section 5 | Active |
| R-010 | greenfield/MASTER_PROMPT.md | Compare at most 3 stacks; ADR-0001 before scaffold | VERIFIED | MASTER_PROMPT.md Section 6 | Active |
| R-011 | greenfield/CURRENT_STATUS.md | Next actions: feature catalogue, conflict list, stack spike, ADR-0001, then smallest vertical slice | VERIFIED | CURRENT_STATUS.md | Active |

**Unknowns:** No legacy source code inspected (only greenfield docs fetched). Existing app entry points, storage schemas, Android config, tests, CI — marked UNKNOWN until local/legacy repo inspection is authorized.

---

## 3. Conflict List

| Conflict | Description | Resolution Required |
|----------|-------------|---------------------|
| C-001 | Staging branch lives inside `seven-ai-true`; desired final home is separate repo `seven-rpg` | Owner must create `Awfdfhy/seven-rpg` before code migration |
| C-002 | No technology stack selected | Stack scorecard + ADR-0001 + proof-of-concept required (Phase 2) |
| C-003 | MVP-0 defined in docs but no code/tests exist | Implementation must follow G0-G3 gates first |

---

## 4. MVP-0 Acceptance Journey (adversarial suite)

A new user can:
1. Launch app
2. Create world
3. Create player character
4. Enter a scene
5. Submit player action
6. Action validated against current state + player agency
7. Receive structured narrative from **deterministic mock provider**
8. Validate proposed domain events
9. Apply only legal events
10. Save atomically
11. Force-stop / reopen and recover identical world + character state

**Failure cases to test (required):**
- Malformed or empty model response
- Proposal attempts unauthorized state mutation
- Illegal action / insufficient resources
- Duplicate submission / replayed event
- User cancellation while request in flight
- Late response arriving after cancellation / newer action
- Interrupted save / corrupted save
- Migration failure and recovery
- Offline launch and offline action
- World/campaign isolation
- Arabic RTL, English LTR, mixed-direction text, long text, keyboard navigation

---

## 5. Technology Stack Scorecard (Phase 2 placeholder)

Score at most 3 stacks against: Android distribution, mobile UI quality, Arabic RTL, persistence/migrations, deterministic domain tests, AI streaming/cancellation, offline mode, low/mid-range performance, accessibility, build reproducibility, app size, licensing, ecosystem maintenance, agent ergonomics.

**Stack candidates (to be scored):** UNKNOWN — not yet evaluated.  
**ADR-0001:** Not yet written (BLOCKED until scorecard complete).

---

## 6. Architecture Boundaries (pre-implementation)

| Boundary | Interface | Owner |
|----------|-----------|-------|
| World/campaign repository | Versioned save codec, atomic boundaries | Domain |
| Typed player commands | Deterministic validation, event IDs, idempotency, concurrency | Domain |
| Domain events | Reducer, event identity, replay rules | Domain |
| Narrative request/response | Schema for AI proposals | AI runtime |
| AI provider | Capability + cancellation contract | AI runtime |
| Canon/memory | Retrieval/writes separated by world, character, time, confidence, source | Memory |
| Import/export | Validation, size limits, rollback | Domain |
| Telemetry/error | Sensitive-data filtering | Platform |

**Invariant:** AI returns proposals + prose. Domain engine validates against state, permissions, rules, event history. Invalid proposals rejected without mutation.

---

## 7. Dependency-Ordered Backlog (MVP-0 slice)

| ID | Task | Dependencies | Files allowed | Risk | Rollback | Status |
|----|------|--------------|---------------|------|----------|--------|
| T-001 | Source register + conflict list (this report) | None | docs/BOOTSTRAP_REPORT.md | Low | N/A | Done |
| T-002 | Feature catalogue with stable IDs + acceptance criteria | T-001 | docs/FEATURE_CATALOG.md | Low | N/A | Pending |
| T-003 | Stack comparison (max 3) + proof-of-concept spike | T-002 | docs/STACK_SCORECARD.md | Medium | Revert spike only | Pending |
| T-004 | ADR-0001 technology decision | T-003 | docs/ADR-0001.md | Low | N/A | Pending |
| T-005 | Data contracts: versioned schema, commands, events, reducer | T-004 | graphs/, tools/ | High | Schema versioning | Pending |
| T-006 | Deterministic mock AI provider | T-005 | tools/mock_provider.py | Medium | Replaceable | Pending |
| T-007 | MVP-0 vertical slice (launch → save → recover) | T-005, T-006 | agents/, graphs/ | High | Atomic save rollback | Pending |
| T-008 | Adversarial acceptance tests for MVP-0 | T-007 | tests/ | High | N/A | Pending |
| T-009 | UI contract + design tokens (RTL/LTR) | T-007 | prompts/, api/ | Medium | N/A | Pending |
| T-010 | Android readiness + release gates | T-009 | docs/ANDROID_RELEASE_GATES.md | High | N/A | Pending |

---

## 8. Exact Verification Commands (to be run per stack after selection)

```bash
# Example placeholders — replace after ADR-0001 stack choice
pytest tests/ -v                 # unit + contract tests
npm run build                    # if web/mobile stack
flutter test                     # if Flutter
./gradlew assembleDebug          # if Android/Kotlin
```

---

## 9. Blockers

| Blocker | Impact | Required action |
|---------|--------|-----------------|
| No legacy source inspected (only greenfield docs fetched) | Cannot verify existing app entry points, storage, CI, Android config | Authorize local/legacy repo inspection or grant access |
| Separate repo `Awfdfhy/seven-rpg` not created | Cannot migrate code or establish final home | Owner creates repo |
| No stack selected | Cannot scaffold or implement | Complete stack scorecard + ADR-0001 |
| No credentials available | Cannot run real AI provider tests | Use deterministic mock provider only (per plan) |

---

## 10. Evidence Statement

No command, test, emulator run, screenshot, build, benchmark, or agent action claimed in this report has been executed beyond reading the public GitHub documentation. All code/implementation claims are **planned, not executed**.

**Next unblocked task:** T-002 — Feature catalogue with stable IDs + acceptance criteria (docs/FEATURE_CATALOG.md), then T-003 stack scorecard.
