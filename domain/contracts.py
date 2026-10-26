# Seven RPG — Domain Contracts (Stack-Agnostic)
# Directive: multi-agent-architect — validation results, proposals, AI provider interface.

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
import uuid


@dataclass
class ValidationResult:
    """Result of validating a command or proposal."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_at: str = field(default_factory=lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "validated_at": self.validated_at,
        }


@dataclass
class Proposal:
    """AI proposal — untrusted output, never mutates state directly."""
    type: str
    prose: str                    # narrative text only — not authoritative state
    events: list = field(default_factory=list)
    attempts_unauthorized_mutation: bool = False
    revision_base: int = 1
    provider: str = "mock"
    call_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "prose": self.prose,
            "events": self.events,
            "attempts_unauthorized_mutation": self.attempts_unauthorized_mutation,
            "revision_base": self.revision_base,
            "provider": self.provider,
            "call_id": self.call_id,
        }


class AIProviderInterface(Protocol):
    """Interface for AI providers — replaceable, declares capabilities."""

    def generate_narrative(self, goal: str, context: dict, revision: int) -> Proposal:
        """Generate a narrative proposal from player goal and context."""
        ...

    def cancel(self, call_id: str) -> bool:
        """Cancel an in-flight request."""
        ...

    def declare_capabilities(self) -> dict:
        """Declare supported features for contract validation."""
        ...


@dataclass
class AIProviderCapabilities:
    """Declared capabilities of an AI provider."""
    provider: str
    streaming: bool = False
    cancellation: bool = True
    structured_output: bool = True
    timeout_support: bool = True
    retry_support: bool = True
    max_revision_base: int = 1000000