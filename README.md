# Seven RPG — Greenfield Bootstrap (Local Workspace)

**Status:** Planning/bootstrap only — no production runtime yet.  
**Directive:** codex-fable5 evidence-first. No claim of execution unless actually run.

## What this is
A local design and planning workspace for **Seven RPG**, an independent mobile-first AI-powered RPG. Based on the greenfield documentation staged in `https://github.com/Awfdfhy/seven-ai-true/tree/db763b5a81975994f01d4b0dc3e434b23c33d0db/greenfield`.

## Loaded skills
- `codex-fable5` — evidence-first: inspect before acting, track goals, verify before completion.
- `continuous-agent-loop` — production loop with quality gates, backlog, verification.
- `tokenwise` — model-fallback routing (haiku/sonnet/opus); local cost/token logging.
- `agenthub` — N parallel competing agents, coordinator eval/merge.
- `multi-agent-architect` — LangGraph TypedDict state, one-responsibility agents, allowlist routing, step_count guard.

## Folder structure
```
seven-rpg-bootstrap/
├── AGENTS.md              # Agent contract
├── AGENTHUB_SESSION.md    # AgentHub parallel-agent template
├── README.md              # This file
├── main.py                # MVP-0 smoke test entry point
├── agents/                # One file per agent role (supervisor, world, player, scene, action, validator, ai_provider, saver)
├── configs/               # Model router (tokenwise fallback)
├── graphs/                # LangGraph state + compiled workflow
├── memory/                # (empty) Redis/VectorDB memory helpers — TBD after stack choice
├── prompts/               # (empty) Prompt templates — TBD after stack choice
├── tools/                 # (empty) Tool wrappers — TBD after stack choice
├── workflows/             # (empty) High-level orchestration — TBD after stack choice
├── api/                   # (empty) FastAPI routes — optional, TBD
├── tests/                 # MVP-0 adversarial acceptance tests
└── docs/                  # BOOTSTRAP_REPORT, FEATURE_CATALOG, CURRENT_STATUS, ADR-0001, STACK_SCORECARD, DATA_MODEL, STATE_AND_EVENT_CONTRACT, AI_RUNTIME_CONTRACT, CANON_MEMORY_CONTRACT
```

## How to run (after Python + langgraph installed)
```bash
cd seven-rpg-bootstrap
python main.py
```
Runs the MVP-0 deterministic smoke test (mock AI provider, no credentials required).

## Blockers
- Separate GitHub repo `Awfdfhy/seven-rpg` not created (owner action).
- Legacy source not inspected (access required).
- No stack selected (ADR-0001 pending).
- `langgraph` not installed locally.

## Safety
No merge to `main`, no release, no paid usage without owner approval. No secrets in code.