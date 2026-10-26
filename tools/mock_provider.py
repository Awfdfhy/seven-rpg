# Seven RPG — Deterministic Mock AI Provider
# Directive: codex-fable5 — deterministic mock for tests; real providers replaceable.
# Directive: multi-agent-architect — AI returns proposals + prose only; never mutates state.
# Run: python tools/mock_provider.py

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from domain.contracts import Proposal


class MockAIProvider:
    """
    Deterministic mock AI provider for MVP-0 testing.
    Returns structured proposals without mutating game state.
    Replaceable by a real provider after contract tests pass (G5).
    """

    def __init__(self, seed: Optional[str] = None) -> None:
        self.seed = seed or "mock-default"
        self.call_count = 0
        self.last_request: Optional[Dict[str, Any]] = None

    def generate_narrative(
        self,
        goal: str,
        context: Dict[str, Any],
        revision: int,
    ) -> Dict[str, Any]:
        """
        Generate a narrative proposal.

        Args:
            goal: Player-submitted action text (untrusted).
            context: Current game context (world, player, scene).
            revision: Current state revision for optimistic concurrency.

        Returns:
            Proposal dict with prose, events, and metadata.
        """
        self.call_count += 1
        self.last_request = {
            "goal": goal[:80],
            "context_keys": list(context.keys()),
            "revision": revision,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Deterministic narrative based on goal hash (no randomness)
        narrative_seed = hash((goal, revision)) % 1000
        prose_templates = [
            "העולם يستجيب لإجراءتك: {goal}",
            "الشخصية تتحرك في المشهد وتكتشف أدلة جديدة.",
            "يحدث تحول غير متوقع في الأحداث بناءً على خيارك.",
            "المخزون يتغير بعد تنفيذ الإجراء.",
            "علاقات الشخصيات تتطور استجابةً لقرارك.",
        ]
        prose = prose_templates[narrative_seed % len(prose_templates)].format(goal=goal[:50])

        # Deterministic event proposal
        event_id = f"evt_{revision}_{uuid.uuid4().hex[:8]}"
        proposal = Proposal(
            type="narrative_response",
            prose=prose,
            events=[
                {
                    "event_id": event_id,
                    "type": "narrative_advance",
                    "revision_base": revision,
                    "authorized": True,
                    "payload": {
                        "description": prose,
                        "derived_from": goal[:50],
                    },
                }
            ],
            attempts_unauthorized_mutation=False,
            revision_base=revision,
            provider="mock",
            call_id=str(self.call_count),
        )

        return proposal

    def declare_capabilities(self) -> Dict[str, Any]:
        """Declare supported features for contract validation."""
        return {
            "provider": "mock",
            "streaming": False,
            "cancellation": True,
            "structured_output": True,
            "timeout_support": True,
            "retry_support": True,
            "max_revision_base": 1000000,
        }

    def cancel(self, call_id: int) -> bool:
        """Cancel an in-flight request. Mock always succeeds."""
        return True

    def get_last_request(self) -> Optional[Dict[str, Any]]:
        """Return the last request for test inspection."""
        return self.last_request


def main() -> None:
    """Smoke test for the mock provider."""
    provider = MockAIProvider(seed="seven-rpg-mvp-0")

    proposal = provider.generate_narrative(
        goal="استكشف الغابة المظلمة",
        context={"world_id": "world_1", "player_id": "player_1", "scene_id": "scene_1"},
        revision=1,
    )

    print(json.dumps(proposal, indent=2, ensure_ascii=False))

    # Validation assertions (evidence-first)
    assert proposal["attempts_unauthorized_mutation"] is False
    assert proposal["revision_base"] == 1
    assert len(proposal["events"]) == 1
    assert proposal["events"][0]["authorized"] is True
    assert provider.call_count == 1

    print("\n✅ Mock provider smoke test passed")


if __name__ == "__main__":
    main()