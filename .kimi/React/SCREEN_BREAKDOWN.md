# Baagicha — Screen Breakdown

> **Architecture:** APIs live in Laravel (`web_baagicha/`). React Native (`baagichaApp/`) is the pure frontend client.
> **Updated:** 2026-06-06 — merged prediction engine, kisan tools, segmented home, new nav tabs
> All data is fetched from Laravel API endpoints.

---

## Tab Structure

```
MainTabs (Bottom Nav)
├── Home          ← Segmented: My Farm / Community
├── Spray         ← Spray Schedule
├── Shop          ← eCommerce (Phase 1)
├── Discover      ← Disease / Varieties / Rootstocks / Blog / Tools
└── MyOrchard     ← Orchards / Blocks / Spray Logs / Predictions
```

Old tabs retired: Disease → inside Discover; Varieties → inside Discover; Rootstock → inside Discover.

---

## 1. Home Screen

**Route:** `Home` (tab)  
**File:** `src/screens/HomeScreen.tsx`  
**Type:** Segmented dual-mode screen

### Segmented Control
- **My Farm** (default) — dashboard view
- **Community** — social feed view
- On focus, resets to "My Farm"

### 1A. My Farm Segment (`MyFarmSegment`)

```
┌─────────────────────────────────────────┐
│  🌤️ Shimla, HP  |  18°C  |  Safe spray  │  ← weather header
├─────────────────────────────────────────┤
│  ⚠️ DO NOW (2)                          │  ← prediction alerts
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
│  📅 NEXT 7 DAYS                         │  ← spray schedule
│  ┌─────────────────────────────────┐   │
│  │ ☀️ Mar 20  |  Good for Spray    │   │
│  │ ☁️ Mar 21  |  Use Caution       │   │
│  └─────────────────────────────────┘   │
│  📋 TODAY'S TASKS                       │  ← task list
│  ✓ Copper Oxychloride (Essential)      │
│  ○ Mancozeb 75WP (Recommended)         │
└─────────────────────────────────────────┘
```

**Components:**
- `HeroCard` — Stage name, Hindi, progress bar, period, spray suitability
- `StatMiniCards` — 2-col: temp/location, spray status
- `PredictionAlertCard` — Risk badge, disease name, action, buttons
- `ForecastStrip` — 4-day horizontal scroll
- `WeeklyTasks` — Tab bar: Spray | Nutrition | Cultural
- `SpraySuitabilityTimeline` — 7-day spray status

### 1B. Community Segment (`CommunitySegment`)

```
┌─────────────────────────────────────────┐
│  ✏️ What's on your mind?               │  ← post composer
│  [📷 Photo] [❓ Question] [💡 Expert]    │
├─────────────────────────────────────────┤
│  👤 Ramesh N. · 2h ago                 │  ← feed post
│  Scab outbreak in my orchard. Anyone    │
│  else seeing this in Shimla?            │
│  [❤️ 12] [💬 4] [↗️ Share]             │
├─────────────────────────────────────────┤
│  ❓ Questions                           │
│  "Best fungicide for scab right now?"   │
│  [3 answers] · not resolved             │
├─────────────────────────────────────────┤
│  👨‍🔬 Experts                            │
│  Dr. Sharma · Plant Pathologist         │
│  ⭐ 4.8 (23 reviews)                    │
├─────────────────────────────────────────┤
│  👥 Groups                              │
│  HP Apple Growers · 1,240 members       │
└─────────────────────────────────────────┘
```

**Components:**
- `PostComposer` — Quick action bar
- `FeedPostCard` — Author, content, images, engagement stats
- `QuestionCard` — Title, excerpt, answer count, resolved badge
- `ExpertCard` — Name, specialization, rating, reviews
- `GroupCard` — Name, member count

---

## 2. Spray Schedule Screen

**Route:** `Spray` (tab)  
**File:** `src/screens/SprayScreen.tsx`

### Components:
- Stage hero with fruit image
- Fruit selector tabs
- Region tabs (HP / UK / J&K)
- Stage track / timeline
- Chemical panels (priority sections)
- Tank calculator
- Safety card
- Hail card
- Tips panel
- Share row
- Floating action button

---

## 3. Shop Screen

**Route:** `Shop` (tab)  
**File:** `src/screens/ShopScreen.tsx`  
**Status:** Phase 1 — catalog + cart

### Components:
- Category pills
- Product cards (image, name, price, rating)
- Product detail screen
- Cart screen
- Checkout flow

> Full roadmap: `../ECOMMERCE_PLAN.md`

---

## 4. Discover Screen

**Route:** `Discover` (tab)  
**File:** `src/screens/DiscoverScreen.tsx`

### Sections (scrollable):
- **Disease Library** — Filter pills (All/Fungal/Pest/Bacterial), disease cards with image, detail with Symptoms/Prevention/Treatment tabs
- **Variety Guide** — Filter by season, variety cards, detail with altitude chart, characteristics, ratings
- **Rootstock Guide** — Filter by size, rootstock cards, detail with spacing, soil compatibility
- **Blog** — Category pills, blog cards, article pages
- **Kisan Tools** — 26 widgets in 7 categories (2-col grid). See `KISAN_TOOLS.md`

---

## 5. My Orchard Screen

**Route:** `MyOrchard` (tab)  
**File:** `src/screens/MyOrchardScreen.tsx`

### Components:
- Orchard list cards (primary + secondary)
- Orchard detail with varieties
- Activity log
- Weather for each orchard
- **Prediction alerts** per orchard
- **Blocks** management (OrchardBlocksScreen)
- **Spray logs** (SprayLogScreen)

---

## 6. Weather Forecast Screen

**Route:** `Weather` (modal from any screen or nested)  
**File:** `src/screens/WeatherScreen.tsx`

### Components:
- Current weather widget
- 7-day forecast list
- Hourly forecast
- Spray suitability for each day
- **Spray safety indicator** (🟢 SAFE TO SPRAY)
- **48h Forecast** — hourly scrollable chart (temp, rain, humidity, wind)
- **Disease Risk Timeline** — 7-day risk chart
- Weather alerts

---

## 7. Auth Screens

**Route:** `Auth` (stack navigator)  
**Files:** `src/screens/Auth/*.tsx`

### Screens:
- Welcome (onboarding carousel) — 4 slides
- Login — phone/OTP + email/password
- Register — phone, OTP, name, location
- Forgot Password
- OTP verification

---

## 8. Onboarding / Welcome

**Route:** `Welcome`  
**File:** `src/screens/Onboarding/WelcomeScreen.tsx`

### 4 Slides:
1. Welcome to Baagicha — 🍎 Himalayan apple growing
2. Your Orchard — 🌳 Track stages, sprays, alerts
3. Expert Knowledge — 📖 Disease library, variety guides
4. Shop & Connect — 🛒 Buy inputs, join community

**Design:**
- Card centered vertically
- Icon 80px, title 22sp, description 13sp
- Skip button: arrow-right icon
- No grouped feature blocks (simplified after overflow complaint)

---

## 9. Notifications Screen

**Route:** `Notifications`  
**File:** `src/screens/NotificationsScreen.tsx`

### Components:
- Notification list (push + in-app)
- Unread badge
- Settings screen for notification preferences
- **Prediction alert notifications** — deep-link to AlertDetailScreen

---

## 10. Profile Screen

**Route:** `Profile`  
**File:** `src/screens/ProfileScreen.tsx`

### Components:
- User info card
- Points / badges
- Stats (reports, reviews, photos, spray logs)
- Saved items section
- Settings link
- **Orchard Blocks** quick access

---

## 11. Alert Detail Screen (NEW)

**Route:** `AlertDetail`  
**File:** `src/screens/Predictions/AlertDetailScreen.tsx`

### Full-screen detail for a single prediction:
- Disease name + Hindi name
- Risk badge (score 0-100)
- **Why this alert?** — factors list (temp, rain, humidity, altitude)
- **Predicted Infection** — start/end time, wetness hours, severity
- **Recommended Action** — chemical, dose, best spray window
- Safety tips
- Action buttons: `[✅ I sprayed]` `[📅 Remind me later]`
- **Feedback**: `[👍 Yes]` `[👎 No]` `[📝 Add note]`

---

## 12. Orchard Blocks Screen (NEW)

**Route:** `OrchardBlocks`  
**File:** `src/screens/Orchard/OrchardBlocksScreen.tsx`

### Components:
- `[+ Add New Block]` button
- Block cards: variety, area, plant count, aspect, irrigation
- Per-block risk badges: `🔴 Scab: HIGH | 🟡 Moth: MED`
- Actions: View / Edit / Delete

---

## 13. Block Detail Screen (NEW)

**Route:** `BlockDetail`  
**File:** `src/screens/Orchard/BlockDetailScreen.tsx`

### Same layout as AlertDetailScreen but scoped to one block's predictions.

---

## 14. Spray Log Screen (NEW)

**Route:** `SprayLog`  
**File:** `src/screens/Orchard/SprayLogScreen.tsx`

### Farmer spray history with reward points:
- `[+ Log New Spray]` button
- Log entries: date, chemical, dose, area, weather, points
- Reward points display

---

## 15. Prediction Feedback Modal (NEW)

**Route:** `PredictionFeedback` (modal)  
**File:** `src/screens/Predictions/PredictionFeedbackModal.tsx`

### Shown ~10 days after a HIGH/CRITICAL alert:
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

---

## 16. Kisan Tools Screens (NEW)

**Route:** `Tools`  
**File:** `src/screens/ToolsScreen.tsx`

### Hub screen — 26 widgets in 7 categories:
- 2-column grid layout (`width: 47.5%`)
- Each widget: icon circle + title + Hindi title
- On tap: navigate to individual calculator screen

**Categories:**
1. Orchard Establishment (4)
2. Crop Load & Thinning (4)
3. Spray & Inputs (4)
4. Harvest & Post-Harvest (5)
5. Financial & Market (3)
6. Weather & Phenology (4)
7. Training & Pruning (2)

> Full catalog: `KISAN_TOOLS.md`

---

## 17. Saved Items Screen

**Route:** `Saved`  
**File:** `src/screens/SavedItemsScreen.tsx`

### Components:
- Filter by type (Varieties / Rootstocks / Blogs / Chemicals)
- Saved item cards
- Remove from saved action

---

## Navigation Structure (Full)

```
AuthStack
├── Welcome
├── Login
├── Register
└── OTP

MainTabs (5 tabs)
├── Home (Tab)
│   ├── MyFarmSegment (dashboard)
│   └── CommunitySegment (social)
├── Spray (Tab)
│   └── SprayDetail
├── Shop (Tab)
│   ├── ProductDetail
│   ├── Cart
│   └── Checkout
├── Discover (Tab)
│   ├── Disease Library
│   │   └── Disease Detail
│   ├── Variety Guide
│   │   └── Variety Detail
│   ├── Rootstock Guide
│   │   └── Rootstock Detail
│   ├── Blog
│   │   └── Article Detail
│   └── Kisan Tools
│       └── Tool Calculator (×26)
└── MyOrchard (Tab)
    ├── Orchard List
    ├── Orchard Detail
    ├── Orchard Blocks
    │   ├── Block List
    │   └── Block Detail (predictions per block)
    ├── Spray Logs
    └── Alert Detail (prediction)

Global Modals
├── Weather
├── Notifications
├── Profile
│   ├── Saved Items
│   ├── Settings
│   └── Edit Profile
├── Prediction Feedback
└── Disease Reporter
    └── Submit Report
```

---

*This breakdown covers every screen in the React Native app. Each screen is implemented as a React Native screen component with matching design and data structures.*
