# Seven RPG — Architecture Overview

**Status:** Stack-agnostic design  
**Directive:** multi-agent-architect — domain independent of UI and provider SDKs.

---

## Architecture Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (Mobile)                        │
│  Launch → World → Character → Scene → Action → Save       │
│  RTL/Arabic | Accessibility | Touch targets                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Layer (LangGraph State Machine)          │
│  Supervisor → World → Player → Scene → Action → Validator   │
│           → AI Provider → Saver → End                       │
│  step_count guard | Allowlist routing | TypedDict state    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Domain Layer (Pure Python, Stack-Agnostic)     │
│  Entities: World, Player, Scene, Event                      │
│  Commands: PlayerCommand                                    │
│  Contracts: ValidationResult, Proposal, AIProviderInterface │
│  Reducer: apply_event (deterministic, pure)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Persistence Layer (Atomic Save)                │
│  JSON save | Backup | Corrupt recovery | Versioned          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Provider Layer (Replaceable)                │
│  Mock (deterministic) → Real (after contract test)          │
│  Model fallback: Haiku → Sonnet → Opus                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Principles

1. **Domain Independence:** Game logic has zero dependency on UI framework or AI provider SDK.
2. **One Responsibility Per Agent:** Each LangGraph node does exactly one thing.
3. **AI Never Mutates State:** AI returns proposals; domain reducer validates and applies.
4. **Deterministic Reducer:** Same state + same event → same result every time.
5. **Optimistic Concurrency:** Revision-based conflict detection.
6. **Atomic Save:** Write temp → fsync → atomic rename; backup previous version.
7. **RTL First:** Arabic primary, English secondary, icon mirroring.
8. **Accessibility First:** WCAG AA contrast, 44×44px touch targets, focus rings.

---

## Data Flow (MVP-0)

```
User Action → PlayerCommand → validate_command → 
  → AI Provider (mock) → Proposal → validate_proposal →
  → apply_event → GameState → Atomic Save → Recover
```

---

## Contract Layers

| Layer | Responsibility | Stack Dependency |
|-------|---------------|------------------|
| UI | Rendering, input, navigation | High (Flutter/RN/Kotlin/etc.) |
| Agent | Orchestration, routing | Medium (LangGraph or equivalent) |
| Domain | Rules, validation, reducer | None (pure Python) |
| Persistence | Save/load, backup, recovery | Medium (file/db) |
| AI Provider | Narrative generation | Medium (mock → real) |

---

## Blocker

Architecture cannot be implemented in target stack until ADR-0001 stack selection is complete.