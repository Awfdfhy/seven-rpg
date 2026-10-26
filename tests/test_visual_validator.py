# Seven RPG — Visual Validator Tests
# Directive: ui-visual-validator — verify before completion; evidence-first.
# Run: pytest tests/test_visual_validator.py -v

import pytest
from tools.visual_validator import VisualValidator


def test_validator_loads_tokens():
    """Validator loads design tokens successfully."""
    validator = VisualValidator()
    assert validator.load_tokens() is True
    assert validator.tokens != {}


def test_validator_checks_rtl():
    """Validator checks RTL configuration."""
    validator = VisualValidator()
    validator.load_tokens()
    validator.validate_rtl_support()
    # Should have at least one RTL pass
    rtl_passed = [c for c in validator.passed if "RTL" in c]
    assert len(rtl_passed) >= 1


def test_validator_checks_touch_targets():
    """Validator checks touch targets."""
    validator = VisualValidator()
    validator.load_tokens()
    validator.validate_touch_targets()
    touch_passed = [c for c in validator.passed if "Touch target" in c or "Button height" in c]
    assert len(touch_passed) >= 1


def test_validator_checks_accessibility():
    """Validator checks accessibility settings."""
    validator = VisualValidator()
    validator.load_tokens()
    validator.validate_accessibility()
    a11y_passed = [c for c in validator.passed if "Accessibility" in c]
    assert len(a11y_passed) >= 1


def test_validator_checks_html_prototypes():
    """Validator checks HTML prototypes exist."""
    validator = VisualValidator()
    validator.load_tokens()
    validator.validate_html_prototypes()
    proto_passed = [c for c in validator.passed if "UI Prototype" in c]
    assert len(proto_passed) >= 1


def test_validator_no_emoji_icons():
    """Validator checks no emoji icons in prototypes."""
    validator = VisualValidator()
    validator.load_tokens()
    validator.validate_no_emoji_icons()
    # Should pass for all prototypes (no emoji icons in our HTML)
    emoji_warnings = [w for w in validator.warnings if "emoji" in w.lower()]
    assert len(emoji_warnings) == 0


def test_validator_overall_result():
    """Validator returns overall result."""
    validator = VisualValidator()
    result = validator.run()
    assert "passed" in result
    assert "errors" in result
    assert "warnings" in result
    assert "passed_checks" in result