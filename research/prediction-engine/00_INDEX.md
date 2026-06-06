# Baagvaani Prediction & Recommendation Engine — Implementation Index

> **Module:** Intelligent Disease/Pest Prediction + Spray Recommendation Engine
> **Target:** Laravel 12 Backend + React Native Mobile App
> **Status:** Ready for Implementation
> **Estimated Effort:** 6-8 weeks (Phase 1 + Phase 2)
> **Date:** 2026-05-21
> **Based on Research:** Global DSS Landscape + Epidemiological Models + Existing Baagvaani Stack

---

## Documents in this Folder

| # | Document | Purpose | Lines |
|---|----------|---------|-------|
| `00_INDEX.md` | This file | Navigation + overview | — |
| `01_DATABASE_SCHEMA.md` | All DB migrations, tables, indexes, relationships | Run these migrations first | ~400 |
| `02_MODELS.md` | Eloquent models with relationships, casts, scopes | Create after migrations | ~300 |
| `03_SERVICES.md` | Core PHP service classes (production-ready code) | Business logic layer | ~900 |
| `04_COMMANDS_JOBS.md` | Artisan commands + queued jobs + scheduler config | Automation layer | ~300 |
| `05_API_CONTROLLERS.md` | API routes + controllers + Form Requests | REST layer | ~400 |
| `06_NOTIFICATIONS.md` | Push notification templates + channels | Alert delivery | ~200 |
| `07_MOBILE_INTEGRATION.md` | React Native types, stores, screen specs | Frontend contract | ~300 |
| `08_IMPLEMENTATION_ROADMAP.md` | Week-by-week checklist with acceptance criteria | Project management | ~200 |
| `09_GLOBAL_DSS_RESEARCH_SUMMARY.md` | Competitor analysis + why our approach wins | Context for devs | ~250 |

---

## What This Module Does

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PREDICTION & RECOMMENDATION ENGINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  INPUTS                              PROCESSING                    OUTPUTS  │
│  ────────                            ──────────                    ──────── │
│                                                                            │
│  🌤️ Weather data              ┌─────────────────────┐        📱 Push alerts │
│     (current + 5-day forecast)│  DiseasePressure    │        📋 Spray tasks │
│                               │  Service            │        🏠 Home cards  │
│  🍎 Orchard profile    ──────▶│  ├─ Revised Mills   │──────▶ 🌡️ Weather UI │
│     (altitude, variety,       │  ├─ Maryblyt        │        ⚠️ Risk badges │
│      blocks, soil)            │  ├─ DMC             │                       │
│                               │  └─ Enhanced Rules  │                       │
│  🐛 Pest lifecycle data       ├─────────────────────┤                       │
│     (DD thresholds, biofix)   │  PestDevelopment    │                       │
│                               │  Service            │                       │
│  📊 Historical feedback       ├─────────────────────┤                       │
│     (farmer confirmations)    │  SprayWindow        │                       │
│                               │  Service            │                       │
│                               ├─────────────────────┤                       │
│                               │  Recommendation     │                       │
│                               │  Generator          │                       │
│                               └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Three Implementation Phases

### Phase 1: Enhanced Rules + Forecast (Weeks 1-3)
**Goal:** Dynamic risk scoring using existing `Disease` model fields + 5-day forecast
- Extend `diseases` table with model flags
- Build `DiseasePressureService` (rule-based v2)
- Add `disease_pressure_log` table
- Wire predictions into existing notification pipeline
- Mobile: Weather screen + prediction cards

### Phase 2: Epidemiological Models (Weeks 4-8)
**Goal:** Real scientific models for scab, fire blight, powdery mildew, codling moth
- Implement `RevisedMillsModel` for apple scab
- Implement `SimplifiedMaryblytModel` for fire blight
- Implement `DmcModel` for powdery mildew
- Create `pest_models` + `pest_tracker` tables
- Implement `DegreeDayModel` + daily accumulation
- Add `orchard_blocks` table + CRUD API
- Mobile: Block manager + per-block predictions

### Phase 3: ML + Microclimate (Months 3-6)
**Goal:** Block-level precision + learning from farmer feedback
- Build `MicroclimateService` (slope/aspect adjustments)
- Farmer feedback loop (`is_confirmed` field)
- Simple ML (random forest) on feedback data
- KVK partnership for model validation

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Revised Mills (not RIMpro)** | RIMpro requires hourly rain/RH/light sensors. Mills works with forecast data. Upgrade later. |
| **Leaf wetness ESTIMATED** | Small farmers don't have sensors. We estimate from RH + rain + dew point (~70-80% accuracy). |
| **Regional biofix defaults** | Farmers won't buy pheromone traps. Use altitude-based default dates, allow override. |
| **Rule engine FIRST** | Existing `WeatherIntelligenceService` already works. Enhance it before replacing. |
| **Orchard blocks SEPARATE** | New table, not column on `user_orchards`. Supports multi-orchard, multi-block per user. |
| **Offline-first predictions** | Pre-compute 48h predictions, cache in Redis + mobile MMKV. Himalayan connectivity is poor. |
| **Hindi + English bilingual** | Every alert has `message_hi`. Critical for HP farmer adoption. |

---

## Quick Start for Developer

```bash
# Step 1: Run migrations (Document 01)
cd web_baagicha
php artisan migrate

# Step 2: Seed disease model flags + pest models
php artisan db:seed --class=DiseaseModelSeeder
php artisan db:seed --class=PestModelSeeder

# Step 3: Add scheduled commands to app/Console/Kernel.php (Document 04)
# Step 4: Add API routes to routes/api.php (Document 05)
# Step 5: Copy service classes to app/Services/Prediction/ (Document 03)
# Step 6: Copy controllers to app/Http/Controllers/Api/ (Document 05)
# Step 7: Test with: php artisan app:compute-disease-pressure --dry-run
```

---

## Validation Gate (DO NOT SKIP)

Before trusting predictions for farmer spray decisions:

1. **Shadow Mode (Season 0):** Run predictions internally, compare with KVK expert recommendations
2. **Target:** < 20% false positives, < 5% false negatives
3. **Soft Launch (Season 1):** Label predictions "BETA", heavy feedback collection
4. **Full Launch (Season 2):** Predictions become primary recommendations

**Wrong spray advice = crop loss = trust destroyed forever.**

---

## Related Documents (in DreamBoard)

- `dreamboard/baagvaani/research/competitors/2026-05-20-apple-dss-global-landscape.md` — Full competitor analysis
- `dreamboard/baagvaani/research/tech-stack/2026-05-20-baagvaani-prediction-engine-architecture.md` — Original architecture pseudocode
- `dreamboard/baagvaani/docs/prediction-recommendation-engine.md` — Product concept document

---

*Part of Baagvaani — AI-Powered Apple Orchard Management Platform*
