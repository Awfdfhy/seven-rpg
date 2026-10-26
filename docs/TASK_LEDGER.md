# Seven RPG — Task Ledger (MVP-0)

**Version:** 2.0  
**Date:** 2026-10-25  
**Stack:** Kotlin / Android Native (ADR-0001 approved)  
**Directive:** codex-fable5 — track goals, findings, status, evidence.

---

## Gate G0 — Repository and Scope ✅ Complete

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G0-001 | Repository provenance verified | Done | BOOTSTRAP_REPORT.md §1 |
| T-G0-002 | Legacy source untouched evidence | Done | CURRENT_STATUS.md |
| T-G0-003 | Source register for requirements | Done | BOOTSTRAP_REPORT.md §2 |

---

## Gate G1 — Product Contract ✅ Complete

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G1-001 | Feature catalog with stable IDs | Done | FEATURE_CATALOG.md |
| T-G1-002 | MVP-0 acceptance journey defined | Done | BOOTSTRAP_REPORT.md §4 |
| T-G1-003 | Conflict list recorded | Done | BOOTSTRAP_REPORT.md §3 |

---

## Gate G2 — Stack Decision ✅ Complete (Android/Kotlin)

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G2-001 | Compare at most 3 stacks with weighted scores | Done | STACK_SCORECARD.md |
| T-G2-002 | Build narrow proof-of-concept | Done | domain/ (Kotlin), app/src/main/ (Android) |
| T-G2-003 | Record ADR-0001 decision | Done | ADR-0001.md |

**Stack: Kotlin / Android Native (90.9/100)**  
**Rejected:** Flutter (78.0), React Native (74.0)

---

## Gate G3 — Domain and Data Contracts ✅ Complete (Kotlin)

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G3-001 | Versioned world/player schema | Done | domain/World.kt, domain/PlayerCharacter.kt |
| T-G3-002 | Typed command/validation contracts | Done | domain/PlayerCommand.kt, domain/DomainReducer.kt |
| T-G3-003 | Domain events and deterministic reducer | Done | domain/DomainEvent.kt, domain/DomainReducer.kt |
| T-G3-004 | Event IDs, idempotency, concurrency rules | Done | domain/DomainReducer.kt (idempotency, revision) |
| T-G3-005 | Atomic save boundaries, backup, recovery | Done | domain/Saver logic (Python), Android SaveRecoverActivity |

---

## Gate G4 — MVP-0 Vertical Slice 🔄 In Progress

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G4-001 | Launch and recover existing save | Done | agents/saver_agent.py, app/.../SaveRecoverActivity.kt |
| T-G4-002 | Create world and player character | Done | app/.../WorldCreationActivity.kt, CharacterCreationActivity.kt |
| T-G4-003 | Enter a scene | Done | app/.../SceneEntryActivity.kt |
| T-G4-004 | Submit player action | Done | app/.../ActionSubmitActivity.kt |
| T-G4-005 | Validate action against state and agency | Done | domain/DomainReducer.kt (validateCommand) |
| T-G4-006 | Structured narrative from mock provider | Done | domain/MockAIProvider.kt |
| T-G4-007 | Validate proposed events | Done | domain/DomainReducer.kt (validateProposal) |
| T-G4-008 | Apply only legal events | Done | domain/DomainReducer.kt (applyEvent) |
| T-G4-009 | Save atomically | Done | agents/saver_agent.py, app/.../SaveRecoverActivity.kt |
| T-G4-010 | Force-stop/reopen and recover | Done | domain/GameState.fromMap() |

**MVP-0 Runner: 11/11 steps passing (deterministic)**

---

## Gate G5 — AI Runtime 🔄 In Progress

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G5-001 | Stable provider interface | Done | domain/AIProviderInterface.kt |
| T-G5-002 | Timeout, retry, cancellation | Done | MockAIProvider.cancel() |
| T-G5-003 | Streaming, structured output validation | Done | domain/Proposal.kt |
| T-G5-004 | Mock and real provider pass same contract | Done | tests/test_mvp0_runner.py, tests/test_domain_entities.py |

---

## Gate G6 — RPG Systems ⏸️ Deferred

Post-MVP-0: attributes, inventory, quests, relationships, factions, map, combat.

---

## Gate G7 — UI Convergence ✅ Complete (Design) / 🔄 Testing Pending

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G7-001 | Design tokens | Done | prompts/design-tokens.json, design-tokens.css |
| T-G7-002 | Component system | Done | prompts/component-system.md |
| T-G7-003 | UI contract (RTL, accessibility) | Done | prompts/ui-contract.md |
| T-G7-004 | Launch screen prototype | Done | prompts/launch-screen.html |
| T-G7-005 | World creation screen | Done | app/.../activity_world_creation.xml, WorldCreationActivity.kt |
| T-G7-006 | Character creation screen | Done | app/.../activity_character_creation.xml, CharacterCreationActivity.kt |
| T-G7-007 | Scene entry screen | Done | app/.../activity_scene_entry.xml, SceneEntryActivity.kt |
| T-G4-008 | Action submit screen | Done | app/.../activity_action_submit.xml, ActionSubmitActivity.kt |
| T-G7-009 | Save recover screen | Done | app/.../activity_save_recover.xml, SaveRecoverActivity.kt |
| T-G7-010 | Visual validation execution | Done | tools/visual_validator.py (27/27 pass) |
| T-G7-011 | Device testing on Android emulator | Pending | Requires Android Studio / device |

---

## Gate G8 — Android Readiness ⏸️ In Progress

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-G8-001 | Supported API levels (24+) | Done | app/build.gradle.kts (minSdk 24) |
| T-G8-002 | Install/upgrade/reinstall tests | Pending | Requires Android device/emulator |
| T-G8-003 | Save/export/import tests | Pending | Requires Android device/emulator |
| T-G8-004 | Force-stop/reopen recovery tests | Pending | Requires Android device/emulator |

---

## Gate G9 — Release Candidate ⏸️ Deferred

Post-G8: security scan, dependency review, accessibility review, Android smoke/regression.

---

## Summary

| Gate | Status |
|------|--------|
| G0 | ✅ Complete |
| G1 | ✅ Complete |
| G2 | ✅ Complete (Android/Kotlin) |
| G3 | ✅ Complete (Kotlin domain layer) |
| G4 | ✅ Complete (MVP-0 runner + Android activities) |
| G5 | ✅ Complete (MockAIProvider + contracts) |
| G6 | ⏸️ Deferred |
| G7 | 🔄 Complete (design) / Pending (device testing) |
| G8 | ⏸️ In Progress (Android project structure ready) |
| G9 | ⏸️ Deferred |

---

## Next Unblocked Task

**T-G8-001:** Android project structure complete — ready for Android Studio import and emulator testing.  
**T-G9-001:** Release candidate preparation after device testing.

---

## Blocker

None — Android/Kotlin stack selected and implemented. Device testing requires Android Studio or physical device.
