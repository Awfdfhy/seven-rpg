# Seven RPG — Exact Verification Commands

**Status:** Ready — stack-agnostic placeholders  
**Directive:** codex-fable5 — verify before completion; evidence-first.  
**Note:** Replace placeholders with stack-specific commands after ADR-0001.

---

## Python (Mock Provider & Agent Tests — Runnable Now)

```bash
# Install dependencies
pip install -r requirements.txt

# Run mock provider smoke test
python tools/mock_provider.py

# Run MVP-0 acceptance tests
pytest tests/test_mvp0_smoke.py -v

# Run main MVP-0 smoke test
python main.py

# Lint
ruff check .

# Format check
ruff format --check .

# Type check
mypy .
```

---

## Stack-Specific (To Be Populated After ADR-0001)

| Stack | Build Command | Test Command | Lint Command | Package Command |
|-------|--------------|--------------|--------------|-----------------|
| Flutter | `flutter build apk` | `flutter test` | `flutter analyze` | `flutter build apk --release` |
| React Native | `npx react-native run-android` | `npm test` | `npm run lint` | `npx react-native run-android --variant=release` |
| Kotlin/Android | `./gradlew assembleDebug` | `./gradlew test` | `./gradlew detekt` | `./gradlew assembleRelease` |
| Swift/iOS | `xcodebuild -scheme SevenRPG build` | `xcodebuild test` | `swiftlint` | `xcodebuild -archive` |
| Python + Kivy | `python main.py` | `pytest` | `ruff check .` | `pyinstaller` |
| Tauri | `cargo tauri build` | `cargo test` | `cargo clippy` | `cargo tauri build` |

---

## Adversarial Acceptance Test Suite (MVP-0)

Run these after stack selection:

```
test_mvp0_happy_path              # launch → world → player → scene → action → validate → mock AI → events → save → recover
test_malformed_model_response     # empty/malformed model response must not mutate state
test_duplicate_submission_rejected # replayed event with stale revision must be rejected
test_unauthorized_mutation_rejected # proposal attempting unauthorized mutation must be rejected
test_step_count_guard             # step_count > 20 must route to end
```

---

## Failure Injection Tests (Required)

| Test | Expected Behavior |
|------|-------------------|
| Malformed or empty model response | No crash, state unchanged, error logged |
| Proposal attempts unauthorized state mutation | Rejected without mutation, error returned |
| Illegal action / insufficient resources | Rejected, player notified |
| Duplicate submission / replayed event | Rejected (idempotency), revision mismatch |
| User cancellation while request in flight | Request cancelled, stale response ignored |
| Late response arriving after cancellation | Ignored, no state mutation |
| Interrupted save / corrupted save | Recovery option shown, previous state preserved |
| Migration failure and recovery | Rollback to previous version, error reported |
| Offline launch and offline action | Queue actions, sync when online |
| World/campaign isolation | No cross-world data leakage |
| Arabic RTL / English LTR | Correct rendering in both directions |
| Mixed-direction text | No layout breakage |
| Long text | No overflow, proper wrapping |
| Keyboard navigation | Focus order matches visual order |

---

## Release Evidence Checklist (G9)

Before any release, record:
- [ ] Commit SHA
- [ ] Exact commands run
- [ ] Toolchain versions
- [ ] Test outcomes (all categories)
- [ ] Device/API level tested
- [ ] Screenshots/logs where relevant
- [ ] Artifact checksum
- [ ] Known gaps documented
- [ ] No credentials or secrets in bundle
- [ ] Owner approval obtained

---

## Immediate Next Step

**Your stack choice** → I will:
1. Populate STACK_SCORECARD.md with evidence
2. Build proof-of-concept spike
3. Complete ADR-0001
4. Implement domain contracts in your stack
5. Run MVP-0 adversarial tests
6. Proceed through G3-G9
