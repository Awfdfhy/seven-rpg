# Seven RPG — Data Model Contract

**Status:** DRAFT — pre-implementation (G3 gate)  
**Directive:** Define versioned world/player schema before save logic. Versioned, recoverable, exportable. No destructive migrations.

## Entities

### World
| Field | Type | Constraints |
|-------|------|-------------|
| world_id | string | UUID-like, unique per campaign |
| name | string | non-empty |
| canon_facts | map<string, any> | canonical world facts only |
| version | int | >= 1, incremented on structural change |
| isolated | boolean | true — never mix with another world |
| created_at | timestamp | ISO-8601 |
| updated_at | timestamp | ISO-8601 |

### PlayerCharacter
| Field | Type | Constraints |
|-------|------|-------------|
| player_id | string | unique within world |
| name | string | non-empty |
| identity_sheet | map | player-defined character sheet |
| attributes | map | deterministic stats |
| version | int | >= 1 |
| world_id | string | references World.world_id |

### Scene
| Field | Type | Constraints |
|-------|------|-------------|
| scene_id | string | unique |
| world_id | string | references World |
| player_id | string | references PlayerCharacter |
| canon_facts_loaded | boolean | true before play |
| character_knowledge | map | character-specific knowledge only |

### DomainEvent
| Field | Type | Constraints |
|-------|------|-------------|
| event_id | string | unique, immutable |
| type | string | event taxonomy |
| revision_base | int | optimistic concurrency base |
| authorized | boolean | validated before application |
| payload | map | typed event data |
| timestamp | timestamp | ISO-8601 |

## Versioning
- Save format versioned: `save_v1`, `save_v2`, ...
- Migration scripts per version bump; rollback tested.
- Atomic save: write temp → fsync → atomic rename; backup previous version.

## Isolation
- Canon, confirmed events, authoritative state, character knowledge, beliefs, rumors, summaries, suggestions stored separately.
- A generated suggestion does not become history until domain rules + user authority approve.

## Export/Import
- JSON schema with size limits.
- Validation before import; confirmation step; rollback on failure.