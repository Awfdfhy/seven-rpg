# Seven RPG — pytest configuration
# Directive: codex-fable5 — deterministic mock provider for tests; real providers replaceable.

import pytest


@pytest.fixture
def mock_ai_provider():
    """Deterministic mock AI provider for tests."""
    def generate_proposal(goal: str, revision: int) -> dict:
        return {
            "type": "narrative_response",
            "prose": f"Mock response to: {goal[:50]}",
            "events": [{"id": f"evt_{rev}_1", "type": "narrative_advance", "revision_base": revision, "authorized": True}],
            "attempts_unauthorized_mutation": False,
        }
    return generate_proposal