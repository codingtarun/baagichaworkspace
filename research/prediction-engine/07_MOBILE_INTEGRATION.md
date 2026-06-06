# 07 — Mobile App Integration

> **React Native (0.85) + TypeScript + Zustand**
> 
> These are specs for the frontend developer to implement. Not server code.

---

## New TypeScript Types

**File:** `baagvaaniApp/src/types/prediction.ts`

```typescript
// ─── Risk Levels ─────────────────────────────────────────────
export type RiskLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';

export type PredictionModel = 'rule' | 'mills' | 'maryblyt' | 'dmc' | 'dd_model' | 'ml';

// ─── Factor (why the prediction was made) ────────────────────
export interface PredictionFactor {
  key: string;
  label: string;
  label_hi: string;
}

// ─── Infection Period (from Mills/Maryblyt models) ───────────
export interface InfectionPeriod {
  start: string;           // ISO timestamp
  end: string | 'ongoing';
  hours: number;
  avg_temp: number;
  required_hours: number;
  severity: 'light' | 'moderate' | 'severe';
}

// ─── Spray Window ────────────────────────────────────────────
export interface SprayWindow {
  start: string;           // ISO timestamp
  hours: number;
  rating: 'excellent' | 'good' | 'short' | 'insufficient';
  avg_temp: number;
  max_wind: number;
}

// ─── Recommendation ──────────────────────────────────────────
export interface SprayRecommendation {
  action_needed: boolean;
  action_en: string;
  action_hi: string;
  chemical: string | null;
  dose: string | null;
  timing: string | null;
  safety_notes: {
    en: string;
    hi: string;
  };
}

// ─── Disease Prediction ──────────────────────────────────────
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

// ─── Pest Prediction ─────────────────────────────────────────
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

// ─── Weather Warning ─────────────────────────────────────────
export interface WeatherWarning {
  type: 'frost' | 'hail' | 'wind' | 'heat';
  severity: RiskLevel;
  message: string;
  message_hi: string;
}

// ─── Prediction Response ─────────────────────────────────────
export interface PredictionsResponse {
  orchard_id: number;
  date: string;
  generated_at: string;
  cached?: boolean;
  predictions: DiseasePrediction[];
  weather_warnings?: WeatherWarning[];
}

// ─── Block Prediction Response ───────────────────────────────
export interface BlockPredictionsResponse {
  orchard_id: number;
  block_id: number;
  block_name: string;
  predictions: DiseasePrediction[];
}

// ─── Spray Log ───────────────────────────────────────────────
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

// ─── Orchard Block ───────────────────────────────────────────
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
```

---

## Zustand Store: `predictionStore.ts`

**File:** `baagvaaniApp/src/store/predictionStore.ts`

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  DiseasePrediction,
  PestPrediction,
  PredictionsResponse,
  SprayWindow,
  WeatherWarning,
} from '../types/prediction';
import api from '../services/api';

interface PredictionState {
  // Data
  predictions: DiseasePrediction[];
  pestPredictions: PestPrediction[];
  sprayWindows: SprayWindow[];
  weatherWarnings: WeatherWarning[];
  
  // Loading states
  isLoadingPredictions: boolean;
  isLoadingSprayWindow: boolean;
  
  // Metadata
  lastUpdated: string | null;
  orchardId: number | null;
  
  // Actions
  fetchPredictions: (orchardId: number) => Promise<void>;
  fetchPestPredictions: (orchardId: number) => Promise<void>;
  fetchSprayWindow: (orchardId: number) => Promise<void>;
  submitFeedback: (predictionId: number, wasCorrect: boolean, notes?: string) => Promise<void>;
  refreshAll: (orchardId: number) => Promise<void>;
  clearCache: () => void;
}

export const usePredictionStore = create<PredictionState>()(
  persist(
    (set, get) => ({
      predictions: [],
      pestPredictions: [],
      sprayWindows: [],
      weatherWarnings: [],
      isLoadingPredictions: false,
      isLoadingSprayWindow: false,
      lastUpdated: null,
      orchardId: null,

      fetchPredictions: async (orchardId: number) => {
        set({ isLoadingPredictions: true, orchardId });
        try {
          const response = await api.get<PredictionsResponse>(`/orchard/${orchardId}/predictions`);
          set({
            predictions: response.data.predictions,
            weatherWarnings: response.data.weather_warnings || [],
            lastUpdated: response.data.generated_at,
            isLoadingPredictions: false,
          });
        } catch (error) {
          set({ isLoadingPredictions: false });
          throw error;
        }
      },

      fetchPestPredictions: async (orchardId: number) => {
        // Fetch pest trackers and transform to predictions
        // Implementation depends on your API structure
      },

      fetchSprayWindow: async (orchardId: number) => {
        set({ isLoadingSprayWindow: true });
        try {
          const response = await api.get(`/orchard/${orchardId}/spray-window`);
          set({
            sprayWindows: response.data.windows || [],
            isLoadingSprayWindow: false,
          });
        } catch (error) {
          set({ isLoadingSprayWindow: false });
          throw error;
        }
      },

      submitFeedback: async (predictionId: number, wasCorrect: boolean, notes?: string) => {
        await api.post(`/predictions/${predictionId}/feedback`, {
          was_correct: wasCorrect,
          notes,
        });
      },

      refreshAll: async (orchardId: number) => {
        await Promise.all([
          get().fetchPredictions(orchardId),
          get().fetchSprayWindow(orchardId),
        ]);
      },

      clearCache: () => {
        set({
          predictions: [],
          pestPredictions: [],
          sprayWindows: [],
          weatherWarnings: [],
          lastUpdated: null,
        });
      },
    }),
    {
      name: 'prediction-store',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        predictions: state.predictions,
        sprayWindows: state.sprayWindows,
        weatherWarnings: state.weatherWarnings,
        lastUpdated: state.lastUpdated,
        orchardId: state.orchardId,
      }),
    }
  )
);
```

---

## Zustand Store: `orchardBlockStore.ts`

**File:** `baagvaaniApp/src/store/orchardBlockStore.ts`

```typescript
import { create } from 'zustand';
import { OrchardBlock } from '../types/prediction';
import api from '../services/api';

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

export const useOrchardBlockStore = create<OrchardBlockState>((set, get) => ({
  blocks: [],
  isLoading: false,
  selectedBlockId: null,

  fetchBlocks: async (orchardId: number) => {
    set({ isLoading: true });
    try {
      const response = await api.get(`/orchards/${orchardId}/blocks`);
      set({ blocks: response.data.blocks, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createBlock: async (orchardId: number, data: Partial<OrchardBlock>) => {
    const response = await api.post(`/orchards/${orchardId}/blocks`, data);
    set({ blocks: [...get().blocks, response.data.block] });
  },

  updateBlock: async (orchardId: number, blockId: number, data: Partial<OrchardBlock>) => {
    const response = await api.put(`/orchards/${orchardId}/blocks/${blockId}`, data);
    set({
      blocks: get().blocks.map((b) =>
        b.id === blockId ? response.data.block : b
      ),
    });
  },

  deleteBlock: async (orchardId: number, blockId: number) => {
    await api.delete(`/orchards/${orchardId}/blocks/${blockId}`);
    set({ blocks: get().blocks.filter((b) => b.id !== blockId) });
  },

  selectBlock: (blockId: number | null) => {
    set({ selectedBlockId: blockId });
  },
}));
```

---

## Screen Specifications

### 1. `HomeScreen` — Prediction Cards (Update)

**File:** Update existing `baagvaaniApp/src/screens/HomeScreen.tsx`

Add prediction cards at the top of the home screen:

```
┌─────────────────────────────────────────┐
│  🌤️ Shimla, HP  |  18°C  |  Safe spray  │  ← existing weather strip
├─────────────────────────────────────────┤
│                                         │
│  ⚠️ DO NOW (2)                          │  ← NEW: Action cards
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
│                                         │
│  📅 NEXT 7 DAYS                         │  ← existing spray schedule
│  ...                                    │
└─────────────────────────────────────────┘
```

**Card Component:** `src/components/PredictionCard.tsx`

```typescript
interface PredictionCardProps {
  prediction: DiseasePrediction;
  onPress: () => void;
  onMarkSprayed: () => void;
}
```

**Risk Level Colors:**
| Level | Background | Text | Icon |
|-------|-----------|------|------|
| `critical` | `#DC2626` (red-600) | white | 🚨 |
| `high` | `#EA580C` (orange-600) | white | ⚠️ |
| `medium` | `#D97706` (amber-600) | white | 👁️ |
| `low` | `#65A30D` (lime-600) | white | ℹ️ |
| `none` | `#6B7280` (gray-500) | white | ✅ |

---

### 2. `AlertDetailScreen` (NEW)

**File:** `baagvaaniApp/src/screens/AlertDetailScreen.tsx`

```
┌─────────────────────────────────────────┐
│ ← Back                                  │
├─────────────────────────────────────────┤
│                                         │
│  🍎 Apple Scab                          │
│  सेब की छाई                             │
│                                         │
│  [🔴 HIGH RISK — 75/100]               │
│                                         │
│  ── Why this alert? ────────────────── │
│  🌡️ Temperature 18°C (optimal)          │
│  🌧️ Rain forecast tomorrow              │
│  💧 Humidity will reach 85%             │
│  ⛰️  Your altitude matches scab range   │
│                                         │
│  ── Predicted Infection ────────────── │
│  Tomorrow 2 PM → Day after 8 AM        │
│  Wetness: 18 hours at 16°C             │
│  Severity: MODERATE                     │
│                                         │
│  ── Recommended Action ─────────────── │
│  Spray Copper Oxychloride 50WP          │
│  750g (2.5 acres, 500L water)           │
│                                         │
│  Best window: Tomorrow 6-10 AM         │
│  Wind 8 km/h, No rain, 16°C            │
│                                         │
│  [🧤 Safety tips]                       │
│                                         │
│  [✅ I sprayed]  [📅 Remind me later]  │
│                                         │
│  ── Was this alert correct? ────────── │
│  [👍 Yes]  [👎 No]  [📝 Add note]      │
│                                         │
└─────────────────────────────────────────┘
```

---

### 3. `WeatherScreen` (NEW or Update)

**File:** `baagvaaniApp/src/screens/WeatherScreen.tsx`

Show detailed weather + spray safety indicator:

```
┌─────────────────────────────────────────┐
│ 🌤️ Weather | Shimla                     │
├─────────────────────────────────────────┤
│                                         │
│  [Big weather widget]                   │
│  18°C | Cloudy | Humidity 75%           │
│                                         │
│  [🟢 SAFE TO SPRAY]                    │
│  Wind 8 km/h | No rain | 16°C           │
│  Next unsafe: Tomorrow 2 PM             │
│                                         │
│  ── Spray Windows ──────────────────── │
│  Today 6AM-12PM  ⭐⭐⭐ Excellent       │
│  Tomorrow 6AM-10AM ⭐⭐ Good            │
│                                         │
│  ── 48h Forecast ───────────────────── │
│  [Hourly scrollable chart]              │
│  Temp | Rain | Humidity | Wind          │
│                                         │
│  ── Disease Risk Timeline ──────────── │
│  [Chart showing risk over next 7 days] │
│                                         │
└─────────────────────────────────────────┘
```

---

### 4. `OrchardBlocksScreen` (NEW)

**File:** `baagvaaniApp/src/screens/OrchardBlocksScreen.tsx`

```
┌─────────────────────────────────────────┐
│ ← My Orchard | Blocks                   │
├─────────────────────────────────────────┤
│                                         │
│  [+ Add New Block]                      │
│                                         │
│  ── Block A ────────────────────────── │
│  Variety: Red Delicious                 │
│  Area: 1.5 kanal | Plants: 45           │
│  South-facing, drip irrigation          │
│  🔴 Scab: HIGH | 🟡 Moth: MED           │
│  [View] [Edit] [Delete]                 │
│                                         │
│  ── Block B (Valley) ───────────────── │
│  Variety: Granny Smith                  │
│  Area: 1.0 kanal | Plants: 30           │
│  North-facing, sprinkler                │
│  🟢 Scab: LOW | 🟢 Moth: NONE           │
│  [View] [Edit] [Delete]                 │
│                                         │
└─────────────────────────────────────────┘
```

---

### 5. `BlockDetailScreen` (NEW)

**File:** `baagvaaniApp/src/screens/BlockDetailScreen.tsx`

Show block profile + per-block predictions. Same layout as `AlertDetailScreen` but scoped to one block.

---

### 6. `PredictionFeedbackModal` (NEW)

**File:** `baagvaaniApp/src/components/PredictionFeedbackModal.tsx`

Shown 10 days after a HIGH/CRITICAL alert:

```
┌─────────────────────────────────────────┐
│                                         │
│  Was the Apple Scab alert helpful?      │
│                                         │
│     [👍 Yes, correct]                   │
│     [👎 No, false alarm]                │
│                                         │
│  Add note (optional):                   │
│  ┌─────────────────────────────────┐   │
│  │ Sprayed but scab still came...  │   │
│  └─────────────────────────────────┘   │
│                                         │
│        [Submit Feedback]                │
│                                         │
└─────────────────────────────────────────┘
```

---

### 7. `SprayLogScreen` (NEW)

**File:** `baagvaaniApp/src/screens/SprayLogScreen.tsx`

```
┌─────────────────────────────────────────┐
│ ← Spray History                         │
├─────────────────────────────────────────┤
│                                         │
│  [+ Log New Spray]                      │
│                                         │
│  May 20 — Copper Oxychloride           │
│  300g/200L | 2.5 kanal | ⛅ Cloudy      │
│  +20 points 🏆                          │
│                                         │
│  May 15 — Mancozeb 75WP                │
│  200g/200L | 2.5 kanal | ☀️ Sunny       │
│  +20 points 🏆                          │
│                                         │
└─────────────────────────────────────────┘
```

---

## Push Notification Handling

**File:** Update `baagvaaniApp/src/services/notificationService.ts`

```typescript
// Handle incoming push notifications
export function handleNotification(remoteMessage: FirebaseMessagingTypes.RemoteMessage) {
  const data = remoteMessage.data;
  const type = data?.type;

  switch (type) {
    case 'disease_alert':
      navigationRef.navigate('AlertDetailScreen', {
        logId: Number(data.logId),
        diseaseId: Number(data.diseaseId),
      });
      break;

    case 'pest_alert':
      navigationRef.navigate('PestTrackerScreen', {
        trackerId: Number(data.trackerId),
        pestId: Number(data.pestId),
      });
      break;

    case 'spray_reminder':
      navigationRef.navigate('SprayScheduleScreen', {
        stageId: Number(data.stageId),
      });
      break;
  }
}
```

---

## Offline-First Strategy

```
1. On app open / pull-to-refresh:
   - Fetch predictions + spray windows
   - Store in MMKV (via Zustand persist)

2. Display cached data with timestamp:
   - "Updated 2 hours ago" 
   - If > 6 hours old, show "Pull to refresh"

3. Actions queue when offline:
   - Mark sprayed → queue for sync
   - Submit feedback → queue for sync
   - Log spray → queue for sync

4. Background refresh (when app returns to foreground):
   - Check if lastUpdated > 30 min ago
   - Auto-refresh if needed
```

---

## API Service Pattern

**File:** `baagvaaniApp/src/services/predictionApi.ts`

```typescript
import api from './api';
import {
  PredictionsResponse,
  BlockPredictionsResponse,
  SprayWindow,
  SprayLog,
} from '../types/prediction';

export const predictionApi = {
  getPredictions: (orchardId: number, date?: string) =>
    api.get<PredictionsResponse>(`/orchard/${orchardId}/predictions`, {
      params: date ? { date } : undefined,
    }),

  getDiseasePrediction: (orchardId: number, diseaseId: number) =>
    api.get(`/orchard/${orchardId}/predictions/disease/${diseaseId}`),

  getPestPrediction: (orchardId: number, pestModelId: number) =>
    api.get(`/orchard/${orchardId}/predictions/pest/${pestModelId}`),

  getSprayWindow: (orchardId: number) =>
    api.get<{ windows: SprayWindow[]; best_window: SprayWindow | null }>(
      `/orchard/${orchardId}/spray-window`
    ),

  getDetailedForecast: (orchardId: number) =>
    api.get(`/orchard/${orchardId}/forecast/detailed`),

  submitFeedback: (logId: number, wasCorrect: boolean, notes?: string) =>
    api.post(`/predictions/${logId}/feedback`, { was_correct: wasCorrect, notes }),

  // Blocks
  getBlocks: (orchardId: number) =>
    api.get(`/orchards/${orchardId}/blocks`),

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

*Next: Read `08_IMPLEMENTATION_ROADMAP.md` for week-by-week plan.*
