# Seven RPG — Deployment Checklist (G8-G9)

**Status:** Ready — stack-agnostic  
**Directive:** codex-fable5 — verify before completion; evidence-first.  
**Note:** Complete after ADR-0001 stack selection and MVP-0 implementation.

---

## Pre-Deployment (G8 — Android Readiness)

### Device & API Level
- [ ] Supported API levels documented (e.g., Android API 24+)
- [ ] Device assumptions recorded (low/mid-range, screen sizes)
- [ ] Emulator testing completed on supported API levels
- [ ] Physical device testing completed (if available)

### Build & Packaging
- [ ] Reproducible build confirmed (same source → same artifact)
- [ ] Build commands documented and repeatable
- [ ] Artifact checksum recorded (SHA-256)
- [ ] Signing configuration prepared (keys NOT in source control)
- [ ] App size within target (documented)

### Storage & Permissions
- [ ] Storage/document-provider behavior tested
- [ ] Permission requests handled (storage, etc.)
- [ ] Save/export/import tested
- [ ] Backup/restore tested

### Lifecycle
- [ ] Install/upgrade/reinstall tested
- [ ] Force-stop/reopen recovery tested
- [ ] Back navigation handled
- [ ] Network transitions tested (online/offline)

---

## Deployment Gate (G9 — Release Candidate)

### Automated Suite
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All UI tests pass
- [ ] Adversarial acceptance tests pass (MVP-0 failure cases)
- [ ] Test coverage meets threshold

### Security Scan
- [ ] Dependency vulnerability scan (no critical/high CVEs)
- [ ] License compliance checked (no copyleft surprises)
- [ ] Secret scanning — no API keys/tokens in source
- [ ] Code scan — no hardcoded credentials

### Accessibility & RTL
- [ ] WCAG AA contrast verified (≥ 4.5:1 normal, ≥ 3:1 large)
- [ ] Arabic RTL layout verified
- [ ] English LTR layout verified
- [ ] Mixed-direction text tested
- [ ] Screen reader labels present
- [ ] Focus rings visible
- [ ] Touch targets ≥ 44×44px

### Release Evidence
- [ ] Commit SHA recorded
- [ ] Exact build commands recorded
- [ ] Toolchain versions documented
- [ ] Test outcomes documented (all categories)
- [ ] Device/API level documented
- [ ] Screenshots/logs captured
- [ ] Artifact checksum recorded (SHA-256)
- [ ] Known gaps documented

### Approval
- [ ] Owner approval obtained for release
- [ ] No merge to main without approval
- [ ] No repository visibility change without approval
- [ ] No paid usage incurred without approval

---

## Post-Deployment

- [ ] Release monitored for crashes/errors
- [ ] User feedback collected
- [ ] Crash reports analyzed
- [ ] Next release planned

---

## Blocker Note

This checklist cannot be executed until:
1. Stack selected (ADR-0001)
2. MVP-0 implemented (G4)
3. Tests passing (G4-G5)

**Current status: G2 blocked — awaiting stack selection.**
