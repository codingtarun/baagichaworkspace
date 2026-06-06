# Baagicha — Complete Design Specification

> **Architecture:** APIs live in Laravel (`web_baagicha/`). React Native (`baagichaApp/`) is the pure frontend client.
> **Updated:** 2026-06-06 — merged prediction engine + kisan tools + segmented home + new nav
> Source: Laravel web frontend + prediction engine research + mobile implementation

---

## 1. Project Overview

**Baagicha** (बागीचा) is a farmer-focused mobile app for Himalayan apple growers in HP, UK, and J&K. It provides spray schedules, disease/pest libraries with **prediction engine** alerts, weather forecasts with spray suitability, variety & rootstock guides, community disease reporting, a blog/knowledge base, **26 kisan tool calculators**, and an eCommerce shop.

**Web Stack:** Laravel + Blade + Custom CSS (mobile-first PWA)  
**Mobile Target:** React Native 0.85 (bare, CLI-bootstrapped)

---

## 2. Color Scheme

| Token | Hex | Usage |
|-------|-----|-------|
| `bgPrimary` | `#1a2e1a` | Dark green header bg |
| `bgSecondary` | `#2d4a2d` | Secondary dark green |
| `primary` | `#3a7d44` | Primary green (buttons, active states) |
| `primaryLight` | `#52a85f` | Light green |
| `accent` | `#e8b84b` | Gold/amber accent |
| `accentLight` | `#f5d07a` | Light gold |
| `gray50` | `#f8fafc` | Page background |
| `gray100` | `#f1f5f9` | Card backgrounds |
| `gray200` | `#e2e8f0` | Borders |
| `gray400` | `#94a3b8` | Secondary text |
| `gray500` | `#64748b` | Muted text |
| `gray600` | `#475569` | Body text |
| `gray700` | `#334155` | Headings |
| `gray800` | `#1e293b` | Dark text |
| `gray900` | `#0f172a` | Almost black |
| `success` | `#22c55e` | Success/good |
| `warning` | `#f59e0b` | Warning/caution |
| `danger` | `#ef4444` | Error/critical |
| `info` | `#3b82f6` | Info blue |

**Priority Colors:**
- Essential: `#dc2626` (red)
- Recommended: `#f59e0b` (amber)
- Conditional: `#60a5fa` (blue)

**Severity Colors (General):**
- Critical: `#dc2626`
- High: `#f97316`
- Medium: `#f59e0b`
- Low: `#22c55e`

**Prediction Engine — Risk Level Colors:**

| Level | Background | Text | Icon |
|-------|-----------|------|------|
| `critical` | `#DC2626` | white | 🚨 |
| `high` | `#EA580C` | white | ⚠️ |
| `medium` | `#D97706` | white | 👁️ |
| `low` | `#65A30D` | white | ℹ️ |
| `none` | `#6B7280` | white | ✅ |

---

## 3. Typography

| Purpose | Font | Fallback |
|---------|------|----------|
| Display/Headings | DM Serif Display | Georgia, serif |
| Body | DM Sans | system-ui, sans-serif |
| Hindi | Noto Sans Devanagari | DM Sans |
| Hindi Display | Yatra One | Noto Sans Devanagari |

**Font Sizes (mobile dp):**
- Hero title: `23` (1.45rem)
- Section headers: `20` (1.25rem)
- Sub-headings: `17` (1.05rem)
- Card titles: `15` (0.95rem)
- Body: `14` (0.82–0.88rem)
- Body small: `13` (0.76–0.8rem)
- Caption: `12` (0.72rem)
- Small (badges/pills): `11` (0.6–0.68rem)
- Micro (nav Hindi): `9` (0.5–0.55rem)

---

## 4. Layout Structure

```
┌─────────────────────────┐
│  App Header (sticky)    │  ← Dark gradient, greeting, location chip,
│  · Greeting             │     weather widget, stat pills
│  · Location Chip        │
│  · Weather Widget       │
│  · 3 Stat Pills         │
├─────────────────────────┤
│  Segmented Control      │  ← "My Farm" / "Community" toggle (Home)
├─────────────────────────┤
│                         │
│  Main Content (scroll)  │  ← White bg (#f8fafc), 16px padding
│                         │
├─────────────────────────┤
│  App Footer             │  ← Minimal copyright + socials
├─────────────────────────┤
│  Bottom Navigation      │  ← Fixed, glassmorphism, 5 tabs
└─────────────────────────┘
```

**Header Behavior:** On scroll > 50px, compact mode shrinks header (hides stats, reduces padding & font sizes).

**App Container:** `max-width: 428px`, `100dvh`, centered on desktop, full-width on actual phones.

---

## 5. Shadows

| Token | Value |
|-------|-------|
| `shadowXs` | `0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.02)` |
| `shadowSm` | `0 1px 2px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.04)` |
| `shadowMd` | `0 2px 4px rgba(0,0,0,0.04), 0 8px 20px rgba(0,0,0,0.06)` |
| `shadowLg` | `0 4px 8px rgba(0,0,0,0.04), 0 12px 32px rgba(0,0,0,0.08)` |
| `shadowXl` | `0 8px 16px rgba(0,0,0,0.06), 0 24px 48px rgba(0,0,0,0.1)` |
| `shadowPrimary` | `0 4px 14px rgba(58,125,68,0.15)` |
| `shadowAccent` | `0 4px 14px rgba(232,184,75,0.2)` |

---

## 6. Border Radius

| Token | Value |
|-------|-------|
| `radiusSm` | `8px` |
| `radiusMd` | `16px` |
| `radiusLg` | `24px` |
| `radiusXl` | `32px` |
| `radiusFull` | `999px` |

---

## 7. Spacing

| Token | Value |
|-------|-------|
| `spaceXs` | `4px` |
| `spaceSm` | `8px` |
| `spaceMd` | `16px` |
| `spaceLg` | `24px` |
| `spaceXl` | `32px` |

---

## 8. Transitions

| Token | Value |
|-------|-------|
| `transitionFast` | `150ms cubic-bezier(0.2, 0, 0, 1)` |
| `transitionBase` | `250ms cubic-bezier(0.2, 0, 0, 1)` |
| `transitionSlow` | `350ms cubic-bezier(0.2, 0, 0, 1)` |
| `transitionSpring` | `400ms cubic-bezier(0.34, 1.56, 0.64, 1)` |
| `transitionBounce` | `500ms cubic-bezier(0.175, 0.885, 0.32, 1.275)` |

---

## 9. Interactions & Animations

| Interaction | Behavior |
|-------------|----------|
| **Scroll** | Header compacts after 50px scroll |
| **Haptic** | 8-10ms vibration on all buttons/taps |
| **Press** | `transform: scale(0.97)` on cards, `scale(0.92)` on nav items |
| **Toast** | Android-style snackbar from bottom (success, saved, liked, error) |
| **Dropdowns** | Backdrop overlay, close on outside tap or Escape |
| **Task Done/Pin** | Toggle icon regular/solid, persist to localStorage |
| **Like/Save** | POST to `/actions/like` or `/actions/save`, toggle state |
| **Nav Active** | Pill background, larger icon |
| **Stagger Load** | Cards animate in with `slideUp` + delay |

---

## 10. Segmented Control Pattern

Used on **HomeScreen** to switch between "My Farm" and "Community" views.

```
┌─────────────────────────────────┐
│  [🌱 My Farm]  [💬 Community]   │  ← pill selector, active = green fill
└─────────────────────────────────┘
```

- Inactive: transparent bg, gray text
- Active: `primary` (#3a7d44) bg, white text, `radiusFull`
- Switch triggers content swap with no nav stack change
- On focus, segment resets to "My Farm"

---

## 11. Dashboard Card Pattern (My Farm Segment)

Compact cards used in the dashboard segment:

```
┌──────────────────────────────┐
│  🍎 Stage Hero Card          │  ← full width, dark gradient bg
│  Dormancy Break / Green Tip   │
│  सुप्तावस्था / हरी कली       │
│  [==========>    ] 65%       │
│  Mar 1 – Mar 20              │
│  ☀️ Spray: Good to Spray     │
└──────────────────────────────┘

┌──────────┐ ┌──────────┐
│  ☁️      │ │  ☀️      │  ← stat mini-cards (2-col)
│  18°C    │ │  Good    │
│  Shimla  │ │  Spray   │
└──────────┘ └──────────┘

┌──────────────────────────────┐
│  🔴 Apple Scab — HIGH Risk   │  ← alert card (prediction engine)
│  Rain tomorrow. Spray by 10AM│
│  [View] [✅ I Sprayed]       │
└──────────────────────────────┘

┌──────────────────────────────┐
│  📅 Weekly Tasks             │  ← collapsible section
│  ✓ Copper Oxychloride        │
│  ○ Mancozeb 75WP             │
└──────────────────────────────┘
```

---

## 12. Header Component (Inner Pages)

Slim header with:
- Brand link "Baagicha" with seedling icon
- Orchard weather button (dropdown) — shows temp circle + orchard name + condition
- Notification bell (badge + dropdown)
- Profile button (dropdown with menu)

**Orchard Dropdown:**
- Active orchard summary
- List of orchards (selectable)
- Device GPS option
- Footer: Manage Orchards · Forecast

**Profile Dropdown Menu:**
- My Profile
- My Orchards
- Orchard Diary
- Saved Items
- Disease Reports
- Notification Settings
- Log out

---

## 13. Bottom Navigation (5 Tabs)

| Route | Label (EN) | Label (HI) | Icon (RN) |
|-------|-----------|-----------|-----------|
| `Home` | Home | होम | `home` (MaterialCommunityIcons) |
| `Spray` | Spray | स्प्रे | `spray-bottle` (MaterialCommunityIcons) |
| `Shop` | Shop | दुकान | `store` (MaterialCommunityIcons) |
| `Discover` | Discover | खोजें | `compass` (MaterialCommunityIcons) |
| `MyOrchard` | My Orchard | मेरा बाग | `tree` (MaterialCommunityIcons) |

**Active State:** Green pill background, larger icon, green text.

**Old tabs (retired):** Disease / Varieties / Rootstock — moved into Discover tab.

---

## 14. Component Patterns

| Component | Description |
|-----------|-------------|
| `.card-modern` | White card, rounded-2xl, subtle shadow, scale on press |
| `.section-header` | Title (display font) + Hindi subtitle + "View All" link |
| `.section-title-icon` | Small green circle icon before section title |
| `.h-scroll-track` | Horizontal scroll container with snap |
| `.card-act-btn` | Circular action button (32px), like/save/done/pin |
| `.task-priority-pill` | Colored pill by priority |
| `.alert-row-card` | Alert with left colored severity bar |
| `.outbreak-card` | Community report with left severity bar |
| `.scroll-hint` | "Swipe to explore · स्वाइप करें" hint text |
| `SegmentedControl` | Two-pill toggle for dual-mode screens |
| `ToolWidgetCard` | Icon circle + title + Hindi title, 2-col grid |
| `PredictionCard` | Risk badge + disease name + action buttons |

---

## 15. All Screens

| Screen | Route | Key Features |
|--------|-------|-------------|
| **Home** | `home` | Segmented: My Farm dashboard / Community feed |
| My Farm | (segment) | Hero, stats, prediction alerts, tasks, forecast |
| Community | (segment) | Post composer, feed, questions, experts, groups |
| **Spray** | `spray` | Schedule, stages, chemicals, tank calc |
| **Shop** | `shop` | Products, cart, checkout (Phase 1) |
| **Discover** | `discover` | Disease lib, varieties, rootstocks, blog, tools |
| Disease Library | `discover/disease` | Filters, cards, detail with symptoms/prevention/treatment |
| Variety Guide | `discover/variety` | Filter by season, cards, detail |
| Rootstock Guide | `discover/rootstock` | Filter by size, cards, detail |
| Blog | `discover/blog` | Category pills, cards, article pages |
| Kisan Tools | `discover/tools` | 26 widgets in 7 categories (2-col grid) |
| Tool Calculator | `tools/:id` | Individual calculator screen |
| **My Orchard** | `my-orchard` | Orchard list, blocks, spray logs, predictions |
| Orchard Blocks | `my-orchard/blocks` | Manage sub-divisions per orchard |
| Alert Detail | `alert/:logId` | Full prediction detail + feedback |
| Spray Log | `my-orchard/spray-logs` | History + reward points |
| **Weather** | `weather` | 7-day + hourly forecast, spray suitability, 48h chart |
| **Auth** | `auth` | Login, Register, OTP, Forgot Password |
| **Onboarding** | `welcome` | 4-slide carousel → auth flow |
| **Notifications** | `notifications` | List + settings |
| **Profile** | `profile` | User stats, saved items, settings |

---

*This document is a reference for the Baagicha React Native app. Values extracted from Laravel frontend + mobile implementation + prediction engine research.*
