# Community Event Report — Implementation Plan

> **Saved on:** 2026-06-07  
> **Status:** Pending Approval / Design Freeze  
> **Context:** Add a "Report" quick-action chip in the Community Post Status section so farmers can quickly report farming-related events (weather, disease, fire, etc.) with auto-attached GPS and weather. Nearby farmers get push notifications for critical/high-urgency events.

---

## 📋 Proposed Report Event List

| # | Event (EN) | Event (HI) | Category | Default Urgency |
|---|-----------|-----------|----------|-----------------|
| 1 | **Hail Storm** | ओलावृष्टि | Weather | 🔴 Critical |
| 2 | **Heavy Rain** | भारी वर्षा | Weather | 🟠 High |
| 3 | **Thunderstorm / Lightning** | आंधी-तूफान / बिजली | Weather | 🟠 High |
| 4 | **Frost / Cold Wave** | पाला / शीत लहर | Weather | 🟠 High |
| 5 | **Drought / No Rain** | सूखा / वर्षा का अभाव | Weather | 🟠 High |
| 6 | **Snowfall** | हिमपात | Weather | 🟡 Medium |
| 7 | **Heat Wave** | लू / अत्यधिक गर्मी | Weather | 🟡 Medium |
| 8 | **Strong Winds** | तीखी हवाएं | Weather | 🟡 Medium |
| 9 | **Dense Fog** | घना कोहरा | Weather | 🔵 Low |
| 10 | **Disease Outbreak** *(select from DB)* | रोग का प्रकोप | Disease | 🟠 High |
| 11 | **Pest Infestation** *(select from DB)* | कीट का प्रकोप | Disease | 🟠 High |
| 12 | **Forest Fire** | जंगल की आग | Fire | 🔴 Critical |
| 13 | **Orchard / Crop Fire** | बाग/फसल में आग | Fire | 🔴 Critical |
| 14 | **Landslide / Road Block** | भूस्खलन / सड़क जाम | Infrastructure | 🟠 High |
| 15 | **Water Shortage / Canal Dry** | पानी की कमी / नहर सूखना | Infrastructure | 🟠 High |
| 16 | **Power Outage** | बिजली गुल | Infrastructure | 🟡 Medium |
| 17 | **Irrigation Failure** | सिंचाई व्यवस्था खराब | Infrastructure | 🟡 Medium |
| 18 | **Mandi / Market Closure** | मंडी बंद | Market | 🟡 Medium |
| 19 | **Sudden Price Crash** | भाव गिरावट | Market | 🟡 Medium |
| 20 | **Transport Strike** | परिवहन हड़ताल | Market | 🟡 Medium |
| 21 | **Wildlife / Monkey Damage** | जानवर / बंदर का नुकसान | Other | 🟡 Medium |
| 22 | **Chemical / Fertilizer Scarcity** | दवाई / उर्वरक की कमी | Other | 🟡 Medium |
| 23 | **Labor Shortage** | मजदूर की कमी | Other | 🔵 Low |
| 24 | **Govt Scheme Announcement** | सरकारी योजना | Other | 🔵 Low |
| 25 | **Frost Protection Failure** | एंटी-फ्रॉस्ट सिस्टम फेल | Other | 🟠 High |

> **Admin Panel:** Each event type will be managed from the admin panel (`/admin/report-types`). Admins can toggle active status, change urgency, and reorder the list.

---

## 🏗️ Implementation Plan

### Phase 1 — Backend (Laravel)

| Step | Task | Details |
|------|------|---------|
| 1.1 | **Migration: `report_types`** | `id`, `name_en`, `name_hi`, `category` (weather/disease/fire/infra/market/other), `urgency_level` (critical/high/medium/low), `icon`, `is_active`, `sort_order`, `timestamps` |
| 1.2 | **Model: `ReportType.php`** | Active scope, ordered by `sort_order` |
| 1.3 | **Admin CRUD** | `Admin/ReportTypeController` + Blade views under `/admin/report-types`. Full CRUD + AJAX toggle for `is_active` |
| 1.4 | **Extend `posts` table** | Add nullable columns: `report_type_id`, `latitude`, `longitude`, `weather_snapshot` (JSON), `report_meta` (JSON for `disease_id`, `disease_name`, etc.) |
| 1.5 | **Extend `POST /api/v1/posts`** | Accept `type: report`, `report_type_id`, `latitude`, `longitude`, `disease_id` (optional). Backend auto-fetches weather and stores in `weather_snapshot` |
| 1.6 | **New API: `GET /api/v1/report-types`** | Returns all active report types + diseases list (`id`, `name_en`, `name_hi`) from existing `diseases` table |
| 1.7 | **Nearby Notification Engine** | On Critical/High report creation: use Haversine formula to find users within configured radius (~15 km) where `notify_new_reports = true`. Dispatch FCM push + DB notification |
| 1.8 | **Update `PostResource`** | Include `report_type`, `distance_km`, `weather_snapshot`, `location_text` when `type = report` |

### Phase 2 — Frontend (React Native)

| Step | Task | Details |
|------|------|---------|
| 2.1 | **New chip: "Report"** | Add to `POST_TEMPLATES` in `CommunitySegment.tsx` alongside existing Spraying, Weather, Market, Orchard Work chips |
| 2.2 | **New component: `ReportComposerSheet`** | Bottom sheet / modal triggered by the Report chip |
| 2.3 | **Report Composer Flow** | ① Select event type ② If Disease/Pest → show searchable disease picker ③ Auto-capture & display GPS (with refresh) ④ Auto-fetch & display current weather ⑤ Optional photo + notes ⑥ Submit |
| 2.4 | **Update `postApi.ts`** | Extend `createPost` or add `createReportPost()` to send report fields |
| 2.5 | **Update `FeedPost` card** | Special rendering for `type === 'report'`: urgency-colored badge/border, event icon, location text, weather snapshot, disease name (tappable → disease detail) |
| 2.6 | **Push notification deep link** | Tapping a report notification opens `PostDetailScreen` for that report |

---

## ❓ Open Questions (To Be Answered Before Coding)

1. **Notification radius:** How far should push notifications go? *(Recommended: 15 km for Himalayan terrain)*
2. **Weather source:** Should the backend fetch weather server-side using posted coordinates, or should the app send it? *(Recommended: backend fetch for consistency)*
3. **Disease filter:** For Disease/Pest selection, show **all diseases** or only `hp_common = true` (common in Himachal Pradesh)?
4. **Edit / Delete:** Should reports be editable/deletable by the reporter after posting, like normal posts?
5. **Event list:** Any additions, removals, or re-categorizations from the 25-event list above?

---

## 🔗 Relevant Files (Existing Codebase)

### React Native
- `baagichaApp/src/screens/Home/CommunitySegment.tsx` — Post composer + feed
- `baagichaApp/src/services/postApi.ts` — Post creation API
- `baagichaApp/src/screens/PostDetailScreen.tsx` — Post detail view

### Laravel
- `app/Models/Post.php` — Post model
- `app/Models/Disease.php` — Disease master (for picker)
- `app/Services/NotificationDispatcher.php` — Push notification dispatcher
- `app/Models/DeviceToken.php` — FCM tokens
- `app/Http/Controllers/Api/PostController.php` — Post creation endpoint
- `routes/web/admin/diseases.php` — Example admin CRUD pattern to follow

---

*End of plan. Resume from here when ready to implement.*
