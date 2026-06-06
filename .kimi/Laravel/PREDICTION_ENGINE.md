# Baagvaani Prediction & Recommendation Engine

> **Module:** Intelligent Disease/Pest Prediction + Spray Recommendation  
> **Backend:** Laravel 12  
> **Status:** Phase 1 + Phase 2 Backend COMPLETE (2026-05-21)  
> **Next:** Shadow Mode Validation (Weeks 11-12)  
> **Source:** `research/prediction-engine/` (9 implementation docs)

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

### Phase 1: Enhanced Rules + Forecast (Weeks 1-3) ✅ DONE
- Extended `diseases` table with model flags
- Built `DiseasePressureService` (rule-based v2)
- Added `disease_pressure_log` table
- Wired predictions into notification pipeline

### Phase 2: Epidemiological Models (Weeks 4-10) ✅ DONE
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

### New Migrations (8 total)

```php
// 1. orchard_blocks — sub-divisions within an orchard
disease_pressure_logs    // 2. Prediction outputs per orchard/date
pest_models              // 3. Config for each pest (codling moth, etc.)
pest_trackers            // 4. Per-orchard pest state (cumulative DD, biofix)
spray_logs               // 5. Farmer spray records (feedback loop)
prediction_feedbacks     // 6. Farmer confirmation/denial of alerts
spray_windows            // 7. Computed optimal spray times
weather_hourly_forecasts // 8. Hourly data for model inputs
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
| `DiseasePressureService` | `app/Services/Prediction/DiseasePressureService.php` | Orchestrates all disease models |
| `PestDevelopmentService` | `app/Services/Prediction/PestDevelopmentService.php` | Degree-day accumulation |
| `SprayWindowService` | `app/Services/Prediction/SprayWindowService.php` | Optimal spray timing |
| `LeafWetnessEstimator` | `app/Services/Prediction/LeafWetnessEstimator.php` | Estimates wetness from RH+rain+dew |
| `RecommendationGenerator` | `app/Services/Prediction/RecommendationGenerator.php` | Actionable spray recommendations |
| `MicroclimateService` | `app/Services/Prediction/MicroclimateService.php` | Slope/aspect adjustments |
| `ModelFactory` | `app/Services/Prediction/ModelFactory.php` | Instantiates correct model per disease |

### Model Classes

| Model | Disease/Pest | Approach | Accuracy |
|-------|-------------|----------|----------|
| `RevisedMillsModel` | Apple scab | Temperature + estimated wetness | ~75-80% |
| `SimplifiedMaryblytModel` | Fire blight | Temp + humidity thresholds | Medium |
| `DmcModel` | Powdery mildew | Temp + RH (no rain needed) | High |
| `DegreeDayModel` | Codling moth, San Jose scale | Cumulative degree-days | Medium |
| `RuleBasedModel` | All (fallback) | Weather threshold rules | Baseline |

---

## API Endpoints

```
GET    /api/v1/orchard/{id}/predictions
GET    /api/v1/orchard/{id}/predictions/disease/{diseaseId}
GET    /api/v1/orchard/{id}/predictions/pest/{pestModelId}
GET    /api/v1/orchard/{id}/spray-window
GET    /api/v1/orchard/{id}/forecast/detailed
POST   /api/v1/predictions/{logId}/feedback

GET    /api/v1/orchards/{id}/blocks
POST   /api/v1/orchards/{id}/blocks
PUT    /api/v1/orchards/{id}/blocks/{blockId}
DELETE /api/v1/orchards/{id}/blocks/{blockId}
GET    /api/v1/orchard/{id}/blocks/{blockId}/predictions

GET    /api/v1/orchard/{id}/spray-logs
POST   /api/v1/orchard/{id}/spray-logs
```

---

## Automation (Commands + Jobs + Scheduler)

| Command | Schedule | Purpose |
|---------|----------|---------|
| `app:compute-disease-pressure` | Daily 6 AM | Run all disease models for all orchards |
| `app:accumulate-pest-degree-days` | Daily 6:30 AM | Update DD accumulations |
| `app:compute-spray-windows` | Daily 7 AM | Calculate optimal spray windows |
| `app:initialize-pest-season` | Yearly (Nov) | Reset pest trackers for new season |
| `SendPredictionAlert` (Job) | Queued | Deliver push notifications |
| `ComputePredictionsForUser` (Job) | Queued | Per-user prediction batch |

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

# Run scheduler
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
