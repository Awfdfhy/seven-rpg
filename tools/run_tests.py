# Seven RPG — Stdlib Test Runner (بدون pytest)
# Directive: codex-fable5 — verify before completion; evidence-first.
# Runs all tests using Python standard library only.
# Run: python tools/run_tests.py

import ast
import importlib.util
import inspect
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


class TestResult:
    """Result of a single test."""

    def __init__(self, name: str, passed: bool, error: Optional[str] = None, duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.error = error
        self.duration = duration


class StdlibTestRunner:
    """Simple test runner using Python standard library (unittest-compatible discovery)."""

    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.results: List[TestResult] = []
        self.total = 0
        self.passed = 0
        self.failed = 0

    def discover_test_files(self) -> List[Path]:
        """Discover all test_*.py files in the test directory."""
        if not self.test_dir.exists():
            return []
        return sorted(self.test_dir.glob("test_*.py"))

    def load_test_module(self, file_path: Path) -> Any:
        """Load a test module from file path."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load {file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_test_functions(self, module: Any) -> List[Tuple[str, Callable]]:
        """Get all test_* functions from a module."""
        tests = []
        for name in dir(module):
            if name.startswith("test_") and callable(getattr(module, name)):
                tests.append((name, getattr(module, name)))
        return tests

    def run_test(self, name: str, func: Callable) -> TestResult:
        """Run a single test function and return result."""
        start = time.perf_counter()
        try:
            func()
            duration = time.perf_counter() - start
            return TestResult(name=name, passed=True, duration=duration)
        except Exception as exc:  # noqa: BLE001
            duration = time.perf_counter() - start
            return TestResult(name=name, passed=False, error=str(exc), duration=duration)

    def run_all(self) -> Dict[str, Any]:
        """Run all discovered tests."""
        test_files = self.discover_test_files()

        if not test_files:
            print("⚠️  No test files found.")
            return {"total": 0, "passed": 0, "failed": 0, "results": []}

        print(f"\n🧪  Seven RPG — Stdlib Test Runner")
        print(f"   Test directory: {self.test_dir}")
        print(f"   Test files found: {len(test_files)}")
        print("=" * 60)

        for test_file in test_files:
            print(f"\n📄  {test_file.name}")
            try:
                module = self.load_test_module(test_file)
                test_functions = self.get_test_functions(module)

                if not test_functions:
                    print("   ⚠️  No test functions found.")
                    continue

                for name, func in test_functions:
                    self.total += 1
                    result = self.run_test(name, func)
                    self.results.append(result)

                    if result.passed:
                        self.passed += 1
                        print(f"   ✅  {name} ({result.duration:.3f}s)")
                    else:
                        self.failed += 1
                        print(f"   ❌  {name} — {result.error}")

            except Exception as exc:  # noqa: BLE001
                print(f"   ❌  Failed to load module: {exc}")

        # Summary
        print("\n" + "=" * 60)
        print(f"   Total:  {self.total}")
        print(f"   Passed: {self.passed}")
        print(f"   Failed: {self.failed}")
        print("=" * 60)

        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "error": r.error,
                    "duration": r.duration,
                }
                for r in self.results
            ],
        }


def main() -> int:
    runner = StdlibTestRunner()
    result = runner.run_all()
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())