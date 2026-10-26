# Seven RPG — Domain Contracts (Stack-Agnostic)

**Status:** Ready — works with any tech stack  
**Directive:** multi-agent-architect — TypedDict-like state, one responsibility per module, allowlist routing, step_count guard.

---

## 1. State Schema (Typed)

```python
class AgentState(TypedDict):
    user_goal: str
    world_id: Optional[str]
    player_id: Optional[str]
    scene_id: Optional[str]
    tasks: List[str]
    completed_tasks: List[str]
    next_agent: str
    context: Dict[str, Any]
    step_count: int          # guard against infinite loops
    error: Optional[str]
    revision: int            # optimistic concurrency base
    proposal: Optional[Dict[str, Any]]  # AI proposal awaiting validation
    events: List[Dict[str, Any]]        # applied domain events
```

---

## 2. Entities

### World
| Field | Type | Constraint |
|-------|------|------------|
| world_id | string | unique, immutable |
| name | string | non-empty, max 30 chars |
| canon_facts | map<string, any> | canonical world facts only |
| version | int | >= 1 |
| isolated | boolean | true — never mix worlds |
| created_at | timestamp | ISO-8601 |
| updated_at | timestamp | ISO-8601 |

### PlayerCharacter
| Field | Type | Constraint |
|-------|------|------------|
| player_id | string | unique within world |
| name | string | non-empty |
| identity_sheet | map | player-defined |
| attributes | map | deterministic stats |
| version | int | >= 1 |
| world_id | string | references World |

### Scene
| Field | Type | Constraint |
|-------|------|------------|
| scene_id | string | unique |
| world_id | string | references World |
| player_id | string | references PlayerCharacter |
| canon_facts_loaded | boolean | true before play |
| character_knowledge | map | character-specific only |

### DomainEvent
| Field | Type | Constraint |
|-------|------|------------|
| event_id | string | unique, immutable |
| type | string | event taxonomy |
| revision_base | int | optimistic concurrency base |
| authorized | boolean | validated before application |
| payload | map | typed event data |
| timestamp | timestamp | ISO-8601 |

---

## 3. Typed Player Command

```
Command {
  command_id: string
  player_id: string
  scene_id: string
  action: string          # player-submitted, untrusted text
  revision_base: int      # state revision this command is based on
  timestamp: timestamp
}
```

---

## 4. Deterministic Validation Rules

1. `command.revision_base == current_state.revision` — else reject as stale
2. `command.player_id` matches current scene player — else reject unauthorized
3. Action text parsed into typed proposal; never applied directly
4. Resource checks (health, inventory, currency) enforced before event generation

---

## 5. Reducer (Deterministic)

```
apply(state: GameState, event: Event) -> GameState
```
- Pure function; no side effects
- Same state + same event → same result every time
- Invalid events rejected without mutation

---

## 6. Idempotency & Concurrency

- Event IDs unique; duplicate event_id → ignored (idempotent)
- Optimistic concurrency: revision incremented on each successful apply
- Stale commands (revision_base < current revision) rejected

---

## 7. State Categories (Kept Separate)

1. Canon facts
2. Confirmed event log
3. Current authoritative state
4. Character knowledge
5. Character beliefs / uncertainty
6. Rumors / hearsay
7. Compacted summaries (with provenance)
8. Generated suggestions (pending validation)

---

## 8. AI Provider Interface

```
AIProvider {
  generate_narrative(goal: string, context: Context) -> Proposal
  cancel(token: CancellationToken) -> void
  declare_capabilities() -> CapabilitySet
}
```

### Proposal Schema (AI output = untrusted)
```
Proposal {
  type: string
  prose: string                 # narrative text only — not authoritative state
  events: Event[]               # candidate events for domain validation
  attempts_unauthorized_mutation: boolean
  revision_base: int
}
```

### Provider Constraints
- AI prose never mutates state directly
- Domain engine validates proposals against state, permissions, rules, event history
- Invalid proposals rejected without mutation
- Timeouts and retry budgets enforced per call
- Cancellation honored; stale late responses ignored
- Safe logging: no secrets, no PII, no user data in logs
- Credentials outside source and mobile bundles; server-side mediation preferred

---

## 9. Memory Retrieval Rules

- Scope by world_id (never cross worlds)
- Scope by character_id (character-appropriate knowledge only)
- Filter by time (no future knowledge)
- Rank by relevance + confidence + source reliability
- A suggestion becomes history only after domain validation + user authority

---

## 10. Agent Routing Allowlist

```
ALLOWED_AGENTS = {"world", "player", "scene", "action", "validator", "ai_provider", "saver", "end"}
```
- Supervisor routing output validated against this allowlist before setting `next_agent`
- step_count > 20 → route to "end" (infinite loop guard)

---

## Implementation Readiness

These contracts are stack-agnostic. Once you choose a stack (Flutter / React Native / Kotlin / Swift / Python / etc.), I will:
1. Translate these contracts into that stack's type system
2. Implement the agents in that stack's language
3. Wire the LangGraph-equivalent state machine
4. Connect the mock AI provider (already implemented in Python)
5. Run MVP-0 adversarial acceptance tests

**Awaiting your stack choice to proceed.**