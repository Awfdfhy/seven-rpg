# Seven RPG — Visual Validation Plan

**Directive:** ui-visual-validator — default assumption: modification NOT achieved until proven visually.  
**Scope:** Launch screen + design tokens + RTL + mobile breakpoints  
**Status:** Ready for execution

---

## 1. Validation Principles

- **Default assumption:** The design has NOT been implemented correctly until visual evidence proves it.
- **Be highly critical:** Look for flaws, inconsistencies, incomplete implementations.
- **Ignore code hints:** Base judgments solely on visual evidence (screenshots).
- **Accessibility first:** WCAG 2.2 AA contrast, focus rings, touch targets, reduced motion.
- **RTL first:** Arabic direction must be mirrored correctly (icons, alignment, spacing).

---

## 2. Screens to Validate

| Screen | Viewport | Theme | Direction | States to Capture |
|--------|----------|-------|-----------|-------------------|
| Launch | 375×812 (iPhone SE) | Light | RTL (ar) | idle, loading, error |
| Launch | 375×812 | Dark | RTL (ar) | idle |
| Launch | 768×1024 (iPad) | Light | RTL (ar) | idle |
| Launch | 375×812 | Light | LTR (en) | idle |
| WorldCreation | 375×812 | Light | RTL (ar) | idle, input-error |
| CharacterCreation | 375×812 | Light | RTL (ar) | idle |
| SceneEntry | 375×812 | Light | RTL (ar) | narrative-loading |
| ActionSubmit | 375×812 | Light | RTL (ar) | submitting, success |

---

## 3. Visual Checks per Screen

### Launch Screen

| Check | Expected | Pass/Fail | Evidence |
|-------|----------|-----------|----------|
| Logo visible with "Seven RPG" text | Yes | | Screenshot |
| Logo has gold pulse animation | Yes | | Video / animation check |
| Two buttons stacked vertically | Yes | | Screenshot |
| Buttons full width on mobile | Yes | | Measurement |
| Button height ≥ 44px | Yes | | Visual measurement |
| Primary button: amethyst background | Yes | | Color picker |
| Ghost button: transparent with amethyst border | Yes | | Color picker |
| Focus ring visible on keyboard tab | 2px solid primary-500 | | Keyboard test |
| Arabic text right-aligned | Yes | | Screenshot |
| No horizontal scroll | Yes | | Overflow check |
| Loading spinner centered | Yes | | State test |
| Error text red (#ef4444) | Yes | | State test |
| Dark mode: background dark, text light | Yes | | Theme switch |
| Reduced motion: animations disabled | Yes | | prefers-reduced-motion |

### WorldCreation Screen

| Check | Expected | Pass/Fail | Evidence |
|-------|----------|-----------|----------|
| World name input right-aligned (RTL) | Yes | | Screenshot |
| Input border: neutral-300 light / neutral-700 dark | Yes | | Color check |
| Focus state: primary-500 border | Yes | | Keyboard test |
| Empty submission shows error in red | Yes | | State test |
| Error text below input | Yes | | Screenshot |
| Create button disabled when empty | Yes | | Interaction test |

### CharacterCreation Screen

| Check | Expected | Pass/Fail | Evidence |
|-------|----------|-----------|----------|
| Class select arrow mirrors on RTL | Yes | | Screenshot |
| Avatar preview updates on class change | Yes | | Interaction test |
| Character name input right-aligned | Yes | | Screenshot |

---

## 4. Accessibility Visual Checks

| Check | WCAG Requirement | Target | Method |
|-------|-----------------|--------|--------|
| Color contrast (normal text) | ≥ 4.5:1 | primary-500 on neutral-50 | Contrast analyzer |
| Color contrast (large text) | ≥ 3:1 | headings | Contrast analyzer |
| Touch target size | ≥ 44×44px | All buttons | Visual measurement |
| Focus indicator | Visible | 2px solid primary-500 | Keyboard navigation |
| Screen reader labels | Present | All buttons/inputs | VoiceOver / TalkBack |
| Reduced motion | Respected | Animation disabled | prefers-reduced-motion |
| Color not sole indicator | Icons + text | Error/success states | Grayscale test |
| Text resize 200% | No loss | Layout intact | Browser zoom |

---

## 5. RTL-Specific Checks

| Check | Expected | Method |
|-------|----------|--------|
| Direction attribute | `dir="rtl"` on html | HTML inspection |
| Text alignment | Arabic right, English left | Screenshot |
| Icon mirroring | Chevron-left → Chevron-right | Icon inspection |
| Spacing mirror | margin-left ↔ margin-right | Computed styles |
| Mixed direction | Arabic + English in same line | Unicode rendering test |
| Font fallback | Tajawal → Segoe UI | Font stack verification |

---

## 6. Evidence Output Format

For each validation session, produce:

```
## Visual Validation Report — {Screen}
**Date:** {date}
**Viewport:** {viewport}
**Theme:** {light|dark}
**Direction:** {rtl|ltr}
**State:** {idle|loading|error|...}

### Observations
From the visual evidence, I observe:
- {objective description of what is seen}
- {measurements where relevant}

### Pass/Fail
| Check | Result | Evidence |
|-------|--------|----------|
| {check} | PASS/FAIL | {screenshot ref} |

### Issues Found
1. {issue} — {severity} — {remediation}
2. {issue} — {severity} — {remediation}

### Sign-off
- [ ] All critical checks passed
- [ ] RTL verified
- [ ] Accessibility verified
- [ ] Ready for implementation handoff
```

---

## 7. Tools (recommended)

| Tool | Purpose |
|------|---------|
| Chrome DevTools | Color picker, computed styles, responsiveness |
| Lighthouse | Accessibility audit, contrast |
| VoiceOver (iOS) / TalkBack (Android) | Screen reader testing |
| Browser zoom (200%) | Text resize test |
| prefers-reduced-motion toggle | Motion accessibility |
| Screenshot comparison | Visual regression (future: Chromatic / Percy) |

---

## 8. Sign-off Criteria (Gate G7 — UI Convergence)

Before any screen is marked complete:

- [ ] Screenshot captured at 375px mobile
- [ ] RTL direction verified (Arabic)
- [ ] Contrast ≥ 4.5:1 normal text
- [ ] Touch targets ≥ 44×44px
- [ ] Focus ring visible
- [ ] Loading/error/empty states tested
- [ ] No horizontal scroll
- [ ] Dark mode consistent
- [ ] Reduced motion respected
- [ ] Visual validation report written

**Directive:** ui-visual-validator — Never declare success without concrete visual evidence. A screenshot is not evidence that underlying behavior works — it is evidence that the screen *renders*. Behavior must be verified separately via tests (`tests/test_mvp0_smoke.py`).
