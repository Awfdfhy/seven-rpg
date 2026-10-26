# Seven RPG — UI Contract

**Directive:** frontend-design — aesthetic direction + implementation standards.  
**Directive:** ui-design-system — design tokens + component system.  
**Product:** Mobile-first Fantasy RPG  
**RTL:** Arabic primary, English secondary  
**Status:** Draft

---

## 1. Aesthetic Direction

| Attribute | Value |
|-----------|-------|
| Name | Fantasy Quest Premium |
| Tone | Editorial / Luxury (max 2 blended) |
| Differentiation Anchor | Gold-embossed typography + deep shadow realm background + translucent glass panels |
| DFII Score | 14 (Strong — proceed with discipline) |
| Primary Color | Amethyst (#d946ef) |
| Accent | Fantasy Gold (#d4af37) |
| Neutral | Slate-neutral (#171717 dark / #fafafa light) |
| Display Font | Rakkas / Amiri (Arabic display) |
| Body Font | Tajawal / Segoe UI (Arabic body) |

**Recognition test:** If logo removed, identifiable by gold amethyst gradient + shadow-realm depth + fantasy typography.

---

## 2. Screen Contracts

Each screen specifies: ID, states, RTL behavior, mobile breakpoints, acceptance criteria.

### SC-001 — Launch Screen

| Field | Value |
|-------|-------|
| Purpose | Entry point — new game or load save |
| States | idle, loading (app init), error (storage fail) |
| Layout | Centered logo, 2 buttons stacked vertically |
| Breakpoints | 375px (mobile), 768px (tablet) |
| RTL | Buttons full width, text-align right for Arabic |
| Acceptance | - Logo visible at 3s\n- "New Game" button navigates to WorldCreation\n- "Load Save" shows existing saves or empty state\n- No horizontal scroll\n- Arabic: "بدء لعبة جديدة" right-aligned |

**Visual Anchor:** Logo with gold glow animation (1500ms pulse).

### SC-002 — World Creation

| Field | Value |
|-------|-------|
| Purpose | Create new world with name |
| States | idle, input-focus, input-error, submitting, success, error |
| Fields | World name (text, required, max 30) |
| Buttons | Create World (primary), Cancel (ghost) |
| RTL | Input text-align right, placeholder right-aligned |
| Acceptance | - Empty name shows error "اسم العالم مطلوب"\n- 31+ chars shows error\n- Valid name creates world and navigates to CharacterCreation\n- Cancel returns to Launch |

### SC-003 — Character Creation

| Field | Value |
|-------|-------|
| Purpose | Create player character |
| States | idle, class-selected, submitting, success |
| Fields | Character name, Class select (Warrior/Mage/Rogue) |
| Avatar | Default class avatar (preview) |
| RTL | Form fields right-aligned, select arrow mirrors |
| Acceptance | - Class change updates avatar preview\n- Valid submission creates character and navigates to SceneEntry\n- Empty name blocks Create button |

### SC-004 — Scene Entry

| Field | Value |
|-------|-------|
| Purpose | Enter game scene |
| States | idle, narrative-loading, narrative-ready |
| Content | Scene description text, Enter button |
| RTL | Text direction auto (Arabic right, English left) |
| Acceptance | - Narrative text wraps correctly in Arabic\n- Enter button navigates to ActionSubmit\n- Loading state shows spinner |

### SC-005 — Action Submit

| Field | Value |
|-------|-------|
| Purpose | Submit player action |
| States | idle, input-focus, submitting, success, error |
| Fields | Action textarea (required) |
| Buttons | Execute (primary), Cancel (ghost) |
| Acceptance | - Empty action blocks Execute\n- Loading disables Execute\n- Success shows narrative response + applies events\n- Error shows toast with retry |

### SC-006 — Save Recover

| Field | Value |
|-------|-------|
| Purpose | Atomic save with recovery |
| States | saving, saved, corrupted, recovered |
| Feedback | Toast + status indicator |
| Acceptance | - Save completes in <2s\n- Force-stop/reopen restores identical state\n- Corrupted save shows recovery option\n- Arabic: "تم الحفظ بنجاح" / "فشل الحفظ" |

---

## 3. Component State Matrix

| Component | idle | loading | success | error | empty | offline | cancelled | stale |
|-----------|------|---------|---------|-------|-------|---------|-----------|-------|
| Button | default | spinner + disabled | check icon | red border | — | grayed | — | — |
| Input | normal | — | green border | red border + text | — | readonly | — | — |
| Card | normal | skeleton | — | — | illustration | — | — | — |
| List | normal | skeleton | — | — | empty illustration | — | — | — |
| Toast | — | — | green check | red exclamation | — | — | gray info | yellow warn |
| Page | content | spinner | content | error banner | empty state | offline banner | — | stale banner |

---

## 4. RTL / Arabic Requirements

| Requirement | Implementation |
|-------------|----------------|
| Default direction | `dir="rtl"` on html for Arabic |
| Text alignment | Arabic: right, English: left, auto-detect |
| Icon mirroring | Chevron-left → Chevron-right on RTL |
| Spacing mirror | margin-left ↔ margin-right, padding-left ↔ padding-right |
| Number localization | Arabic-Indic digits optional (user setting) |
| Date format | Hijri + Gregorian toggle |
| Font fallback | Tajawal → Segoe UI → system-ui |
| Mixed text | Arabic + English in same paragraph handled by Unicode |

---

## 5. Accessibility Contract

| Check | Requirement | Verification Method |
|-------|-------------|-------------------|
| Contrast ratio | ≥ 4.5:1 normal, ≥ 3:1 large | Color contrast analyzer |
| Touch target | ≥ 44×44px | Visual measurement |
| Focus ring | 2px solid primary-500 | Keyboard tab test |
| Screen reader | Labels on all buttons/inputs | VoiceOver / TalkBack |
| Reduced motion | Animations disabled | prefers-reduced-motion media query |
| Zoom | 200% without loss | Browser zoom test |
| Color not sole indicator | Icons + text for status | Grayscale test |

---

## 6. Performance Contract

| Metric | Target | Measurement |
|--------|--------|-------------|
| First paint | < 1.5s | Lighthouse / Chrome DevTools |
| Interactive | < 3s | Time to Interactive |
| Bundle size | < 2MB initial | Build output |
| Image format | WebP + AVIF | Network panel |
| Lazy loading | Below-fold images | Loading waterfall |

---

## 7. Visual Validation Plan (ui-visual-validator)

**Directive:** Default assumption: modification NOT achieved until proven visually.

### Phase 1 — Screenshot Capture
| Screen | Viewport | Theme | Direction | States |
|--------|----------|-------|-----------|--------|
| Launch | 375×812 | Light | RTL (ar) | idle |
| Launch | 375×812 | Dark | RTL (ar) | idle |
| WorldCreation | 375×812 | Light | RTL (ar) | idle, error |
| CharacterCreation | 375×812 | Light | LTR (en) | idle |
| SceneEntry | 375×812 | Light | RTL (ar) | narrative-loading |
| ActionSubmit | 375×812 | Light | RTL (ar) | submitting |

### Phase 2 — Visual Diff Detection
- Compare against design tokens (colors, spacing, typography)
- Verify no layout shift on hover/focus
- Verify RTL mirroring (icons, alignment)
- Verify dark mode consistency

### Phase 3 — Accessibility Visual Check
- Contrast ratios on all text/background pairs
- Focus ring visibility
- Touch target sizes
- Screen reader label presence

### Phase 4 — Edge Cases
- Long Arabic text overflow
- Empty state illustration
- Error state visibility
- Offline banner display
- Cancelled action fade-out

### Phase 5 — Sign-off Criteria
- [ ] All screenshots match design tokens
- [ ] RTL mirroring correct on all components
- [ ] Contrast ≥ 4.5:1 everywhere
- [ ] Touch targets ≥ 44×44px
- [ ] No horizontal scroll on mobile
- [ ] Loading/error/empty states visible
- [ ] Arabic text renders correctly (Tajawal font)

---

## 8. Implementation Standards (frontend-design)

- **Code:** Clean, modular, semantic HTML/CSS
- **No dead styles:** Every class used
- **No unused animations:** Only purposeful motion
- **CSS variables:** All colors/spacing from design tokens
- **Framework:** Default html-tailwind (mobile-first)
- **Animation:** CSS-first, 150-300ms duration, transform/opacity only
- **Icons:** SVG only (Heroicons/Lucide), no emojis

---

## 9. Anti-Patterns (Forbidden)

1. Emoji icons as UI elements
2. Hover states causing layout shift
3. Gray-400 body text
4. Content behind fixed navbar
5. Mixed container widths
6. Invisible borders in light mode
7. More than 2 aesthetic directions blended
8. Decorative micro-motion spam
9. Hardcoded values (no design tokens)
10. RTL not mirrored

---

## 10. Verification Statement

> From the visual evidence, I observe that the design system is defined in `design-tokens.json` and `component-system.md`. Implementation has NOT yet been visually verified — no screenshots captured, no RTL rendering tested, no contrast ratios measured. **Status: NOT ACHIEVED pending actual UI implementation and visual testing on mobile devices.**

**Next step:** Implement first screen (Launch) using html-tailwind + design tokens, then capture screenshots and run visual validation per Phase 1-5 above.
