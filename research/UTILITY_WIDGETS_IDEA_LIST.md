# Farmer Utility Widgets / Calculator Ideas for Baagicha App

> **Date:** 2026-06-03  
> **Scope:** Apple, Pear & Plum (Himachal Pradesh, J&K, Uttarakhand focus)  
> **Status:** Research Compilation — Pending Review & Prioritization  

---

## Background

This document compiles candidate **standalone utility widgets / mini-calculators** that can be embedded into the Baagicha mobile app to provide daily value to temperate-fruit growers. These are meant to be **simple, single-purpose tools** — not full modules. Where necessary, a lightweight Laravel-backed config/admin layer can support dynamic rates, varieties, and regional norms.

Research sources include:
- Competitor apps (Semios, Orchard Solutions, Croptracker, farmOS, Agworld)
- Global orchard tools (Cornell, WSU Tree Fruit, UMass, Perennia, Ferri App, MaluSim)
- Indian horticulture manuals (HP GAP Apple Manual, HPHDP guidelines, MIDH norms)
- Existing agriculture calculator apps (Pioneer Field360, Yara, Climate FieldView)

---

## Categorized Widget List

### 1. Orchard Establishment & Planning

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 1.1 | **New Orchard Cost Estimator** *(User Idea)* | Given area (bigha/acre), rootstock choice, variety mix, and infrastructure level (basic / MIDH-subsidized / high-density), estimates total setup cost: saplings, pits, manure, irrigation, anti-hail net, labour. | ✅ | Admin DB: per-unit rates by region & season; subsidy % by scheme |
| 1.2 | **Tree Spacing & Density Calculator** | Input: plot dimensions + rootstock vigor (dwarf / semi-dwarf / standard). Output: recommended in-row & between-row spacing, trees per acre, layout sketch. | ✅ | Static tables per crop + rootstock |
| 1.3 | **Pollinizer Ratio Planner** | Given main variety + orchard area, suggests how many pollinizer trees needed (UHF recommends 33% for HP apples), placement pattern (every 3rd tree, alternate rows, etc.). | ✅ | Variety compatibility matrix |
| 1.4 | **Orchard Layout Visualizer** | Simple grid preview of tree positions with variety labels + pollinizer markers. Exportable as image/share. | ✅ | N/A — purely visual |

### 2. Crop Load & Thinning Management

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 2.1 | **Fruit Thinning Guide by Trunk Diameter** *(User Idea)* | Input: rootstock type + trunk diameter (mm) at 1 ft above graft union. Output: recommended fruits to keep per tree (Cornell/Valent gauge logic). Supports young trees (2nd–5th leaf). | ✅ | Static lookup tables by crop & rootstock vigor |
| 2.2 | **Equilifruit Branch Disc Digital** | Input: branch diameter (mm). Output: target fruit count for that limb (INRA Equilifruit disc logic). Helps hand-thinning crews. | ✅ | Static branch-diameter → fruit count tables |
| 2.3 | **Crop Load Target Calculator (Mature Trees)** | Input: tree density + desired yield (kg/acre) + average fruit weight. Output: target fruits per tree + expected grade distribution. | ✅ | Variety-specific avg fruit weight |
| 2.4 | **Fruitlet Growth Rate Tracker** | Post-thinning follow-up: input fruitlet diameters at 2-day intervals. Trend graph shows which fruitlets are persisting vs. abscising (simplified Ferri/Schwallier model). | ⚠️ (can store locally, sync later) | N/A — user data only |

### 3. Spray & Input Calculators

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 3.1 | **Sprayer Calibration (Tree Row Volume)** | Input: tree height, width, row spacing, travel speed, concentration factor (1X/2X/3X). Output: Dilute GPA, required GPM, nozzle flow check. | ✅ | Static constants (TRV formula) |
| 3.2 | **Pesticide Mix Calculator** | Input: tank capacity, recommended dose per 100L or per acre, orchard block size. Output: exact ml/gm to pour + water needed + number of tank loads. | ✅ | Product DB (dose rates) from admin |
| 3.3 | **Fertilizer Requirement Calculator** | Input: orchard age, area, soil test results (optional), leaf analysis (optional). Output: FYM, N, P, K, micronutrient quantities + split schedule (HP GAP-aligned). | ⚠️ | Admin DB: standard schedules by orchard age; optionally soil test norms |
| 3.4 | **Calcium Spray Schedule Planner** | Given harvest date, generates pre-harvest calcium chloride/nitrate spray calendar (typically 3–4 sprays, 10–15 days apart). | ✅ | Static calendar math |

### 4. Harvest & Post-Harvest

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 4.1 | **Harvest Maturity Checker** | Input: starch index (iodine test), firmness (kg), brix (%), days after full bloom. Output: maturity verdict (ready / wait / over-mature) per cultivar. | ✅ | Cultivar-specific maturity thresholds from admin |
| 4.2 | **Fruit Grade / Size Calculator** | Input: fruit diameter (mm) or weight (g), crop (apple/pear/plum). Output: grade (A/Extra, B/Class I, C/Class II) + expected market tier (export / mandi / processing). | ✅ | Admin DB: grade tables (can vary by mandi/APEDA) |
| 4.3 | **Fruit Weight Estimator from Diameter** | Input: fruit diameter (mm) + variety. Output: estimated weight (g) using allometric regression (e.g., Gala: W = 17.03 − 1.48·FD + 0.046·FD²). | ✅ | Variety-specific regression coefficients |
| 4.4 | **Cold Storage Rent Calculator** | Input: expected produce weight, storage duration (months), CA vs. normal cold store rate. Output: estimated storage cost + break-even vs. spot market price. | ⚠️ | Admin DB: regional cold store tariffs + market price feed |
| 4.5 | **Harvest Labour Estimator** | Input: orchard area / tree count / expected yield. Output: estimated man-days for picking + rough wage cost at local rates. | ✅ | Admin DB: HP/J&K/UK wage norms |

### 5. Financial & Market

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 5.1 | **Input Cost Tracker (Mini)** | Quick log of spray/fertilizer/labour costs per orchard block. Running total per season + per-kg cost of production. | ⚠️ (local store + sync) | N/A — user data |
| 5.2 | **Mandi Price vs. Storage Break-Even** | Input: current mandi rate, expected rate after X months, storage cost, weight loss %. Output: net margin comparison (sell now vs. store). | ❌ | Live mandi price API + storage rates |
| 5.3 | **Subsidy Eligibility Checker** | Input: orchard details (area, location, scheme). Output: which subsidies apply (MIDH, HPHDP, SMAM), estimated subsidy amount, required documents checklist. | ⚠️ | Admin DB: scheme rules by state/district |

### 6. Weather & Phenology

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 6.1 | **Growing Degree Day (GDD) Calculator** | Input: daily max/min temps or auto-fetch from weather API. Output: accumulated GDD + pest/disease stage predictions (e.g., codling moth egg hatch). | ⚠️ | Base temps by pest model from admin |
| 6.2 | **Chill Hour / Chill Portion Tracker** | For HP/J&K apple varieties: tracks accumulated chilling hours (<7°C) or Utah chill portions Nov–Feb. Alerts if deficit predicted. | ⚠️ | Weather API + variety chill requirements |
| 6.3 | **Full Bloom to Harvest Countdown** | Input: full bloom date. Output: expected harvest window (days after full bloom) by variety, with maturity milestone reminders. | ✅ | Variety-specific DAFB ranges |
| 6.4 | **Frost Risk Window** | Based on 7-day weather forecast, flags nights with temp ≤ 2°C and suggests mitigation (smudge pots, sprinklers, fans). | ❌ | Weather API + altitude-adjusted thresholds |

### 7. Training & Pruning

| # | Widget Name | What It Does | Offline? | Data Source / Config Need |
|---|-------------|--------------|----------|---------------------------|
| 7.1 | **Pruning Weight Estimator** | Input: tree age, vigor, last year’s pruning weight. Output: expected wood to prune (kg/tree) + disposal method suggestions. | ✅ | Empirical tables |
| 7.2 | **Spreader / Branch Angle Guide** | Visual guide + angle measurement helper to ensure primary branches have 60–90° crotch angles for strong scaffold development. | ✅ | N/A — visual tool |

---

## Competitor Feature Gap Analysis

| Competitor | Calculators / Utilities They Offer | What’s Missing (Our Opportunity) |
|------------|-----------------------------------|---------------------------------|
| **Orchard Solutions (India)** | Plantation guidance, cost advisory (human-led) | No self-service app calculators; no real-time widgets |
| **Semios** | Weather, pest models, irrigation — enterprise only | Too expensive; no Indian pricing; no small-farmer calculators |
| **IFFCO Kisan** | Generic weather, market prices | No orchard-specific calculators |
| **Pioneer Field360** | GDU, precipitation, growth stage (row crops) | No tree fruit support; no thinning/spray calibrations |
| **Croptracker** | Labor cost, thinning records (B2B SaaS) | Not India-priced; no Hindi; no subsidy tools |
| **Ferri App / MaluSim** | Fruitlet growth model, carbohydrate model | US-only; no Indian varieties; requires weather station |

**Key Insight:** No existing app in the Indian market offers a **free, Hindi+English, apple/pear/plum-specific calculator suite** for smallholders. This is a clear differentiation opportunity for Baagicha.

---

## Recommended Implementation Notes

### Technical Approach
- **Frontend:** React Native screens, each widget as a self-contained route (`/tools/orchard-cost`, `/tools/thinning-guide`, etc.)
- **Backend:** Laravel API for admin-configurable tables (rates, varieties, thresholds) + user saved calculations history
- **Offline Strategy:** All pure-calculation widgets work offline with locally cached config tables; sync when online
- **Admin Panel:** Simple CRUD in Laravel for:
  - Regional input rates (saplings, labour, nets, etc.)
  - Variety database (chill hours, DAFB, maturity thresholds, grade sizes)
  - Product database (pesticide/fertilizer doses)
  - Subsidy scheme rules

### Priority Tiers (Suggested — To Be Discussed)

| Tier | Widgets | Rationale |
|------|---------|-----------|
| **P0 — Immediate Impact** | 1.1 New Orchard Cost Estimator, 2.1 Thinning by Trunk Diameter, 3.1 Sprayer Calibration, 4.2 Fruit Grade Calculator | Directly address user request + highest daily usage |
| **P1 — High Value** | 1.2 Tree Spacing, 2.3 Crop Load Target, 3.2 Pesticide Mix, 4.1 Harvest Maturity, 5.3 Subsidy Checker | Strong agronomic value; differentiate from competitors |
| **P2 — Engagement** | 1.3 Pollinizer Planner, 2.4 Fruitlet Tracker, 4.3 Weight Estimator, 4.4 Storage Rent, 6.1 GDD, 6.3 Bloom Countdown | Increase session frequency; build habit |
| **P3 — Nice to Have** | 1.4 Layout Visualizer, 4.5 Labour Estimator, 5.2 Mandi Break-Even, 7.1 Pruning Weight | Longer-term stickiness |

---

## Open Questions for Product Discussion

1. **Unit system:** Should inputs accept both `bigha` (local) and `acre/hectare` (standard)? What is the conversion used in each target state?
2. **Variety coverage:** How many apple varieties to support in v1? (Royal Delicious, Red Delicious, Golden, Granny Smith, Fuji, etc.)
3. **Data ownership:** Should saved calculations be tied to the user’s orchard profile, or kept as anonymous tool usage?
4. **Monetization:** Any widgets to reserve for premium tier (e.g., storage break-even, subsidy checker), or all free?
5. **Hindi UX:** Should numeric inputs show both Hindi numerals and English, or just English with Hindi labels?

---

## Research Sources

1. Cornell University — Young Apple Thinning Gauge & Crop Load Models
2. Washington State University (WSU) Tree Fruit — Crop Load Management
3. UMass Amherst — Block-Specific Sprayer Calibration Worksheet
4. Perennia / Ferri — Fruitlet Growth Rate App (Ontario)
5. Ohio State / Ohioline — Orchard Sprayer Calibration
6. HP GAP Apple Cultivation Manual — Fertilizer schedules, pollinizer ratios
7. Orchard Solutions India — Plantation guidance & subsidy context
8. Futura Grading / FAO Codex — Fruit size grading standards
9. University of Tasmania — Post-harvest maturity indices (starch, firmness, brix)
10. MDPI Sensors (2023) — Fruit sizing allometric models
11. Pioneer Field360 / Yara ImageIT / Climate FieldView — Calculator UX patterns
12. Croptracker — Precision crop load & labor cost tools

---

> **Next Step:** Review this list, pick priority tier(s), then proceed to wireframe + DB schema for selected widgets.
