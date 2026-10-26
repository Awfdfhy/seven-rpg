# Seven RPG — Main Entry Point
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: python main.py

import asyncio
import logging
import json
import sys
from pathlib import Path

from graphs.workflow import run

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("seven_rpg")


async def main() -> int:
    # MVP-0 smoke test: single deterministic playthrough
    user_goal = "create a new world, create a player character, enter a scene, submit 'explore the forest' action"

    logger.info("Seven RPG MVP-0 smoke test starting")
    logger.info("User goal: %s", user_goal)

    try:
        final_state = await run(user_goal)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Graph execution failed: %s", exc)
        return 1

    # Evidence output (no secrets, no fabricated claims)
    report = {
        "step_count": final_state.get("step_count"),
        "error": final_state.get("error"),
        "completed_tasks": final_state.get("completed_tasks"),
        "next_agent": final_state.get("next_agent"),
        "world_id": final_state.get("world_id"),
        "player_id": final_state.get("player_id"),
        "scene_id": final_state.get("scene_id"),
        "revision": final_state.get("revision"),
        "events_count": len(final_state.get("events", [])),
        "context_keys": list(final_state.get("context", {}).keys()),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if final_state.get("error"):
        logger.error("MVP-0 completed with error: %s", final_state["error"])
        return 1

    if final_state.get("next_agent") != "end":
        logger.error("MVP-0 did not reach 'end' state; next_agent=%s", final_state.get("next_agent"))
        return 1

    logger.info("MVP-0 smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))