# Architecture

## The three repos

```
BaagichaWorkspace/            ← git repo #1 (thin: docs, skills, playwright artifacts)
├── web_baagicha/             ← git repo #2, gitignored by the root  (Laravel — the backend)
├── baagichaApp/              ← git repo #3, gitignored by the root  (React Native client)
└── BaagvaaniBrain/           ← tracked as a gitlink, but there is NO .gitmodules
```

The root `.gitignore` excludes `baagichaApp/` and `web_baagicha/`, so the workspace repo carries
only cross-cutting docs. `BaagvaaniBrain` is recorded with mode `160000` (a submodule gitlink)
but no `.gitmodules` file exists — a fresh `git clone` of the workspace produces an empty
`BaagvaaniBrain/` directory that `git submodule update --init` cannot populate. See
[known-issues.md](known-issues.md) #4.

## Ground rule

All API logic lives in Laravel. `web_baagicha` is the single backend for three consumers:

1. **Public website** — Blade + hand-written CSS, `layouts.site`
2. **Admin panel** — Blade + Bootstrap 5, `layouts.admin.app`, `/admin/*`, role `admin|manager`
3. **Mobile API** — JSON under `/api/v1/*`, Sanctum bearer tokens

React Native holds no business logic, no schema, no route definitions.

## Laravel: modular monolith

`nwidart/laravel-modules`. `app/` is nearly empty (`Controller`, `AppServiceProvider`,
`RedirectIfNotAdmin`, `helpers.php`, `BlogInternalLinker`). **All feature code is in
`Modules/<Name>/`** — search there, not `app/`.

18 enabled modules. `modules_statuses.json` still lists `Variety` and `Strain` as disabled;
those directories are gone, folded into `VarietyStrain`.

Measured scale (2026-09-06):

| | Count |
|---|---|
| Modules | 18 enabled |
| Registered routes | 638 (337 admin, 180 api, rest public) |
| Controllers | 164 — Admin 52, Api 48, Web 37, App 12 |
| Services | 62 |
| Blade views | 425 in `Modules/`, 10 in `resources/views/` |
| Migrations | 179 files → 138 tables |
| Form Requests | 38 · Policies | 11 |
| Queued jobs | 15 · Console commands | 18 |

Largest modules by file count: Core (172 php / 115 blade), Shop (148 / 40),
KnowledgeBase (143 / 66), Auth (113 / 28), Disease (104 / 29).

### Module anatomy

```
Modules/Fruit/
├── app/{Models,Policies,Providers,Services,Observers,Jobs,Enums,DTOs,Repositories,
│        Http/{Controllers/{Admin,Api,Web},Requests}}
├── database/{migrations,seeders,factories}
├── resources/{views,assets}
├── routes/{web.php,api.php,admin.php}
├── config/config.php
├── module.json          # registers the ServiceProvider
└── composer.json        # merged into root via wikimedia/composer-merge-plugin
```

### Routing

Each module's `RouteServiceProvider::map()` wires its own route files. **There is no central
route registry** — root `routes/web.php` and `routes/api.php` are empty stubs.

| File | Middleware | Prefix | Name prefix |
|---|---|---|---|
| `routes/web.php` | `web` | — | — |
| `routes/api.php` | `api` | `/api` | `api.` |
| `routes/admin.php` | `web,auth,role:admin\|manager` | `/admin` | `admin.` |

Middleware aliases (`role`, `permission`, `role_or_permission`, `admin`, `detect.mobile`,
`cache.response`) are registered in `bootstrap/app.php`; `SecurityHeaders` is appended globally
(nosniff, DENY framing, referrer policy, permissions policy — **no CSP**).

### Views

Module views are namespaced: `view('fruit::app.fruit.index')`, `<x-core::page-hero />`.
**Exception:** `CoreServiceProvider::boot()` adds Core's view path to the finder, so Core's
shared views resolve unprefixed — that is why `@extends('layouts.site')` and `<x-text-input />`
work everywhere.

Layouts, all in `Modules/Core/resources/views/layouts/` — **do not create new ones**:

| Layout | Use |
|---|---|
| `layouts.site` | current public layout — use this for new public pages |
| `layouts.app.base` | older public/PWA layout, still used by many pages |
| `layouts.admin.app` | admin panel |
| `layouts.guest` | auth screens |

### Assets — two competing systems

1. **Vite** builds `resources/css/app.css` (Tailwind 4), `resources/sass/app.scss` (admin),
   `resources/js/app.js`. `npm run build` then runs `scripts/copy-assets.js` to copy hashed
   output to `public/css/app.css`, `public/css/admin.css`, `public/js/app.js`. **Skipping
   copy-assets leaves stale CSS in the production paths.**
2. **Static per-page files** — 28 `public/css/*.css` and 24 `public/js/*.js`, pulled in from
   Blade with `@push('styles')` / `@push('scripts')` + `asset()`. `style.css` (124 KB) and
   `script.js` are shared; page rules go in a page-named file, never in `style.css` and never
   in an inline `<style>`/`<script>` block.

In practice **system 2 does the real work** — Tailwind's `@source` globs never reach
`Modules/**`, so utility classes written in module Blades are purged. See
[known-issues.md](known-issues.md) #3. Module-level `vite.config.js` files are unused scaffolding.

### Scheduled work

`routes/console.php`: weather refresh every 15 min; sitemap daily 03:00; weather alerts 06:00;
spray reminders 08:00; activity-log prune 03:30; weather recommendations twice daily 06:00/18:00;
forecast archive cleanup 02:00. Intelligence schedules are registered by
`IntelligenceServiceProvider`, not here.

There is no long-running queue daemon in production — cron runs `queue:work` per minute, and it
**must** listen on `default,notifications` or notification jobs never drain
(`cronjobs/crons-bacup.md`).

## The domain engines

Three substantial pieces of real domain logic, all backend:

- **`Modules/Disease/app/Services/Prediction/`** — epidemiological models: Revised Mills (scab),
  simplified Maryblyt (fire blight), DMC (powdery mildew), degree-day pest models, plus
  `LeafWetnessEstimator`, `MicroclimateService`, `SprayWindowService`, `RecommendationGenerator`.
  Documented in `.opencode/skills/prediction-engine/`.
- **`Modules/Intelligence/`** — the "Daily Orchard Intelligence Card": feature engine → scoring →
  recommender → explanation builder → persistence → archive, driven by three queued jobs.
- **`Modules/Weather/`** — OpenWeatherMap **and** IMD (India Meteorological Department, with JWT
  auth, warnings, rainfall), plus `VPDCalculator`, `DeltaTCalculator`, `FertigationRecommender`.

## Mobile app

React Native 0.85.3 / React 19.2.3 / TypeScript, CLI-bootstrapped (not Expo). 123 `.tsx`,
65 `.ts` files, ~44 screens.

- **State:** Zustand (7 stores — auth, cart, intelligence, notification, onboarding, orchard, toast)
- **Storage:** MMKV
- **Navigation:** React Navigation, bottom tabs → **Home, Spray, Shop, Discover, MyOrchard**,
  each a native stack
- **Data:** 20 hand-written `src/services/*Api.ts` + 19 `src/hooks/use*.ts`. No react-query.
- **Auth:** Sanctum bearer token in MMKV; Google + Facebook social login; phone OTP
- **Other:** Firebase messaging (push), Razorpay, fast-image, video, geolocation

`src/config/env.ts` reads `react-native-config`, defaulting to a hardcoded LAN IP
`http://192.168.1.100:8000/api/v1`. There is no production API URL anywhere in the repo.

## API contract

138 of 144 API routes are under `/api/v1`. Six stragglers are unversioned:
`api/brands`, `api/brands/{slug}`, `api/weather/{current,coordinates,alerts,refresh}`.

The mobile app's `.opencode/skills/api-reference/SKILL.md` is the closest thing to a written
contract. There is no OpenAPI spec, no generated types, and no contract test — the app's
TypeScript response types are maintained by hand against the Laravel resources.
