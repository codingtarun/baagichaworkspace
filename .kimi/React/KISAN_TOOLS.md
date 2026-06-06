# Baagicha — Kisan Tools / Utility Widgets

> **Date:** 2026-06-03  
> **Scope:** Apple, Pear & Plum (HP, J&K, Uttarakhand focus)  
> **Status:** UI Implemented (`screens/ToolsScreen.tsx`) — calculators show "Coming Soon"  
> **Source:** `research/UTILITY_WIDGETS_IDEA_LIST.md`

---

## Overview

26 standalone utility calculators & guides embedded in the Baagicha mobile app. Each widget is a **simple, single-purpose tool** — not a full module. A lightweight Laravel-backed admin layer supports dynamic rates, varieties, and regional norms.

---

## Categorized Widget List

### 1. Orchard Establishment & Planning 🌱

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 1.1 | **New Orchard Cost Estimator** | Given area (bigha/acre), rootstock, variety mix, infrastructure level → estimates total setup cost | ✅ | Admin DB: per-unit rates by region & season; subsidy % |
| 1.2 | **Tree Spacing & Density** | Input: plot dimensions + rootstock vigor → recommended spacing, trees per acre, layout sketch | ✅ | Static tables per crop + rootstock |
| 1.3 | **Pollinizer Ratio Planner** | Given main variety + area → suggests pollinizer trees needed (UHF: 33% for HP apples), placement pattern | ✅ | Variety compatibility matrix |
| 1.4 | **Orchard Layout Visualizer** | Grid preview of tree positions with variety labels + pollinizer markers. Exportable image | ✅ | None — purely visual |

### 2. Crop Load & Thinning ✂️

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 2.1 | **Thinning by Trunk Diameter** *(User Idea)* | Input: rootstock + trunk diameter (mm). Output: recommended fruits per tree (Cornell/Valent gauge) | ✅ | Static lookup tables |
| 2.2 | **Equilifruit Branch Disc** | Input: branch diameter (mm). Output: target fruit count for that limb (INRA Equilifruit) | ✅ | Static branch-diameter → fruit count tables |
| 2.3 | **Crop Load Target (Mature)** | Input: tree density + desired yield + avg fruit weight → target fruits per tree + grade distribution | ✅ | Variety-specific avg fruit weight |
| 2.4 | **Fruitlet Growth Tracker** | Input fruitlet diameters at 2-day intervals → trend graph showing persistence vs. abscising | ⚠️ | User data only |

### 3. Spray & Inputs 🧪

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 3.1 | **Sprayer Calibration (TRV)** | Input: tree height, width, row spacing, travel speed, concentration → Dilute GPA, required GPM | ✅ | Static constants (TRV formula) |
| 3.2 | **Pesticide Mix Calculator** | Input: tank capacity, recommended dose, block size → exact ml/gm + water needed + tank loads | ✅ | Product DB (dose rates) |
| 3.3 | **Fertilizer Requirement** | Input: orchard age, area, soil test (optional) → FYM, N, P, K, micronutrient quantities + split schedule | ⚠️ | Admin DB: standard schedules |
| 3.4 | **Calcium Spray Schedule** | Given harvest date → generates pre-harvest calcium spray calendar (3–4 sprays, 10–15 days apart) | ✅ | Static calendar math |

### 4. Harvest & Post-Harvest 🧺

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 4.1 | **Harvest Maturity Checker** | Input: starch index, firmness, brix, DAFB → maturity verdict (ready/wait/over-mature) per cultivar | ✅ | Cultivar-specific thresholds |
| 4.2 | **Fruit Grade / Size** | Input: fruit diameter (mm) or weight (g) → grade (A/Extra, B/Class I, C/Class II) + market tier | ✅ | Admin DB: grade tables |
| 4.3 | **Fruit Weight Estimator** | Input: fruit diameter (mm) + variety → estimated weight (g) using allometric regression | ✅ | Variety-specific coefficients |
| 4.4 | **Cold Storage Rent** | Input: produce weight, storage duration, CA vs normal → estimated cost + break-even vs spot price | ⚠️ | Admin DB: regional cold store tariffs |
| 4.5 | **Harvest Labour Estimator** | Input: orchard area / tree count / expected yield → estimated man-days + wage cost | ✅ | Admin DB: HP/J&K/UK wage norms |

### 5. Financial & Market 💰

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 5.1 | **Input Cost Tracker** | Quick log of spray/fertilizer/labour costs per block. Running total per season + per-kg cost | ⚠️ | User data |
| 5.2 | **Mandi Price Break-Even** | Input: current mandi rate, expected rate after X months, storage cost, weight loss % → net margin comparison | ❌ | Live mandi price API |
| 5.3 | **Subsidy Eligibility** | Input: orchard details → which subsidies apply (MIDH, HPHDP, SMAM), estimated amount, documents checklist | ⚠️ | Admin DB: scheme rules |

### 6. Weather & Phenology 🌡️

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 6.1 | **Growing Degree Days (GDD)** | Input: daily max/min temps or auto-fetch from API → accumulated GDD + pest/disease stage predictions | ⚠️ | Base temps by pest model |
| 6.2 | **Chill Hour Tracker** | Tracks accumulated chilling hours (<7°C) or Utah chill portions Nov–Feb. Alerts if deficit | ⚠️ | Weather API + variety chill requirements |
| 6.3 | **Bloom to Harvest Countdown** | Input: full bloom date → expected harvest window (DAFB) by variety, with milestone reminders | ✅ | Variety-specific DAFB ranges |
| 6.4 | **Frost Risk Window** | Based on 7-day forecast → flags nights ≤2°C, suggests mitigation (smudge pots, sprinklers, fans) | ❌ | Weather API + altitude thresholds |

### 7. Training & Pruning 🌳

| # | Widget | What It Does | Offline | Backend Need |
|---|--------|--------------|---------|-------------|
| 7.1 | **Pruning Weight Estimator** | Input: tree age, vigor, last year's pruning weight → expected wood to prune (kg/tree) | ✅ | Empirical tables |
| 7.2 | **Branch Angle Guide** | Visual guide + angle measurement helper for 60–90° crotch angles | ✅ | None — visual tool |

---

## Priority Tiers

| Tier | Widgets | Rationale |
|------|---------|-----------|
| **P0 — Immediate** | 1.1 Orchard Cost, 2.1 Thinning by Trunk, 3.1 Sprayer Calibration, 4.2 Fruit Grade | Direct user request + highest daily usage |
| **P1 — High Value** | 1.2 Tree Spacing, 2.3 Crop Load, 3.2 Pesticide Mix, 4.1 Harvest Maturity, 5.3 Subsidy | Strong agronomic value; differentiates |
| **P2 — Engagement** | 1.3 Pollinizer, 2.4 Fruitlet Tracker, 4.3 Weight Estimator, 4.4 Storage Rent, 6.1 GDD, 6.3 Bloom | Increases session frequency |
| **P3 — Nice to Have** | 1.4 Layout Visualizer, 4.5 Labour, 5.2 Mandi Break-Even, 7.1 Pruning Weight | Longer-term stickiness |

---

## Technical Approach

| Layer | Approach |
|-------|----------|
| **Frontend** | React Native screens, each widget as self-contained route (`/tools/orchard-cost`, etc.) |
| **Backend** | Laravel API for admin-configurable tables (rates, varieties, thresholds) + user saved calculations |
| **Offline** | All pure-calculation widgets work offline with locally cached config tables; sync when online |
| **Admin** | Simple CRUD for: regional rates, variety database, product database, subsidy scheme rules |

---

## Competitive Gap

No existing app in the Indian market offers a **free, Hindi+English, apple/pear/plum-specific calculator suite** for smallholders. Key differentiator vs:
- **Orchard Solutions** — human-led, expensive, no self-service
- **IFFCO Kisan** — generic, no orchard calculators
- **Semios** — enterprise-only, no Indian pricing
- **Pioneer Field360** — row crops only, no tree fruit

---

## Open Product Questions

1. **Units:** Accept both `bigha` (local) and `acre/hectare` (standard)?
2. **Variety coverage:** How many apple varieties in v1?
3. **Data ownership:** Saved calculations tied to orchard profile or anonymous?
4. **Monetization:** Any widgets for premium tier?
5. **Hindi UX:** Numeric inputs — English only or Hindi numerals too?
