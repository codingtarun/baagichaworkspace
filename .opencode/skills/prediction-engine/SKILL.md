---
name: prediction-engine
description: Disease/pest prediction & spray recommendation engine — Phase 1+2 code written but never scheduled, routed or validated. Use when working on DiseasePressureService, PestDevelopmentService, SprayWindowService, epidemiological models (Mills, Maryblyt, DMC), or prediction APIs.
---

# Baagvaani Prediction & Recommendation Engine

> **Module:** Intelligent Disease/Pest Prediction + Spray Recommendation  
> **Backend:** Laravel 12  
> **Status:** Phase 1 + Phase 2 code written (2026-05-21) — **not running in production, never validated**  
> **Next:** Shadow Mode Validation (Weeks 11-12) — not started  
> **Source:** `BaagvaaniBrain/research/prediction-engine/` (00_INDEX + 9 implementation docs)  
> **Code:** `web_baagicha/Modules/Disease/` (services `app/Services/Prediction/`, jobs `app/Jobs/`, commands `app/Console/Commands/`)

> ## ⚠️ Reality check (verified 2026-10-04)
>
> - **The prediction commands never run.** Their schedule is defined only in
>   `web_baagicha/app/Console/Kernel.php`, which Laravel 12 never loads (scheduling lives in
>   `routes/console.php` and module service providers). `php artisan schedule:list` shows
>   none of `app:compute-disease-pressure`, `app:accumulate-pest-dd`,
>   `app:compute-spray-windows` or `app:initialize-pest-season`. The commands themselves are
>   registered and can be run by hand.
> - **`Modules/Disease/app/Http/Controllers/Api/PredictionController.php` is unrouted.** No
>   `predictions`, `spray-window` or `forecast/detailed` routes exist (`route:list`). Only the
>   orchard-blocks and spray-logs endpoints below are live.
> - **Three of the "8 migrations" do not exist:** no migration creates `spray_windows`,
>   `prediction_feedbacks` or `weather_hourly_forecasts`. Hourly data is a JSON column
>   (`weather.hourly_forecast_48h`) and the next spray window is `weather.next_spray_window`.
> - **`pest_models` has 0 rows**, so degree-day tracking has nothing to drive it.
> - **Never validated.** Shadow mode (below) has not been run. Do not surface predictions to
>   farmers until it has.

---

## What It Does

```
┌─────────────────────────────────────────────────────────────┐
│                    PREDICTION & RECOMMENDATION ENGINE        │
├─────────────────────────────────────────────────────────────┤
│  INPUTS                              PROCESSING    OUTPUTS  │
│  ────────                            ──────────    ──────── │
│                                                             │
│  🌤️ Weather data              ┌─────────────────┐  📱 Push  │
│     (current + 5-day forecast)│ DiseasePressure │  📋 Spray │
│                               │ Service         │  🏠 Cards │
│  🍎 Orchard profile    ──────▶│ ├─ Revised Mills│  🌡️ UI    │
│     (altitude, variety,       │ ├─ Maryblyt     │  ⚠️ Badges│
│      blocks, soil)            │ ├─ DMC          │           │
│                               │ └─ Enhanced Rule│           │
│  🐛 Pest lifecycle data       ├─────────────────┤           │
│     (DD thresholds, biofix)   │ PestDevelopment │           │
│                               │ Service         │           │
│  📊 Historical feedback       ├─────────────────┤           │
│     (farmer confirmations)    │ SprayWindow     │           │
│                               │ Service         │           │
│                               ├─────────────────┤           │
│                               │ Recommendation  │           │
│                               │ Generator       │           │
│                               └─────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Three Implementation Phases

### Phase 1: Enhanced Rules + Forecast (Weeks 1-3) ✅ Code written
- Extended `diseases` table with model flags
- Built `DiseasePressureService` (rule-based v2)
- Added `disease_pressure_log` table
- Wired predictions into notification pipeline

### Phase 2: Epidemiological Models (Weeks 4-10) ✅ Code written (not scheduled — see reality check)
- `RevisedMillsModel` — apple scab
- `SimplifiedMaryblytModel` — fire blight
- `DmcModel` — powdery mildew
- `DegreeDayModel` + daily accumulation — codling moth, San Jose scale
- `pest_models` + `pest_tracker` tables
- `orchard_blocks` table + CRUD API

### Phase 3: ML + Microclimate (Months 3-6) ⏳ PENDING
- `MicroclimateService` (slope/aspect adjustments)
- Farmer feedback loop (`is_confirmed` field)
- Random Forest / XGBoost on feedback data
- KVK partnership validation

---

## Database Schema

### Planned Migrations (8 in the plan — 5 exist)

```php
orchard_blocks           // 1. Sub-divisions within an orchard        — Modules/Orchard ✅
disease_pressure_log     // 2. Prediction outputs per orchard/date    — Modules/Disease ✅
pest_models              // 3. Config for each pest (0 rows)          — Modules/Disease ✅
pest_tracker             // 4. Per-orchard pest state (DD, biofix)    — Modules/Disease ✅
spray_logs               // 5. Farmer spray records (feedback loop)   — Modules/KnowledgeBase ✅
prediction_feedbacks     // 6. Farmer confirmation/denial             — ❌ no migration
spray_windows            // 7. Computed optimal spray times           — ❌ no migration (weather.next_spray_window JSON)
weather_hourly_forecasts // 8. Hourly data for model inputs           — ❌ no migration (weather.hourly_forecast_48h JSON)
```

### Key Models

| Model | Purpose |
|-------|---------|
| `OrchardBlock` | Sub-divisions of orchard (variety, aspect, slope, soil) |
| `PestModel` | Configuration: base temp, DD thresholds, biofix defaults |
| `PestTracker` | Per-orchard pest state: cumulative DD, next event |
| `DiseasePressureLog` | Daily prediction output per disease |
| `SprayLog` | Farmer spray records + reward points |
| `PredictionFeedback` | Farmer confirmation/denial + notes |

---

## Core Services

| Service | File | Purpose |
|---------|------|---------|
| `DiseasePressureService` | `Modules/Disease/app/Services/Prediction/DiseasePressureService.php` | Orchestrates all disease models |
| `PestDevelopmentService` | `Modules/Disease/app/Services/Prediction/PestDevelopmentService.php` | Degree-day accumulation |
| `SprayWindowService` | `Modules/Disease/app/Services/Prediction/SprayWindowService.php` | Optimal spray timing |
| `LeafWetnessEstimator` | `Modules/Disease/app/Services/Prediction/LeafWetnessEstimator.php` | Estimates wetness from RH+rain+dew |
| `RecommendationGenerator` | `Modules/Disease/app/Services/Prediction/RecommendationGenerator.php` | Actionable spray recommendations |
| `MicroclimateService` | `Modules/Disease/app/Services/Prediction/MicroclimateService.php` | Slope/aspect adjustments |
| `ModelFactory` | `Modules/Disease/app/Services/Prediction/ModelFactory.php` | Instantiates correct model per disease |

### Model Classes

All under `Modules/Disease/app/Services/Prediction/Models/` — `Scab/RevisedMillsModel`,
`FireBlight/SimplifiedMaryblytModel`, `PowderyMildew/DmcModel`, `Pests/DegreeDayModel`,
plus `RuleBasedModel` and `AbstractPredictionModel` at the top level.

| Model | Disease/Pest | Approach | Accuracy |
|-------|-------------|----------|----------|
| `RevisedMillsModel` | Apple scab | Temperature + estimated wetness | ~75-80% |
| `SimplifiedMaryblytModel` | Fire blight | Temp + humidity thresholds | Medium |
| `DmcModel` | Powdery mildew | Temp + RH (no rain needed) | High |
| `DegreeDayModel` | Codling moth, San Jose scale | Cumulative degree-days | Medium |
| `RuleBasedModel` | All (fallback) | Weather threshold rules | Baseline |

---

## API Endpoints

Live (verified with `route:list`):

```
GET|POST         /api/v1/orchards/{orchard}/blocks
GET|PUT|DELETE   /api/v1/orchards/{orchard}/blocks/{block}
GET|POST         /api/v1/orchards/{orchard}/spray-logs
GET              /api/v1/spray-logs/{log}
```

Planned but **not routed** (`PredictionController` exists with no routes pointing at it):

```
GET    /api/v1/orchard/{id}/predictions
GET    /api/v1/orchard/{id}/predictions/disease/{diseaseId}
GET    /api/v1/orchard/{id}/predictions/pest/{pestModelId}
GET    /api/v1/orchard/{id}/spray-window
GET    /api/v1/orchard/{id}/forecast/detailed
POST   /api/v1/predictions/{logId}/feedback
GET    /api/v1/orchard/{id}/blocks/{blockId}/predictions
```

---

## Automation (Commands + Jobs + Scheduler)

Schedules below are what `app/Console/Kernel.php` declares — **none of them are active**
(see reality check). To activate, move them into `routes/console.php` or a module provider.

| Command | Intended schedule (Kernel.php) | Purpose |
|---------|----------|---------|
| `app:compute-disease-pressure` | Daily 05:30 | Dispatch `ComputeDiseasePressureJob` (queue `disease-pressure`) |
| `app:accumulate-pest-dd` | Daily 06:30 | Update DD accumulations |
| `app:compute-spray-windows` | Twice daily 07:00 / 19:00 | Dispatch `ComputeSprayWindowJob` (queue `spray-windows`) |
| `app:initialize-pest-season` | Yearly, 1 Jan 00:00 | Reset pest trackers for new season |
| `SendPredictionAlert` (Job) | Queued | Deliver push notifications |
| `ComputePredictionsForUser` (Job) | Queued | Per-user prediction batch |

If scheduled, the queue worker must also listen on `disease-pressure` and `spray-windows`.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Revised Mills (not RIMpro)** | RIMpro needs hourly sensors. Mills works with forecast data. Upgrade later. |
| **Leaf wetness ESTIMATED** | Small farmers don't have sensors. ~70-80% accuracy from RH + rain + dew point. |
| **Regional biofix defaults** | Farmers won't buy pheromone traps. Altitude-based defaults, override allowed. |
| **Rule engine FIRST** | Enhance existing `WeatherIntelligenceService` before replacing. |
| **Orchard blocks SEPARATE** | New table, not column on `user_orchards`. Supports multi-block per user. |
| **Offline-first predictions** | Pre-compute 48h, cache in Redis + mobile MMKV. Himalayan connectivity is poor. |
| **Hindi + English bilingual** | Every alert has `message_hi`. Critical for HP adoption. |

---

## Validation Gate (DO NOT SKIP)

1. **Shadow Mode (Season 0):** Run internally, compare with KVK expert recommendations
   - Target: <20% false positives, <5% false negatives
2. **Soft Launch (Season 1):** Label "BETA", heavy feedback collection
3. **Full Launch (Season 2):** Predictions become primary recommendations

> **Wrong spray advice = crop loss = trust destroyed forever.**

---

## Quick Resume Commands

```bash
# Shadow mode
PREDICTION_MODE=shadow

# Seed data
php artisan db:seed --class=DiseaseModelSeeder
php artisan db:seed --class=PestModelSeeder

# Initialize pest season
php artisan app:initialize-pest-season

# Dry run test
php artisan app:compute-disease-pressure --dry-run --orchard=1

# Compute spray windows
php artisan app:compute-spray-windows --orchard=1

# Run scheduler (does NOT run the prediction commands today — see reality check)
php artisan schedule:run
```

---

## Sources

1. [RIMpro Cloud — Apple Scab Model](https://rimpro.cloud/)
2. [WSU Decision Aid System](https://treefruit.wsu.edu/tools-resources/wsu-das/)
3. [NEWA Crop & Pest Management](https://newa.cornell.edu/)
4. [Mills Table Revision (MacHardy & Gadoury, 1989)](https://www.apsnet.org/)
5. [ADEM / NIAB Apple Scab Forecasting](https://www.niab.com/)
6. [Apple Scab in HP — Sharma & Bhandari](https://journal.agrimetassociation.org/)
7. [Codling Moth DD Models — WSU](https://treefruit.wsu.edu/)
