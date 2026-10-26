# Seven RPG — Component System

**Directive:** ui-design-system Workflow 2 — Atomic design hierarchy mapped to design tokens.  
**Product:** Mobile-first Fantasy RPG  
**RTL:** Arabic first-class (rtl: true, default direction rtl)  
**Status:** Draft — pre-implementation

---

## Component Hierarchy

| Level | Components | Purpose |
|-------|-----------|---------|
| **Atoms** | Button, Input, Icon, Label, Badge, Avatar, Divider, Spinner, ProgressBar | Basic building blocks |
| **Molecules** | FormField, SearchBar, Card, ListItem, NavigationItem, DialogHeader, StatChip | Combined atoms |
| **Organisms** | Header, BottomNav, WorldMapPanel, CharacterSheet, InventoryGrid, CombatLog, QuestList | Screen sections |
| **Templates** | WorldView, CharacterView, InventoryView, CombatView, SettingsView | Full screen layouts |
| **Pages** | Launch, WorldCreation, CharacterCreation, SceneEntry, ActionSubmit, SaveRecover | Complete user journeys |

---

## Atom Specifications

### Button
| Variant | Background | Text | Border | Shadow | Size | Touch Target |
|---------|-----------|------|--------|--------|------|--------------|
| primary | primary-500 | white | none | md | md (52px) | 44×44 min |
| secondary | neutral-100 | neutral-900 | none | sm | md | 44×44 min |
| ghost | transparent | primary-600 | none | none | md | 44×44 min |
| danger | error-500 | white | none | md | md | 44×44 min |
| fantasy-gold | gold (#d4af37) | neutral-900 | none | fantasy-glow | lg | 44×44 min |

**States:** hover, active, focus, disabled, loading  
**Focus:** 2px solid primary-500, offset 2px  
**RTL:** Icon mirrors on RTL (arrow-left → arrow-right)

### Input
| Variant | Background | Border | Text | Size |
|---------|-----------|--------|------|------|
| default | surface.panel | borders.color.light | neutral-900 | md (52px) |
| focused | surface.panel | borders.color.primary | neutral-900 | md |
| error | surface.panel | semantic.error | neutral-900 | md |
| disabled | neutral-200 | borders.color.light | neutral-400 | md |

**Label:** Above input, font-size sm, font-weight medium  
**Error text:** Below input, font-size xs, color semantic.error  
**RTL:** Text-align right, icon mirrors

### Icon
| Size | Value | Use Case |
|------|-------|----------|
| sm | 16px | List items, badges |
| md | 24px | Buttons, navigation |
| lg | 32px | Headers, cards |

**Source:** SVG only (Heroicons / Lucide) — no emoji icons  
**RTL:** Mirror directional icons (chevron, arrow, back)

### Avatar
| Size | Value | Use Case |
|------|-------|----------|
| sm | 32px | List items, chat |
| md | 48px | Header, profile |
| lg | 64px | Character sheet, world card |

**Shape:** Circle (border-radius full)  
**Border:** 2px borders.color.primary when selected  
**Fallback:** First letter of name, font-weight bold

---

## Molecule Specifications

### FormField
- Label + Input + Error text + Helper text
- Spacing: space-3 between label and input, space-2 between input and error
- Full width on mobile (container-sm)
- RTL: Label text-align right

### Card
- Background: surface.panel
- Border: 1px borders.color.light
- Radius: borders.radius.lg
- Shadow: shadows.md
- Padding: space-6
- Hover: shadow-lg, transform translate-y(-2px) — **no layout shift**

### ListItem
- Background: surface.panel on hover (neutral-50 light / neutral-900 dark)
- Padding: space-4 horizontal, space-3 vertical
- Border-bottom: 1px borders.color.light
- Avatar left, text center, action icon right (RTL: reversed)
- Touch target: full height, min 44px

### NavigationItem
- Icon + Label
- Active state: primary-500 text + bg primary-50
- Inactive: neutral-600 text
- Bottom nav height: 80px (safe area included)

---

## Organism Specifications

### Header (Top Bar)
- Height: 56px
- Background: surface.panel with glass effect
- Back button left, title center, menu right (RTL: reversed)
- Z-index: zIndex.sticky

### BottomNav
- Height: 80px (including safe area bottom)
- Background: surface.panel
- Border-top: 1px borders.color.light
- 3-5 items max
- Active item: primary-500 + fantasy-gold glow

### WorldMapPanel
- Background: surface.panel
- Map preview image (lazy loaded)
- World name header (typography.display)
- Action buttons: Enter, Settings, Export
- Shadow: shadows.lg

### CharacterSheet
- Avatar (lg)
- Name (typography.2xl, fontFamily.display)
- Attributes grid (health, mana, strength, agility, intelligence)
- Inventory summary (item count, weight)
- Level badge (fantasy-gold background)

### InventoryGrid
- Grid: 3 columns on mobile, 5 on tablet, 7 on desktop
- Item card: icon + name + quantity badge
- Empty state: illustration + text "لا توجد عناصر" / "No items"

### CombatLog
- Scrollable list (max height 200px)
- Message bubbles: player (right, primary-50), system (left, neutral-100)
- Timestamp (typography.xs, neutral-500)
- Auto-scroll to bottom on new message

---

## Template Specifications

### WorldView (Main Game Screen)
```
[Header]
[WorldMapPanel — 40% height]
[CharacterSheet — bottom sheet, collapsible]
[BottomNav — World / Inventory / Quests / Settings]
```

### CharacterView
```
[Header — Back]
[Avatar lg — center top]
[Name — typography.4xl, fontFamily.display]
[Attributes Grid — 2 columns]
[InventoryGrid — scrollable]
[Quests — list]
[Floating Action Button — Edit Character]
```

### InventoryView
```
[Header — Back + Search]
[Empty state or Grid]
[Item detail bottom sheet on tap]
```

### CombatView
```
[Header — Enemy name + health bar]
[CombatLog — top 30%]
[Character status — bottom 20%]
[Action buttons — Attack / Skill / Item / Flee]
```

---

## Page Specifications (MVP-0)

### Launch
- Logo center (typography.6xl, fontFamily.display, fantasy-gold)
- Button primary: "بدء لعبة جديدة" / "New Game"
- Button ghost: "تحميل حفظ" / "Load Save"
- Background: subtle gradient neutral-50 to neutral-100

### WorldCreation
- Input: World name (required, max 30 chars)
- Button primary: "إنشاء العالم" / "Create World"
- Error: "اسم العالم مطلوب" / "World name required"

### CharacterCreation
- Input: Character name
- Select: Class (Warrior / Mage / Rogue)
- Button primary: "إنشاء الشخصية" / "Create Character"

### SceneEntry
- Scene description text (typography.lg, fontFamily.body)
- Button primary: "دخول المشهد" / "Enter Scene"

### ActionSubmit
- Textarea: Action input (required)
- Button primary: "تنفيذ" / "Execute"
- Button ghost: "إلغاء" / "Cancel"
- Loading state on submit

### SaveRecover
- Toast: "تم الحفظ بنجاح" / "Saved successfully"
- Error toast: "فشل الحفظ" / "Save failed"

---

## State Handling (All Async Flows)

Every interactive component must document:

| State | Visual | Behavior |
|-------|--------|----------|
| idle | Default styling | Ready for interaction |
| loading | Spinner + disabled buttons | No double-submit |
| success | Green check + toast | Auto-dismiss 3s |
| error | Red border + error text | Retry action available |
| empty | Illustration + help text | Clear call-to-action |
| offline | Grayed out + offline banner | Queue actions |
| cancelled | Fade out + "تم الإلغاء" / "Cancelled" | Restore previous state |
| stale | Warning toast | Ignore late response |

---

## Dark Mode / Light Mode

| Token | Light | Dark |
|-------|-------|------|
| background | neutral-50 | neutral-900 |
| surface | surface.panel-light | surface.panel-dark |
| text-primary | neutral-900 | neutral-50 |
| text-secondary | neutral-600 | neutral-400 |
| border | borders.color.light | borders.color.dark |
| shadow | shadows.md | shadows.xl |

**Auto:** Respects `prefers-color-scheme` with manual toggle override.

---

## Accessibility Checklist (RTL + Mobile)

- [ ] Color contrast ≥ 4.5:1 normal text, 3:1 large text (WCAG AA)
- [ ] Touch targets ≥ 44×44px
- [ ] Focus rings visible (2px solid primary-500)
- [ ] Arabic RTL layout mirrored correctly
- [ ] Mixed-direction text (Arabic + English) handled
- [ ] Keyboard navigation order matches visual order
- [ ] Screen reader labels on all interactive elements
- [ ] `prefers-reduced-motion` respected (animations disabled)
- [ ] Minimum font size 16px body text on mobile
- [ ] No horizontal scroll on 375px viewport
- [ ] Loading/error/empty states on all async components
- [ ] No emoji icons — SVG only

---

## Anti-Patterns to Avoid

1. Emoji icons instead of SVG
2. Hover states causing layout shift
3. Gray-400 body text (insufficient contrast)
4. Content hidden behind fixed navbar
5. Mixed container widths across screens
6. Invisible borders in light mode
7. More than two aesthetic directions blended
8. Decorative micro-motion spam
9. Hardcoded values instead of design tokens
10. RTL not mirrored (icons, alignment, spacing)
