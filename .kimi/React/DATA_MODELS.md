# Baagicha — Complete Data Models

> **Architecture:** APIs live in Laravel (`web_baagicha/`). React Native (`baagichaApp/`) is the pure frontend client.
> **Updated:** 2026-06-06 — added prediction engine, orchard blocks, feed/post types, auth user
> All TypeScript interfaces for the React Native app. Data is served by Laravel APIs.

---

## 1. Growth Stage

```typescript
interface GrowthStage {
  /** English stage name */
  name: string;
  /** Hindi stage name */
  nameHi: string;
  /** FontAwesome icon class */
  icon: string;
  /** Date range string */
  period: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Next stage English name */
  nextStage: string;
  /** Next stage Hindi name */
  nextStageHi: string;
}
```

---

## 2. Task / Spray Item

```typescript
interface TaskItem {
  /** English name */
  name: string;
  /** Hindi name */
  nameHi: string;
  /** URL slug for detail page */
  slug: string | null;
  /** Dose instruction */
  dose: string | null;
  /** When to apply */
  when: string;
  /** Hindi timing instruction */
  whenHi: string;
  /** What disease/pest it targets */
  target: string;
  /** Available brands */
  brands: Brand[] | null;
  /** Priority level */
  priority: 'essential' | 'recommended' | 'conditional';
  /** Pre-Harvest Interval in days (null if not applicable) */
  phi: number | null;
  /** FontAwesome icon class */
  icon: string;
}

interface Brand {
  name: string;
  slug: string | null;
}
```

---

## 3. Disease Watch Item

```typescript
interface DiseaseWatchItem {
  /** English disease name */
  name: string;
  /** Hindi disease name */
  nameHi: string;
  /** URL slug for detail page */
  slug: string | null;
  /** Type of threat */
  type: 'fungal' | 'pest' | 'bacterial';
  /** Risk level */
  risk: 'high' | 'medium' | 'low';
  /** Advisory note */
  note: string;
  /** Hindi advisory note */
  noteHi: string;
}
```

---

## 4. Soil Nutrition Item

```typescript
interface SoilNutritionItem {
  /** Nutrient name */
  name: string;
  /** Hindi name */
  nameHi: string;
  /** Application dose */
  dose: string;
  /** Application method */
  method: string;
  /** Hindi method */
  methodHi: string;
  /** Timing instruction */
  timing: string;
  /** FontAwesome icon */
  icon: string;
}
```

---

## 5. Weather Warning

```typescript
interface WeatherWarning {
  /** Warning type */
  type: 'frost' | 'hail' | 'heavy_rain' | 'strong_wind' | 'generic';
  /** Warning message */
  message: string;
  /** Severity level */
  severity: 'critical' | 'high' | 'medium' | 'low';
}
```

---

## 6. Preventive Alert

```typescript
interface PreventiveAlert {
  /** FontAwesome icon class */
  icon: string;
  /** English title */
  title: string;
  /** Hindi title */
  titleHi: string;
  /** Description */
  desc: string;
  /** Severity: critical | high | medium | low */
  sev: 'critical' | 'high' | 'medium' | 'low';
}
```

---

## 7. Outbreak Alert

```typescript
interface OutbreakAlert {
  /** Location string */
  location: string;
  /** Disease name English */
  disease: string;
  /** Disease name Hindi */
  diseaseHi: string;
  /** Number of farmer reports */
  reports: number;
  /** Time ago string */
  when: string;
  /** Severity */
  sev: 'critical' | 'high' | 'medium';
  /** Action tip */
  tip: string;
}
```

---

## 8. Variety Card

```typescript
interface Variety {
  /** English name */
  name: string;
  /** Hindi name */
  nameHi: string;
  /** Altitude range */
  altitude: string;
  /** Number of farmer votes */
  votes: number;
  /** Rating out of 5 */
  rating: number;
  /** Card accent color */
  color: string;
  /** Tag label */
  tag: string;
  /** Optional season for filtering */
  season?: string;
}
```

---

## 9. Rootstock Card

```typescript
interface Rootstock {
  /** Name */
  name: string;
  /** Hindi name */
  nameHi: string;
  /** Type (Dwarfing, Semi-dwarfing, etc.) */
  type: string;
  /** Planting spacing */
  spacing: string;
  /** Number of farmer votes */
  votes: number;
  /** Rating out of 5 */
  rating: number;
  /** Card accent color */
  color: string;
  /** Tag label */
  tag: string;
  /** Optional vigour for filtering */
  vigour?: string;
}
```

---

## 10. Blog Card

```typescript
interface BlogPost {
  /** Article title */
  title: string;
  /** Hindi title */
  titleHi: string;
  /** Category name */
  category: string;
  /** Category badge color */
  catColor: string;
  /** Read time in minutes */
  readMin: number;
  /** View count */
  views: number;
  /** Like count */
  likes: number;
  /** Author name */
  author: string;
  /** Publish date string */
  date: string;
  /** Optional excerpt */
  excerpt?: string;
}
```

---

## 11. Contributor

```typescript
interface Contributor {
  /** Full name */
  name: string;
  /** Hindi name */
  nameHi: string;
  /** Location with altitude */
  location: string;
  /** Initials for avatar */
  initials: string;
  /** Avatar border/accent color */
  color: string;
  /** Total points */
  points: number;
  /** Badge label */
  badge: string;
  /** Number of disease reports */
  reports: number;
  /** Number of reviews */
  reviews: number;
  /** Number of photos uploaded */
  photos: number;
}
```

---

## 12. Forecast Day

```typescript
interface ForecastDay {
  /** Day name in Hindi */
  day: string;
  /** Day name in English */
  dayEn: string;
  /** Date string */
  date: string;
  /** Weather FontAwesome icon */
  icon: string;
  /** Icon color */
  iconColor: string;
  /** High temperature */
  high: string;
  /** Low temperature */
  low: string;
  /** Wind speed km/h */
  wind: string;
  /** Rain probability % */
  rain: string;
  /** Spray suitability */
  suit: 'perfect' | 'caution' | 'avoid';
  /** Suitability label English */
  suitLabel: string;
  /** Suitability label Hindi */
  suitHi: string;
}
```

---

## 13. Priority Meta

```typescript
interface PriorityMeta {
  label: string;
  color: string;
}

const priorityMeta: Record<string, PriorityMeta> = {
  essential: { label: 'Essential', color: '#dc2626' },
  recommended: { label: 'Recommended', color: '#f59e0b' },
  conditional: { label: 'If Needed', color: '#60a5fa' },
};
```

---

## 14. Severity Colors Map

```typescript
const sevColors: Record<string, string> = {
  critical: '#dc2626',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#22c55e',
};
```

---

## 15. Spray Suitability Config

```typescript
interface SuitConfig {
  icon: string;
  className: string;
  label: string;
}

const suitConfig: Record<string, SuitConfig> = {
  perfect: { icon: 'fas fa-check-circle', className: 'suit-perfect', label: 'Good for Spray' },
  caution: { icon: 'fas fa-exclamation-triangle', className: 'suit-caution', label: 'Use Caution' },
  avoid: { icon: 'fas fa-times-circle', className: 'suit-avoid', label: 'Avoid Spray' },
};
```

---

## 16. Navigation Item

```typescript
interface NavItem {
  /** Route name for navigation */
  route: string;
  /** English label */
  label: string;
  /** Hindi label */
  labelHi: string;
  /** Accessibility title */
  title: string;
  /** MaterialCommunityIcons name */
  icon: string;
}
```

**Current Tab Navigation:**
```typescript
const navItems: NavItem[] = [
  { route: 'Home', label: 'Home', labelHi: 'होम', title: 'Home', icon: 'home' },
  { route: 'Spray', label: 'Spray', labelHi: 'स्प्रे', title: 'Spray Schedule', icon: 'spray-bottle' },
  { route: 'Shop', label: 'Shop', labelHi: 'दुकान', title: 'Shop', icon: 'store' },
  { route: 'Discover', label: 'Discover', labelHi: 'खोजें', title: 'Discover', icon: 'compass' },
  { route: 'MyOrchard', label: 'My Orchard', labelHi: 'मेरा बाग', title: 'My Orchard', icon: 'tree' },
];
```

---

## 17. Weather Header Data

```typescript
interface HeaderWeather {
  /** Location name */
  location: string;
  /** Current temperature */
  temperature: string;
  /** Weather condition description */
  weatherCondition: string;
  /** Spray status message */
  sprayStatus: string;
  /** Days until bloom */
  daysToBloom: string;
  /** Number of pending sprays */
  pendingSprays: string;
  /** Mandi price trend */
  mandiTrend: string;
}
```

---

## 18. Orchard

```typescript
interface Orchard {
  id: number;
  orchard_name: string;
  village: string;
  district: string;
  location: string;
  is_primary: boolean;
}
```

---

## 19. Auth User

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  avatar?: string;
  location?: string;
  points?: number;
  badge?: string;
}
```

---

## 20. Feed / Post (Community Segment)

```typescript
interface Post {
  id: number;
  author: {
    name: string;
    avatar?: string;
    initials: string;
    color: string;
  };
  content: string;
  content_hi?: string;
  images?: string[];
  likes: number;
  comments: number;
  shares: number;
  isLiked: boolean;
  createdAt: string;
  type: 'post' | 'question' | 'expert_tip';
  tags?: string[];
}

interface Question {
  id: number;
  author: {
    name: string;
    initials: string;
    color: string;
  };
  title: string;
  title_hi?: string;
  excerpt: string;
  answers: number;
  isResolved: boolean;
  createdAt: string;
}

interface ExpertProfile {
  id: number;
  name: string;
  name_hi?: string;
  specialization: string;
  location: string;
  rating: number;
  reviews: number;
  avatar?: string;
}
```

---

## 21. Prediction Engine Types

> Full spec in `PREDICTION_TYPES.md`. Summaries here for quick reference.

```typescript
export type RiskLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';
export type PredictionModel = 'rule' | 'mills' | 'maryblyt' | 'dmc' | 'dd_model' | 'ml';

export interface PredictionFactor {
  key: string;
  label: string;
  label_hi: string;
}

export interface InfectionPeriod {
  start: string;
  end: string | 'ongoing';
  hours: number;
  avg_temp: number;
  required_hours: number;
  severity: 'light' | 'moderate' | 'severe';
}

export interface SprayWindow {
  start: string;
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

---

## 22. Orchard Block

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
```

---

## 23. Spray Log

```typescript
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

*All interfaces extracted from Laravel Blade templates + mobile implementation + prediction engine research.*
