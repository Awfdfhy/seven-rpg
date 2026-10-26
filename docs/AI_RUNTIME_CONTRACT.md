# Seven RPG — AI Runtime Contract

**Status:** DRAFT — pre-implementation (G5 gate)  
**Directive:** Stable provider interface, timeout, retry, cancellation, streaming, structured output validation, telemetry without secrets. Mock first; real provider only after contract tested.

## Provider Interface
```
AIProvider {
  generate_narrative(goal: string, context: Context) -> Proposal
  cancel(token: CancellationToken) -> void
  declare_capabilities() -> CapabilitySet
}
```

## Proposal Schema (AI output = untrusted)
```
Proposal {
  type: string
  prose: string                 # narrative text only — not authoritative state
  events: Event[]               # candidate events for domain validation
  attempts_unauthorized_mutation: boolean
  revision_base: int
}
```

## Provider Constraints
- AI prose never mutates state directly.
- Domain engine validates proposals against state, permissions, rules, event history.
- Invalid proposals rejected without mutation.
- Timeouts and retry budgets enforced per call.
- Cancellation honored; stale late responses ignored.
- Error classification (transient vs permanent) with backoff.
- Rate-limit handling with exponential backoff.
- Safe logging: no secrets, no PII, no user data in logs.
- Credentials outside source and mobile bundles; server-side mediation preferred.

## Model Selection (tokenwise fallback)
| Tier | Model | Task class |
|------|-------|------------|
| Mechanical | haiku | saves, format, lookups |
| Scoped reasoning | sonnet | narrative generation, single-file refactor |
| Synthesis | opus | architecture decisions, multi-file refactor |

## Testing
- Deterministic mock provider passes same contract suite as real provider.
- Failure injection: malformed JSON, empty response, unauthorized mutation, timeout, cancellation.
- Real provider integrated only after mock contract tests pass; no credentials in client bundle.