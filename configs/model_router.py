# Seven RPG — Model Router (tokenwise fallback)
# Directive: tokenwise — measurement-driven model router.
# Route subtasks to cheapest model that can handle them. Log tokens+cost locally.
# Anthropic-only by design; no API keys in code.

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

LOG_PATH = Path(".tokenwise/log.ndjson")

MODEL_TIERS: Dict[str, Dict[str, Any]] = {
    "mechanical": {
        "model": "haiku-4.5",
        "task_class": ["file_reads", "grep", "format", "rename", "simple_edits", "doc_lookups"],
        "max_spawn_depth": 0,
    },
    "scoped_reasoning": {
        "model": "sonnet-4.6",
        "task_class": ["single_file_refactor", "scoped_research", "test_writing", "narrative_generation"],
        "max_spawn_depth": 1,
    },
    "synthesis": {
        "model": "opus-4.7",
        "task_class": ["architecture_decisions", "multi_file_refactor", "security_review"],
        "max_spawn_depth": 2,
    },
}


def select_tier(task_class: str) -> str:
    """Return the cheapest tier that can handle the task class."""
    for tier, spec in MODEL_TIERS.items():
        if task_class in spec["task_class"]:
            return tier
    # Default fallback to mid tier for safety
    return "scoped_reasoning"


def get_model(tier: str) -> str:
    return MODEL_TIERS[tier]["model"]


def log_task(task_description: str, tier: str, tokens_estimate: int, cost_usd: float) -> None:
    """Append a local NDJSON log entry. Zero telemetry; no analytics endpoint."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "task": task_description[:80],
        "tier": tier,
        "model": get_model(tier),
        "tokens_estimate": tokens_estimate,
        "cost_usd": cost_usd,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def require_api_key(env_var: str = "OPENAI_API_KEY") -> str:
    """Read API key from environment only. Never hardcode."""
    key = os.getenv(env_var)
    if not key:
        raise RuntimeError(f"{env_var} not set. Use deterministic mock provider for tests.")
    return key