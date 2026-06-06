# 08 — Implementation Roadmap

> **Week-by-week checklist with acceptance criteria.**

---

## Phase 1: Enhanced Rules + Forecast (Weeks 1-3)

### Week 1: Database + Models

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1 | Run migration `000001_create_orchard_blocks_table` | Table exists with all columns + indexes |
| 1 | Run migration `000002_create_pest_models_table` | Table exists |
| 1 | Run migration `000003_create_pest_tracker_table` | Table exists with unique constraint |
| 1 | Run migration `000004_create_disease_pressure_log_table` | Table exists with indexes |
| 2 | Run migration `000005_add_model_fields_to_diseases_table` | Columns added, existing data intact |
| 2 | Run migration `000006_add_forecast_fields_to_weather_table` | Columns added |
| 2 | Run migration `000007_create_spray_logs_table` | Table exists |
| 3 | Create `OrchardBlock` model | Relationships work, `getMicroclimateAdjustments()` returns correct values |
| 3 | Create `PestModel` model | `getDefaultBiofixDate()` returns correct dates per altitude |
| 3 | Create `PestTracker` model | Scope `forSeason()` works |
| 4 | Create `DiseasePressureLog` model | Scope `pendingFeedback()` works |
| 4 | Create `SprayLog` model | Relationships work |
| 4 | Extend `Disease` model | New casts + `withPredictionModels()` scope works |
| 5 | Extend `UserOrchard` model | `altitude_band` attribute works, new relationships work |
| 5 | Create `DiseaseModelSeeder` | Run `db:seed`, Mills/Maryblyt/DMC flags set correctly |
| 5 | Create `PestModelSeeder` | Run `db:seed`, 3 pests inserted with correct DD targets |

**Week 1 Gate:** All migrations run clean on production-like data. Models pass basic unit tests.

---

### Week 2: Services (Rule-Based)

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1 | Create `AbstractPredictionModel` | `scoreToLevel()` mapping correct |
| 1 | Create `RuleBasedModel` | For test weather (18°C, 85% RH, rain), returns score ≥ 60 for scab |
| 2 | Create `ModelFactory` | `forDisease()` auto-selects correct model |
| 2 | Create `SprayWindowService` | `evaluateWindows()` finds windows in test forecast |
| 2 | Create `LeafWetnessEstimator` | `fetchHourlyForecast()` returns array with >40 hourly items |
| 3 | Create `RecommendationGenerator` | Returns Hindi + English recommendations |
| 3 | Create `DiseasePressureService` | `computeForOrchard()` saves logs to DB |
| 4 | Wire `DiseasePressureService` into existing weather update flow | Every weather update triggers prediction computation |
| 4 | Test with 5 real orchards | All get predictions, no errors in logs |
| 5 | Cache predictions in Redis | `/api/orchard/{id}/predictions` returns in < 200ms |

**Week 2 Gate:** Call API `/api/orchard/1/predictions` and get valid JSON with risk scores.

---

### Week 3: API + Mobile Phase 1

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1 | Create `PredictionController` | All 6 methods return valid JSON |
| 1 | Add API routes | `php artisan route:list` shows all prediction routes |
| 2 | Create `OrchardBlockController` | CRUD works via Postman |
| 2 | Add block API routes | All resource routes registered |
| 3 | Mobile: Update `HomeScreen` with prediction cards | Cards show risk levels with correct colors |
| 3 | Mobile: Create `PredictionCard` component | Tappable, shows action buttons |
| 4 | Mobile: Create `AlertDetailScreen` | Shows all prediction fields |
| 4 | Mobile: Create `predictionStore` (Zustand) | Fetch + cache works, offline shows cached data |
| 5 | Mobile: Create `WeatherScreen` | Spray safety indicator works |
| 5 | Integration test: End-to-end flow | Alert generated → push sent → mobile displays → feedback submitted |

**Phase 1 Gate:** Farmer can open app, see risk cards, tap for details, see spray recommendation.

---

## Phase 2: Epidemiological Models (Weeks 4-8)

### Week 4: Mills Model (Apple Scab)

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1-2 | Create `RevisedMillsModel` | Test with known infection period → returns `moderate`/`severe` |
| 3 | Integrate Mills into `DiseasePressureService` | Scab predictions now use Mills, others use rules |
| 4 | Test against HP weather data | Model detects infection periods in March-May rainy days |
| 5 | Mobile: Show infection periods in `AlertDetailScreen` | Timeline chart renders |

---

### Week 5: Maryblyt + DMC Models

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1-2 | Create `SimplifiedMaryblytModel` | During bloom season + warm rain → returns `high` |
| 3 | Create `DmcModel` | High RH + 20°C → returns `medium`/`high` |
| 4 | Integrate both into `DiseasePressureService` | Fire blight and powdery mildew use correct models |
| 5 | Update `DiseaseModelSeeder` with proper thresholds | All 3 diseases seeded correctly |

---

### Week 6: Pest Tracking

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1 | Create `DegreeDayModel` | DD accumulation math verified against WSU tables |
| 2 | Create `PestDevelopmentService` | `accumulateDaily()` updates tracker cumulative_dd |
| 3 | Create `InitializePestSeason` command | Running it creates trackers for all active orchards |
| 4 | Create `AccumulatePestDegreeDays` command | Daily cron updates all trackers |
| 5 | Add pest routes to API | `GET /api/orchard/{id}/predictions/pest/{id}` works |
| 5 | Mobile: Add pest cards to home screen | Shows DD progress + next event countdown |

---

### Week 7: Blocks + Microclimate

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1-2 | Create `OrchardBlocksScreen` | List, create, edit, delete blocks |
| 2 | Create `BlockDetailScreen` | Shows block profile + per-block predictions |
| 3 | Mobile: `orchardBlockStore` | Zustand store manages block state |
| 4 | Backend: `computeForBlocks()` in `DiseasePressureService` | Different blocks get different scores |
| 4 | Create `MicroclimateService` | Adjusts humidity/wind based on block attributes |
| 5 | Integration: Block-level predictions flow | User sees different alerts for Block A vs Block B |

---

### Week 8: Spray Logs + Polish

| Day | Task | Acceptance Criteria |
|-----|------|---------------------|
| 1 | Create `SprayLogController` | Create + list spray logs |
| 1 | Create `SprayLogScreen` | Shows history, +20 points per log |
| 2 | Mobile: "Mark Sprayed" action | Creates spray log from prediction card |
| 3 | Mobile: `PredictionFeedbackModal` | Shows 10 days after HIGH alert |
| 4 | Backend: `feedback` endpoint | Updates `is_confirmed` + `farmer_feedback` |
| 4 | Performance: Add Redis caching | All prediction APIs < 150ms |
| 5 | QA: Test with 10 real farmers | No crashes, predictions make sense |

**Phase 2 Gate:** System predicts scab infection periods, tracks pest DD, supports blocks.

---

## Phase 3: ML + Microclimate Intelligence (Months 3-6)

### Month 3: Feedback Loop

- [ ] Collect 1 season of feedback data
- [ ] Build admin dashboard showing feedback stats
- [ ] Adjust thresholds per district based on feedback

### Month 4-5: Simple ML

- [ ] Export feedback data to CSV
- [ ] Train random forest / XGBoost model
- [ ] Features: altitude, variety, temp, RH, rain, wind, month
- [ ] Target: binary (disease occurred / didn't occur)
- [ ] A/B test: ML predictions vs rule-based

### Month 6: KVK Validation

- [ ] Partner with KVK Sharbo or Kotkhai
- [ ] Joint validation study
- [ ] Compare Baagvaani predictions vs KVK expert recommendations
- [ ] Adjust models based on findings
- [ ] Publish joint report (marketing + credibility)

---

## Daily Checklist During Implementation

```
□ Did I write a test for this?
□ Did I add Hindi translation?
□ Did I handle the offline case?
□ Did I add logging for errors?
□ Did I check for N+1 queries?
□ Did I run php artisan optimize after changes?
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Weather API fails | Cache last forecast, show "Updated X hours ago" |
| Model gives wrong prediction | Shadow mode for 1 season before farmer-facing |
| Farmer confused by risk scores | Show explanations in Hindi, use emojis |
| Too many notifications | Deduplication: 24h cooldown per disease |
| Block-level too complex initially | Default to orchard-level, opt-in for blocks |

---

*Next: Read `09_GLOBAL_DSS_RESEARCH_SUMMARY.md` for competitive context.*
