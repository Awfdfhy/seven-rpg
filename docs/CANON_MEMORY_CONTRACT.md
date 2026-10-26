# Seven RPG — Canon and Memory Contract

**Status:** DRAFT — pre-implementation  
**Directive:** Keep Canon, events, knowledge, beliefs, rumors, summaries, suggestions separate. Memory retrieval respects world, character, time, relevance, confidence, source.

## Data Categories

| Category | Description | Mutable by AI? |
|----------|-------------|----------------|
| Canon facts | Authoritative world facts | No (domain rules only) |
| Confirmed event log | Append-only history of applied events | No |
| Current authoritative state | Derived from canon + events | No (reducer only) |
| Character knowledge | What this character knows | No (domain rules) |
| Character beliefs | Uncertain character beliefs | Yes (proposals only) |
| Rumors / hearsay | Unverified information | Yes (proposals only) |
| Compacted summaries | Summaries with provenance | Yes (proposals only) |
| Generated suggestions | AI suggestions awaiting validation | Yes (proposals only) |

## Memory Retrieval Rules
- Scope by world_id (never cross worlds).
- Scope by character_id (character-appropriate knowledge only).
- Filter by time (no future knowledge).
- Rank by relevance + confidence + source reliability.
- A suggestion becomes history only after domain validation + user authority.

## Provenance
- Every memory entry carries source, confidence, timestamp, and world/character scope.
- Summaries record which events they compacted and when.