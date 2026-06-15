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
| Prediction Engine | 🔄 Backend complete, RN pending | `PREDICTION_ENGINE.md`, `PREDICTION_TYPES.md` |
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

Recommended Hostinger cron command (note the `cd` into the project directory):

```
* * * * * cd /home/u896019069/domains/baagvaani.com/web_baagicha && /usr/bin/php artisan queue:work --once --timeout=60 --tries=3 >> storage/logs/queue-cron.log 2>&1; /usr/bin/php artisan baagicha:queue-cron-heartbeat
```

## Variety Module — Multi-Fruit Preparation

The `varieties` table has a `fruit_type` enum column to support apples, pears, plums, peaches, apricots, cherries, persimmons, and pomegranates. Existing varieties default to `apple`. The public API defaults to `fruit=apple` for backward compatibility with the mobile app.
