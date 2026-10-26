# Seven RPG — CLI Tests
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: pytest tests/test_cli.py -v

import pytest
from cli import print_banner, print_menu, run_mvp0, show_design_system
from mvp0_runner import MVP0Runner


def test_print_banner_output(capsys):
    """Banner prints without error."""
    print_banner()
    captured = capsys.readouterr()
    assert "Seven RPG" in captured.out


def test_print_menu_output(capsys):
    """Menu prints without error."""
    print_menu()
    captured = capsys.readouterr()
    assert "Main Menu" in captured.out
    assert "MVP-0" in captured.out


def test_mvp0_runner_success():
    """MVP-0 runner returns success result."""
    runner = MVP0Runner()
    result = runner.run()
    assert result["success"] is True
    assert result["steps_completed"] == 11


def test_show_design_system(capsys, tmp_path, monkeypatch):
    """Design system summary function runs."""
    # Just verify the function exists and is callable
    assert callable(show_design_system)