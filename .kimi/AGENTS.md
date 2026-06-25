# Baagicha Workspace — Agent Context

## Architecture Ground Rules

1. **All APIs live in Laravel.** The `web_baagicha/` project is the sole backend. Every endpoint consumed by the mobile app must be built, versioned, and maintained inside the Laravel codebase.
2. **React Native is the frontend.** The `baagichaApp/` project is a pure React Native (CLI) client. It does not contain any backend logic, database migrations, or API route definitions — only UI, state management, and API consumption.
3. **Laravel serves both Web PWA and Mobile API.** The same Laravel application powers the Blade-based web views and exposes JSON endpoints for the React Native app under a dedicated mobile API namespace (e.g., `/api/v1/...`).

## Web Frontend Standards

1. **Hero sections must use a background image.** Any page with a full-width hero section should place a relevant image behind the content with a dark gradient overlay for readability. Use the standard pattern:
   - Wrapper: `relative bg-bg-primary text-white overflow-hidden`
   - Background layer: `absolute inset-0` with a `<picture>` containing WebP + fallback PNG/JPG
   - Overlay: `absolute inset-0 bg-gradient-to-r from-primary-900/90 via-primary-800/80 to-primary-700/60`
   - Content: `relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
2. **Reuse existing hero assets.** Default hero image is `public/images/hero-orchard-farmer.webp` / `.png`. Add page-specific images only when the subject genuinely differs.
3. **Maintain contrast.** Hero text stays white (`text-white`); subtitles use `text-white/75`; interactive elements use `bg-white/10 border-white/20`.

## Project Structure

This workspace contains two projects:

| Directory | Stack | Role |
|-----------|-------|------|
| `web_baagicha/` | Laravel + Blade | Backend API + Web PWA |
| `baagichaApp/` | React Native (CLI) | Mobile frontend (iOS & Android) |

## `.kimi/` Memory Organization

```
.kimi/
├── AGENTS.md          ← This file
├── ECOMMERCE_PLAN.md  ← Shop, cart, checkout, payments roadmap
├── Laravel/
│   └── API_ARCHITECTURE.md  ← API org, auth, response format
│   └── PREDICTION_ENGINE.md ← Disease/pest prediction backend
└── React/
    ├── DESIGN_SPEC.md       ← Colors, typography, shadows, spacing
    ├── DATA_MODELS.md       ← TypeScript interfaces for all entities
    ├── SCREEN_BREAKDOWN.md  ← Complete screen list + navigation
    ├── API_REFERENCE.md     ← API endpoints, auth, toast types
    ├── PREDICTION_TYPES.md  ← Prediction engine frontend types + screens
    └── KISAN_TOOLS.md       ← 26 utility widget calculators
```

### React/ Folder (Mobile App)
Memory files extracted from the Laravel web frontend + new research:

| File | Purpose |
|------|---------|
| `DESIGN_SPEC.md` | Colors, typography, shadows, spacing, animations |
| `DATA_MODELS.md` | TypeScript interfaces for all entities |
| `SCREEN_BREAKDOWN.md` | Complete screen list with components & navigation |
| `API_REFERENCE.md` | API endpoints, auth, toast types |
| `PREDICTION_TYPES.md` | Disease/pest prediction types, stores, screen specs |
| `KISAN_TOOLS.md` | 26 farming calculator widgets catalog |

### Laravel/ Folder (Backend/Web)
| File | Purpose |
|------|---------|
| `API_ARCHITECTURE.md` | API organization, auth guards, response format |
| `PREDICTION_ENGINE.md` | Disease/pest prediction engine — models, services, APIs |

## Active Modules

| Module | Status | Docs |
|--------|--------|------|
| Auth (Sanctum + MMKV) | ✅ Implemented | `API_REFERENCE.md` |
| Onboarding (Welcome → Auth → Permissions) | ✅ Implemented | `SCREEN_BREAKDOWN.md` |
| Home (Segmented: My Farm / Community) | ✅ Implemented | `SCREEN_BREAKDOWN.md` |
| Kisan Tools (26 widgets) | ✅ UI Implemented | `KISAN_TOOLS.md` |
| Fruit Module | ✅ Implemented | `Modules/Fruit/` |
| Prediction Engine | ✅ Backend complete, RN pending | `PREDICTION_ENGINE.md`, `PREDICTION_TYPES.md` |
| Daily Orchard Intelligence Card | ✅ Implemented (v1) | `Modules/Intelligence/` |
| eCommerce (Shop) | 🔄 Phase 1 | `ECOMMERCE_PLAN.md` |

## Quick Reference

- **Web app source:** `web_baagicha/resources/views/app/`
- **Mobile app source:** `baagichaApp/src/`
- **Target regions:** HP, UK, J&K (Himalayan apple belt)
- **Research folder:** `BaagichaWorkspace/research/` (competitors, market, revenue, prediction engine, utility widgets)

## Queue & Cron Health Monitoring

A lightweight heartbeat monitor is available for the queue worker cron job:

- **Artisan command:** `php artisan baagicha:queue-cron-heartbeat`
- **Heartbeat log:** `web_baagicha/storage/logs/cron-heartbeat.json` (rolling 24-hour window)
- **Admin UI:** `/admin/dashboard/queue-health` (linked from the admin sidebar as "Queue & Cron Health")
- **Timezone:** set `APP_TIMEZONE=Asia/Kolkata` in `.env` so timestamps match local time

The admin UI also exposes queue-management actions for admins:

- View full exception + payload for each failed job in a detail modal
- Retry a single failed job by UUID, or retry all failed jobs at once
- Delete (forget) a single failed job, or flush all failed jobs
- Clear all pending jobs from the queue when repeated failures are piling up

Some listeners (e.g. `Modules\Auth\Listeners\NotifyAdminOfNewRegistration`) explicitly dispatch to a `notifications` queue. The main worker **must** listen on both `default` and `notifications` queues or those jobs will sit pending forever.

Recommended Hostinger cron command (note the `cd` into the project directory). The intelligence module adds a dedicated `intelligence` queue, so include it in the worker:

```
* * * * * cd /home/u896019069/domains/baagvaani.com/web_baagicha && /usr/bin/php artisan queue:work --queue=default,notifications,intelligence --once --timeout=60 --tries=3 >> storage/logs/queue-cron.log 2>&1; /usr/bin/php artisan baagicha:queue-cron-heartbeat
```

Optional safety-net command to drain the `notifications` queue on a slower schedule:

- **Artisan command:** `php artisan baagicha:process-notification-queue`
- **Purpose:** Process all pending jobs on the `notifications` queue until empty
- **Suggested cron:** once per hour, e.g. `0 * * * *`

```
0 * * * * cd /home/u896019069/domains/baagvaani.com/web_baagicha && /usr/bin/php artisan baagicha:process-notification-queue >> storage/logs/queue-notifications.log 2>&1
```

## Daily Orchard Intelligence Card

The `Modules/Intelligence` module generates a personalized daily card for every authenticated user. It appears below the navbar in the web PWA and below the global header in the React Native app.

- **Generation:** `intelligence:generate-daily` runs at 02:00 IST for all active users with orchards.
- **Feature recomputation:** `intelligence:recompute-features` runs at 01:30 IST.
- **Archival:** `intelligence:archive-yearly` runs at 03:00 IST on 1 January.
- **Queue:** jobs are dispatched to the `intelligence` queue.
- **On-demand:** `GET /api/v1/intelligence/today` generates a card if missing.
- **Tables:** `user_daily_intelligence`, `user_daily_intelligence_items`, `user_intelligence_features`, `user_intelligence_archive`.
- **Shadow mode:** enable with `INTELLIGENCE_SHADOW_MODE=true` in `.env`.

## Sitemap Generation

The SEO sitemap is a static XML file written to `public/sitemap.xml` and served directly by the web server.

- **Artisan command:** `php artisan sitemap:generate`
- **Output path:** configured by `SITEMAP_PATH` env var (defaults to `public/sitemap.xml`)
- **Schedule:** already registered in `routes/console.php` to run daily at 03:00
- **Requirements:** the Laravel scheduler itself needs a system cron entry to trigger `schedule:run`

On Hostinger/shared hosts where the web root is `public_html` and the Laravel app lives in a separate folder (e.g. `web_baagicha/`), point `SITEMAP_PATH` to the public web root so the file is served at `https://baagicha.com/sitemap.xml`:

```env
APP_URL=https://baagicha.com
SITEMAP_PATH=/home/u896019069/domains/baagvaani.com/public_html/sitemap.xml
```

Recommended Hostinger cron command (runs the scheduler every minute so the 03:00 sitemap job fires):

```
* * * * * cd /home/u896019069/domains/baagvaani.com/web_baagicha && /usr/bin/php artisan schedule:run >> storage/logs/schedule.log 2>&1
```

After deploying, generate the first sitemap manually:

```
cd /home/u896019069/domains/baagvaani.com/web_baagicha && /usr/bin/php artisan sitemap:generate
```

Make sure `APP_URL=https://baagicha.com` is set in `.env` so generated URLs use the production domain.

## Variety Module — Multi-Fruit Preparation

The `varieties` table has a `fruit_type` enum column to support apples, pears, plums, peaches, apricots, cherries, persimmons, and pomegranates. Existing varieties default to `apple`. The public API defaults to `fruit=apple` for backward compatibility with the mobile app.

A dedicated `fruit_id` foreign key now also links a variety to the canonical `Fruit` module. The `Fruit` module owns many-to-many relationships to `Variety`, `Disease`, and `Rootstock` via explicit pivot tables (`fruit_variety`, `fruit_disease`, `fruit_rootstock`). Fruit pages are available at `/fruits/{slug}` and `/varieties/by-fruit/{slug}`.
