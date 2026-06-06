# Baagicha — Prediction Engine Mobile Integration

> **Frontend:** React Native 0.85 + TypeScript + Zustand  
> **Status:** Specs ready — backend complete, RN screens pending  
> **Source:** `research/prediction-engine/07_MOBILE_INTEGRATION.md`

---

## TypeScript Types

### Risk Levels & Models

```typescript
export type RiskLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';
export type PredictionModel = 'rule' | 'mills' | 'maryblyt' | 'dmc' | 'dd_model' | 'ml';
```

### Core Interfaces

```typescript
export interface PredictionFactor {
  key: string;
  label: string;
  label_hi: string;
}

export interface InfectionPeriod {
  start: string;           // ISO timestamp
  end: string | 'ongoing';
  hours: number;
  avg_temp: number;
  required_hours: number;
  severity: 'light' | 'moderate' | 'severe';
}

export interface SprayWindow {
  start: string;           // ISO timestamp
  hours: number;
  rating: 'excellent' | 'good' | 'short' | 'insufficient';
  avg_temp: number;
  max_wind: number;
}

export interface SprayRecommendation {
  action_needed: boolean;
  action_en: string;
  action_hi: string;
  chemical: string | null;
  dose: string | null;
  timing: string | null;
  safety_notes: { en: string; hi: string };
}
```

### Prediction Types

```typescript
export interface DiseasePrediction {
  type: 'disease';
  id: number;
  name: string;
  name_hi: string;
  risk_level: RiskLevel;
  risk_score: number;       // 0-100
  model_used: PredictionModel;
  prediction_window: string;
  factors: PredictionFactor[];
  infection_periods?: InfectionPeriod[];
  spray_window: SprayWindow | null;
  recommended_action: string | null;
  recommended_action_hi: string | null;
  action_needed: boolean;
}

export interface PestEvent {
  name: string;
  at_dd: number;
  dd_remaining: number;
}

export interface PestPrediction {
  type: 'pest';
  id: number;
  name: string;
  name_hi: string;
  risk_level: RiskLevel;
  cumulative_dd: number;
  next_event: PestEvent | null;
  estimated_days?: number;
}

export interface WeatherWarning {
  type: 'frost' | 'hail' | 'wind' | 'heat';
  severity: RiskLevel;
  message: string;
  message_hi: string;
}
```

### Response Types

```typescript
export interface PredictionsResponse {
  orchard_id: number;
  date: string;
  generated_at: string;
  cached?: boolean;
  predictions: DiseasePrediction[];
  weather_warnings?: WeatherWarning[];
}

export interface BlockPredictionsResponse {
  orchard_id: number;
  block_id: number;
  block_name: string;
  predictions: DiseasePrediction[];
}
```

### Orchard Block & Spray Log

```typescript
export interface OrchardBlock {
  id: number;
  name: string;
  variety_id?: number;
  variety?: { id: number; name: string; name_hi?: string };
  rootstock_id?: number;
  rootstock?: { id: number; name: string };
  area_kanal?: number;
  plant_count?: number;
  tree_age_years?: number;
  spacing_meters?: string;
  soil_type?: 'loam' | 'clay' | 'sandy' | 'silty' | 'peaty';
  soil_ph?: number;
  irrigation_type?: 'drip' | 'sprinkler' | 'flood' | 'rainfed';
  aspect?: 'north' | 'south' | 'east' | 'west' | 'flat';
  slope_percent?: number;
  is_sunny_exposure: boolean;
  wind_exposure?: 'sheltered' | 'moderate' | 'exposed';
  frost_pocket_risk?: 'low' | 'medium' | 'high';
}

export interface SprayLog {
  id: number;
  spray_date: string;
  spray_time?: string;
  chemical_name: string;
  quantity_used?: number;
  unit?: 'g' | 'ml' | 'kg' | 'L';
  water_used_liters?: number;
  area_covered_kanal?: number;
  weather_condition?: 'sunny' | 'cloudy' | 'windy' | 'rainy';
  notes?: string;
  photos?: string[];
  reward_points: number;
  disease?: { id: number; name: string };
  orchard_block?: { id: number; name: string };
}
```

---

## Zustand Stores

### predictionStore.ts

```typescript
interface PredictionState {
  predictions: DiseasePrediction[];
  pestPredictions: PestPrediction[];
  sprayWindows: SprayWindow[];
  weatherWarnings: WeatherWarning[];
  isLoadingPredictions: boolean;
  isLoadingSprayWindow: boolean;
  lastUpdated: string | null;
  orchardId: number | null;

  fetchPredictions: (orchardId: number) => Promise<void>;
  fetchPestPredictions: (orchardId: number) => Promise<void>;
  fetchSprayWindow: (orchardId: number) => Promise<void>;
  submitFeedback: (predictionId: number, wasCorrect: boolean, notes?: string) => Promise<void>;
  refreshAll: (orchardId: number) => Promise<void>;
  clearCache: () => void;
}
```

Persisted in MMKV via Zustand persist middleware. Partialize: predictions, sprayWindows, weatherWarnings, lastUpdated, orchardId.

### orchardBlockStore.ts

```typescript
interface OrchardBlockState {
  blocks: OrchardBlock[];
  isLoading: boolean;
  selectedBlockId: number | null;

  fetchBlocks: (orchardId: number) => Promise<void>;
  createBlock: (orchardId: number, data: Partial<OrchardBlock>) => Promise<void>;
  updateBlock: (orchardId: number, blockId: number, data: Partial<OrchardBlock>) => Promise<void>;
  deleteBlock: (orchardId: number, blockId: number) => Promise<void>;
  selectBlock: (blockId: number | null) => void;
}
```

---

## Screen Specifications

### 1. HomeScreen — Prediction Cards (Update)

Add prediction cards at the **top** of the home screen, above the spray schedule:

```
┌─────────────────────────────────────────┐
│  🌤️ Shimla, HP  |  18°C  |  Safe spray  │  ← existing weather
├─────────────────────────────────────────┤
│  ⚠️ DO NOW (2)                          │  ← NEW
│  ┌─────────────────────────────────┐   │
│  │ 🔴 Apple Scab — HIGH Risk       │   │
│  │ Rain tomorrow. Spray by 10 AM.  │   │
│  │ [View Details] [Mark Sprayed]   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ 🟡 Codling Moth — Approaching   │   │
│  │ Egg hatch in ~5 days. Prepare.  │   │
│  │ [View Details]                  │   │
│  └─────────────────────────────────┘   │
│  📅 NEXT 7 DAYS                         │  ← existing schedule
└─────────────────────────────────────────┘
```

**Risk Level Colors:**

| Level | Background | Text | Icon |
|-------|-----------|------|------|
| `critical` | `#DC2626` | white | 🚨 |
| `high` | `#EA580C` | white | ⚠️ |
| `medium` | `#D97706` | white | 👁️ |
| `low` | `#65A30D` | white | ℹ️ |
| `none` | `#6B7280` | white | ✅ |

### 2. AlertDetailScreen (NEW)

Full-screen detail for a single prediction:
- Disease name + Hindi name
- Risk badge (score 0-100)
- **Why this alert?** — factors list (temp, rain, humidity, altitude)
- **Predicted Infection** — start/end time, wetness hours, severity
- **Recommended Action** — chemical, dose, best spray window
- Safety tips
- Action buttons: `[✅ I sprayed]` `[📅 Remind me later]`
- **Feedback**: `[👍 Yes]` `[👎 No]` `[📝 Add note]`

### 3. WeatherScreen (Update)

Add to existing weather screen:
- Spray safety indicator (`🟢 SAFE TO SPRAY`)
- **Spray Windows** — list with star ratings (⭐⭐⭐ Excellent)
- **48h Forecast** — hourly scrollable chart (temp, rain, humidity, wind)
- **Disease Risk Timeline** — 7-day risk chart

### 4. OrchardBlocksScreen (NEW)

Manage orchard sub-divisions:
- `[+ Add New Block]` button
- Block cards: variety, area, plant count, aspect, irrigation
- Per-block risk badges: `🔴 Scab: HIGH | 🟡 Moth: MED`
- Actions: View / Edit / Delete

### 5. BlockDetailScreen (NEW)

Same layout as AlertDetailScreen but scoped to one block's predictions.

### 6. PredictionFeedbackModal (NEW)

Shown ~10 days after a HIGH/CRITICAL alert:
```
Was the Apple Scab alert helpful?
     [👍 Yes, correct]
     [👎 No, false alarm]

Add note (optional):
┌─────────────────────────────────┐
│ Sprayed but scab still came...  │
└─────────────────────────────────┘

        [Submit Feedback]
```

### 7. SprayLogScreen (NEW)

Farmer spray history with reward points:
```
┌─────────────────────────────────────────┐
│ ← Spray History                         │
├─────────────────────────────────────────┤
│  [+ Log New Spray]                      │
│                                         │
│  May 20 — Copper Oxychloride           │
│  300g/200L | 2.5 kanal | ⛅ Cloudy      │
│  +20 points 🏆                          │
│                                         │
│  May 15 — Mancozeb 75WP                │
│  200g/200L | 2.5 kanal | ☀️ Sunny       │
│  +20 points 🏆                          │
└─────────────────────────────────────────┘
```

---

## API Service Pattern

**File:** `src/services/predictionApi.ts`

```typescript
export const predictionApi = {
  getPredictions: (orchardId: number, date?: string) =>
    api.get<PredictionsResponse>(`/orchard/${orchardId}/predictions`, { params: date ? { date } : undefined }),

  getDiseasePrediction: (orchardId: number, diseaseId: number) =>
    api.get(`/orchard/${orchardId}/predictions/disease/${diseaseId}`),

  getPestPrediction: (orchardId: number, pestModelId: number) =>
    api.get(`/orchard/${orchardId}/predictions/pest/${pestModelId}`),

  getSprayWindow: (orchardId: number) =>
    api.get<{ windows: SprayWindow[]; best_window: SprayWindow | null }>(`/orchard/${orchardId}/spray-window`),

  getDetailedForecast: (orchardId: number) =>
    api.get(`/orchard/${orchardId}/forecast/detailed`),

  submitFeedback: (logId: number, wasCorrect: boolean, notes?: string) =>
    api.post(`/predictions/${logId}/feedback`, { was_correct: wasCorrect, notes }),

  // Blocks
  getBlocks: (orchardId: number) => api.get(`/orchards/${orchardId}/blocks`),
  getBlockPredictions: (orchardId: number, blockId: number) =>
    api.get<BlockPredictionsResponse>(`/orchard/${orchardId}/blocks/${blockId}/predictions`),

  // Spray logs
  getSprayLogs: (orchardId: number, params?: { from?: string; to?: string }) =>
    api.get(`/orchard/${orchardId}/spray-logs`, { params }),
  createSprayLog: (orchardId: number, data: Partial<SprayLog>) =>
    api.post(`/orchard/${orchardId}/spray-logs`, data),
};
```

---

## Push Notification Handling

Update `src/services/notificationService.ts` to handle prediction alerts:

```typescript
export function handleNotification(remoteMessage: FirebaseMessagingTypes.RemoteMessage) {
  const data = remoteMessage.data;
  const type = data?.type;

  switch (type) {
    case 'disease_alert':
      navigationRef.navigate('AlertDetailScreen', { logId: Number(data.logId), diseaseId: Number(data.diseaseId) });
      break;
    case 'pest_alert':
      navigationRef.navigate('PestTrackerScreen', { trackerId: Number(data.trackerId), pestId: Number(data.pestId) });
      break;
    case 'spray_reminder':
      navigationRef.navigate('SprayScheduleScreen', { stageId: Number(data.stageId) });
      break;
  }
}
```

---

## Offline-First Strategy

1. **On app open / pull-to-refresh:**
   - Fetch predictions + spray windows
   - Store in MMKV (via Zustand persist)

2. **Display cached data with timestamp:**
   - "Updated 2 hours ago"
   - If > 6 hours old, show "Pull to refresh"

3. **Actions queue when offline:**
   - Mark sprayed → queue for sync
   - Submit feedback → queue for sync
   - Log spray → queue for sync

4. **Background refresh:**
   - On foreground: check if lastUpdated > 30 min
   - Auto-refresh if needed
