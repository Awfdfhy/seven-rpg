# Seven RPG — State and Event Contract

**Status:** DRAFT — pre-implementation (G3 gate)  
**Directive:** Typed commands, deterministic validation, event IDs, idempotency, concurrency, stale-action rules.

## Typed Player Command
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

## Deterministic Validation Rules
1. `command.revision_base == current_state.revision` — else reject as stale.
2. `command.player_id` matches current scene player — else reject unauthorized.
3. Action text parsed into typed proposal; never applied directly.
4. Resource checks (health, inventory, currency) enforced before event generation.

## Domain Event
```
Event {
  event_id: string
  type: string            # e.g. narrative_advance, attribute_change, inventory_add
  revision_base: int
  authorized: boolean
  payload: map<string, any>
}
```

## Reducer (deterministic)
```
apply(state: GameState, event: Event) -> GameState
```
- Pure function; no side effects.
- Same state + same event → same result every time.
- Invalid events rejected without mutation.

## Idempotency & Concurrency
- Event IDs unique; duplicate event_id → ignored (idempotent).
- Optimistic concurrency: revision incremented on each successful apply.
- Stale commands (revision_base < current revision) rejected.

## State Categories (kept separate)
1. Canon facts
2. Confirmed event log
3. Current authoritative state
4. Character knowledge
5. Character beliefs / uncertainty
6. Rumors / hearsay
7. Compacted summaries (with provenance)
8. Generated suggestions (pending validation)