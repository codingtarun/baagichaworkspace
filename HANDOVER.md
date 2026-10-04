# Handover — Claude Code → OpenCode

**Date:** 2026-10-04 · **From:** Claude Code (Claude Opus) · **To:** OpenCode agents · **Owner:** Tarun Chauhan

This is everything Claude Code knew about the Baagvaani workspace at handover. It is written to be
read once, start to finish, before the first OpenCode session. The always-on rules are in
[`AGENTS.md`](AGENTS.md). Measured detail lives in [`.opencode/context/`](.opencode/context/):

| File | Read when |
|---|---|
| `product.md` | you need the domain — who the users are, why altitude matters |
| `architecture.md` | working in `web_baagicha` — module layout, routing, assets, engines |
| `state-of-the-code.md` | judging what is real vs aspirational (sizes, tests, doc reliability) |
| `known-issues.md` | before touching anything — 12 confirmed defects with evidence |
| `modules.md` | Blog / VarietyStrain / Disease deep dive, the 24 broken `route()` calls |
| `environments.md` | local setup, DB, deployment, third-party services, credentials map |
| `open-questions.md` | decisions only Tarun can make — **ask, don't assume** |

`.claude/context/` holds the identical files for Claude Code. If you update one, update both.

---

## 1. The product in one page

**Baagvaani** (legacy/internal name **Baagicha**, बागीचा = "orchard"), `baagvaani.com`. A solo side
project — one developer, Tarun. **It is live with real users**, so production data is sacred.

- **Users:** apple-growing families in the Indian Himalaya — Himachal Pradesh, Uttarakhand, J&K.
  ~800k households. Hindi-first, Android-first, low digital literacy, patchy connectivity.
- **The wedge — altitude.** A grower at 8,700 ft and one at 1,800 ft need spray timings 14 days
  apart, different diseases, varieties and rootstocks. Competitors (Plantix, AgroStar…) give
  everyone the same advice.

  | Band | Metres | Feet | Belt | Spray offset |
  |---|---|---|---|---|
  | `below_6000` | < 1,829 | < 6,000 | Solan, Bilaspur, lower Sirmaur | −7 days |
  | `6000_8000` | 1,829–2,438 | 6,000–8,000 | Shimla belt, lower Kullu | 0 |
  | `above_8000` | > 2,438 | > 8,000 | Narkanda, Kinnaur, upper Kullu | +14 days |

  Band is derived from `altitude_meters` in the model's `booted()` hook. Never set it by hand.
- **Bilingual:** every content table has `_en`/`_hi` column pairs. The legacy web *interface* is
  English-only (no `lang/`); the rebuild intends to fix that (open question R3).
- **Business model (planned):** free → input-marketplace commission + premium → B2B/data. The
  legacy Shop/Vendor modules are built well ahead of demand.
- **Content moat:** 9 fruits, 211 variety strains, 123 rootstocks, 46 diseases, 50 chemicals in the
  legacy DB.
- **Naming:** "Baagicha" in code (DB `baagicha`, repos, RN bundle `com.baagichaapp`) and "Baagvaani"
  in user-facing copy are the same thing.

---

## 2. Workspace and git state (as of 2026-10-04)

```
BaagichaWorkspace/          root repo, branch main — docs only
├── AGENTS.md  HANDOVER.md  CLAUDE.md  .claude/  .opencode/
├── baagvaani_web/          own repo, main, 1 commit (505bb8c), clean        ← ACTIVE
├── web_baagicha/           own repo, feature/fruit-module (= master locally) ← LIVE
├── baagichaApp/            own repo, main, clean
└── BaagvaaniBrain/         submodule → github.com/codingtarun/BaagvaaniBrain
```

**Pending, waiting on Tarun (outward-facing — do not do without an explicit go-ahead):**

1. **Push `web_baagicha`.** `master` was fast-forwarded to `feature/fruit-module` locally on
   2026-09-06 (98 commits: Fruit refactor, VarietyStrain, Intelligence, IMD weather, Disease
   rework). `origin/HEAD` still points at a June `master`.
2. **Deploy to production:** the duplicate-newsletter fix, the Chemical publish crash fix, and
   migration `2026_09_06_000001_add_acre_to_area_unit_enums` (additive, safe forward).
3. Delete branch `backup/modular-migration-20260611-221110`.
4. Rotate and untrack the Facebook client token in `baagichaApp/.env`.
5. Check the live Hostinger crontab's `queue:work --queue=` list (known-issues #12).

**Uncommitted work that belongs to Tarun — leave alone:** 4 modified seeders in `web_baagicha`
(`Modules/Auth/database/seeders/{UserProfileSeeder,UserSeeder}.php`,
`Modules/Intelligence/database/seeders/UserDailyIntelligenceSeeder.php`,
`database/seeders/DatabaseSeeder.php`).

**Doc fixes made at handover (uncommitted in their sub-repos — review and commit there):**
`web_baagicha/.opencode/**`, `web_baagicha/CLAUDE.md` (OrchardActivities line),
`baagichaApp/.opencode/**` + `opencode.json`, `baagvaani_web/AGENTS.md` + `opencode.json`,
`BaagvaaniBrain/.opencode/README.md` + `blog-brain.md`.

### Timeline

| Date | What happened |
|---|---|
| ≤ 2026-06 | `web_baagicha` built with Kimi/OpenCode agents; moved to `Modules/` (nwidart) in June |
| 2026-08-14 | Local DB seeded (all users/orders dated this day — not real traffic) |
| 2026-09-06 | Claude Code takeover: audit + stabilisation. 17 failing tests → 404 passing (3 root causes: Chemical publish crash, duplicate newsletters, missing `acre`). Branch fast-forwarded. Docs corrected. Submodule fixed. VarietyStrain policy added. OrchardActivities module removed. Laravel Boost installed |
| 2026-09-22 | Tarun decides the old app is too confusing → **rebuild** `baagvaani_web` on Laravel 13. Foundation + mobile OTP API built |
| 2026-10-04 | This handover to OpenCode |

---

## 3. `baagvaani_web/` — the rebuild (where new work goes)

Laravel **13.32** · PHP **8.5** (composer `^8.3`) · MySQL **`baagicha_db`** (separate from the live
`baagicha`) · Bootstrap **5.3.8** + jQuery **4** · Vite 8 + Sass · **no Tailwind**.

### 3.1 Scope decisions (from Tarun, 2026-09-22, out of a 24-item feature inventory)

- **Built:** foundation (auth, roles/permissions, admin shell, media library, locations), public
  marketing pages, SEO, security headers, and the mobile phone-OTP auth API.
- **Deferred:** knowledge base — fruits, varieties, rootstocks, diseases, chemicals, spray. Tarun
  will *revise* these features first because they are interlinked.
- **Skipped for now:** farmer tools, content/engagement, commerce.
- **Rule:** never port a module unprompted. When Tarun names one, plan it against the rebuild's
  conventions (below), not the old app's.
- **Nothing altitude-related exists yet** — no `altitude_band` column, no orchard model.

### 3.2 Dependencies

`require`: laravel/framework ^13.17, laravel/sanctum 4.3, laravel/tinker 3, nwidart/laravel-modules
13, spatie/laravel-activitylog 5.1, spatie/laravel-medialibrary 11.23, spatie/laravel-permission
8.3, spatie/laravel-sitemap 8.2. `require-dev`: laravel/boost 2.9, laravel/breeze 2.4, pail, pao,
pint 1.32, phpunit 12.5, mockery, collision, faker. `wikimedia/composer-merge-plugin` merges
`Modules/*/composer.json`.
npm: bootstrap 5.3.8, bootstrap-icons 1.13, jquery 4, @popperjs/core, @fontsource-variable/nunito,
@fontsource/noto-sans-devanagari; dev: vite 8, laravel-vite-plugin 3, sass, concurrently.

Composer scripts: `setup` (install → .env → key → migrate → npm install → build), `dev`
(`php artisan dev`), `test` (`config:clear` then `php artisan test`).

### 3.3 Layout

| Where | What |
|---|---|
| `app/` | Framework-level only: `User` model, Breeze controllers, `Enums/Permission`, `Enums/SystemRole`, middleware `EnsureUserIsActive` (alias `active`) and `SetApiLocale` |
| `Modules/Core` | Public pages, SEO, security headers, admin dashboard, activity log, system health, `AdminMenu`, `ModuleRouteServiceProvider`, `PhoneNumber` |
| `Modules/Users` | Admin user CRUD (soft delete + restore), roles & permissions, admin profile, `users:create-admin`, `AccountSafeguards` |
| `Modules/Media` | `MediaAsset` on spatie/medialibrary — one file each, bilingual alt text |
| `Modules/Location` | `states` / `districts` (`_en`/`_hi`), admin CRUD, public API |
| `Modules/MobileAuth` | Phone OTP → Sanctum token API for the RN app |
| `resources/views/layouts` | `site`, `guest`, `admin` — the **only** layouts |
| `resources/views/components/{form,admin}` | Shared Blade components |

All five modules are enabled in `modules_statuses.json`. Each has a `*ServiceProvider`, a
`RouteServiceProvider` (extends Core's `ModuleRouteServiceProvider`) and an `EventServiceProvider`.

### 3.4 Conventions (verbatim from `baagvaani_web/CLAUDE.md`, all binding)

- **Routes:** a module's `routes/web.php`, `routes/admin.php` (→ `/admin`, `admin.*`, `admin`
  middleware group = `web, auth, active, permission:admin.access`) and `routes/api.php` (→ `/api/v1`,
  `api.v1.*`) are mounted by extending `Modules\Core\Providers\ModuleRouteServiceProvider`. Root
  `routes/web.php` holds Breeze routes only.
- **Permissions:** add a case to `App\Enums\Permission`, grant it in
  `SystemRole::defaultPermissions()`, re-run
  `php artisan db:seed --class="Modules\Users\Database\Seeders\RolesAndPermissionsSeeder"`
  (idempotent). `super-admin` passes every gate via `Gate::before`, so invariants ("not yourself",
  "not the last super admin") go in `AccountSafeguards`, never in policies.
- **Admin menu / sitemap:** modules register entries from their provider's `boot()` via
  `AdminMenu::add($section, $label, $route, $icon, $active, $permission, $order)` and
  `SitemapRegistry::register()`. Nothing is hard-coded in the sidebar. Sections, in order:
  `Main, Content, People, Media, Settings, System` (Content is empty, waiting for future modules).
- **SEO:** controllers set `SeoManager` (`title`, `description`, `canonical`, `breadcrumbs`,
  `schema`). Pages are `noindex` until `SEO_INDEXABLE=true` (production only).
- **CSP:** nonce-based. Inline scripts must be `<script type="module" @cspNonce>` and use
  `window.$` / `window.bootstrap`. No `onclick=` — bind in `resources/js/admin.js` via `data-*` hooks.
- **Frontend:** one Vite build. `resources/scss/_tokens.scss` holds the brand; `site.scss` /
  `admin.scss` import Bootstrap. Fonts and icons are self-hosted via `resources/css/vendor.css`.
  No Tailwind, no per-module Vite.
- **Phones** are stored E.164 (`+919876543210`); normalise with `PhoneNumber::normalize()`
  (`PATTERN /^\+91[6-9]\d{9}$/`, plus `format()` → "+91 98765 43210" and `mask()`).
- **Bilingual columns** come in `_en`/`_hi` pairs. **Strict mode forbids lazy loading** — eager-load.
  `preventSilentlyDiscardingAttributes` is also on outside production.
- From the Boost guidelines: use `php artisan make:* --no-interaction`; tests are **PHPUnit, not
  Pest** (`make:test --phpunit`); curly braces always, constructor promotion, explicit return
  types, TitleCase enum keys; no new base folders; no dependency changes without approval.

### 3.5 Auth and authorisation

- **Web:** Breeze **email + password** (session guard `web`, the only guard). `LoginRequest` adds
  `is_active => true` and throttles at 5. Registration assigns `farmer`. `/dashboard` redirects to
  the admin dashboard if `canAccessAdmin()`, else to `profile.edit`.
- **Mobile:** phone OTP → Sanctum bearer token with ability `app` (see 3.7).
- **Roles** (`App\Enums\SystemRole`): `super-admin` (all, via `Gate::before`), `admin` (every
  permission), `manager` (admin.access, users.view, media.view, media.upload, locations.manage),
  `farmer` (none).
- **Permissions** (`App\Enums\Permission`): `admin.access`, `users.{view,create,update,delete}`,
  `roles.manage`, `media.{view,upload,delete}`, `locations.manage`, `activity.view`, `system.view`.
- `AccountSafeguards`: can't delete yourself or the last active super admin; can't deactivate
  yourself or change your own roles; only a super admin can grant super-admin.
- `AppServiceProvider`: `api` rate limiter 120/min; password rules min 10 + letters/numbers/
  uncompromised in production (min 8 otherwise); `DB::prohibitDestructiveCommands()` in
  production; `Paginator::useBootstrapFive()`.
- Dev login: `admin@baagvaani.test` / `password` (seeded by `DevelopmentAdminSeeder`, local only).
  `php artisan users:create-admin --email= --name= --role=super-admin` creates or promotes an admin.

### 3.6 Routes (72 total)

- **Public (Core):** `/`, `/about`, `/privacy-policy`, `/terms`, `/robots.txt`, `/sitemap.xml`,
  `/llms.txt`, `/site.webmanifest`, health `/up`.
- **Admin:** `/admin` (dashboard), `/admin/activity`, `/admin/system`, `/admin/profile`,
  `/admin/users` (+ `PATCH {user}/restore`), `/admin/roles`, `/admin/media`, `/admin/states`,
  `/admin/districts`.
- **API (`/api/v1`):** `GET locations/states`, `GET locations/states/{state:slug}/districts`
  (public); `auth/*` (3.7). `SetApiLocale` reads `Accept-Language` en|hi and sets `Content-Language`.
  Exceptions render as JSON for `api/*`. Resources are plain `JsonResource` — **no**
  `{success,data,message}` envelope (that envelope is the legacy app's).

### 3.7 MobileAuth API — the contract the RN app will move to

| Method & path | Middleware | Result |
|---|---|---|
| `POST /api/v1/auth/otp/request` `{phone}` | throttle `otp-request` | 202 `{message, expires_in, resend_in}` |
| `POST /api/v1/auth/otp/verify` `{phone, code, device_name, locale}` | throttle `otp-verify` | 201 new / 200 existing `{token, token_type:"Bearer", expires_at, is_new_user, user}` |
| `GET` / `PATCH /api/v1/auth/me` (name, email, locale) | `auth:sanctum, active, abilities:app, throttle:api` | `AccountResource` |
| `GET /api/v1/auth/sessions`, `DELETE /sessions/{session}` | same | token list / revoke |
| `POST /api/v1/auth/logout`, `/logout-all` | same | |

`AccountResource`: id, name, phone, email, locale, avatar_url, is_profile_complete,
phone_verified_at, created_at. Errors: `OtpException` → JSON `{message, error, …}` with
`otp_cooldown` / `otp_send_limit` (429), `otp_expired` / `otp_invalid` / `otp_locked` (422 with
`attempts_left`), account disabled, delivery failed.
Config `mobileauth.*`: 6-digit code, TTL 300 s, 5 attempts, 60 s cooldown, 5 sends/phone/hour,
30 requests/IP/hour, 20 verifies/IP/min; tokens 60 days, max 5 per user (oldest revoked).
SMS via `Contracts/SmsSender` → `LogSmsSender` or `Msg91SmsSender` (`SMS_DRIVER`; sender `BAAGVN`).
**Note:** this differs from the legacy API the app uses today (`otp/send`, different payloads).

### 3.8 Data model so far

- `users`: name?, email? unique, phone(20)? unique, phone_verified_at, password?, locale(5)
  default `en`, is_active, last_login_at, soft deletes. `User` uses HasApiTokens, HasRoles,
  InteractsWithMedia (avatar, 160 px webp thumb), LogsActivity, SoftDeletes.
- `media_assets` (title, alt_en, alt_hi, uploaded_by) + spatie `media`; collection `file`
  (jpeg/png/webp/gif/pdf), conversions `thumb` 400² crop webp q80 and `web` max 1600 webp q82,
  non-queued.
- `states` (code unique, slug, name_en, name_hi, is_active, sort_order) and `districts`
  (state_id FK restrict, unique(state_id, slug)). Trait `HasBilingualName`. `LocationSeeder` seeds
  HP, UT, JK with Hindi district names.
- `otp_challenges` (phone, code_hash, attempts, expires_at, consumed_at, ip, user_agent) — prunable.
- spatie permission tables, activity log, Sanctum tokens, jobs/cache/sessions (all `database` drivers).

### 3.9 Scheduler and queue

Scheduler heartbeat (every minute), `RecordQueueHeartbeat` (every 5 min), `activitylog:clean`
03:30, `model:prune` OtpChallenge 02:15, `sanctum:prune-expired --hours=24` 02:30. A cron
running `schedule:run` every minute **and** a queue worker are required; `/admin/system` shows
their health (stale after 3 / 15 min).

### 3.10 Security headers (`Modules/Core/.../SecurityHeaders`, global)

nosniff, `X-Frame-Options: SAMEORIGIN`, Referrer-Policy, Permissions-Policy (`geolocation=(self)`),
COOP, HSTS, `X-Robots-Tag: noindex` when not indexable, and CSP:
`default-src 'self'; script-src 'self' 'nonce-…'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; font-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'self'`.
Any new external script/connect target needs a CSP change.

### 3.11 Tests

`composer test` → **93 passed, 0 failed, 313 assertions, ~3.6 s** (2026-10-04). Suites: Unit,
Feature, Modules (`Modules/*/tests/{Feature,Unit}`), sqlite `:memory:`, `SMS_DRIVER=log`, array
cache/session/mail, sync queue. Files: Breeze auth (7 files), Core (AdminCorePages, SecurityHeaders,
Seo, PhoneNumber), Users (UserAdmin 14, RoleAdmin 6), Media (4), Location (5), MobileAuth
(OtpLogin 19). **Every new feature ships with feature tests in its module.**

### 3.12 Recipe — adding a module when Tarun names a feature

1. Read the legacy module in `web_baagicha/Modules/<Name>` for *behaviour and data*, not structure.
   Check `.opencode/context/modules.md` + `known-issues.md` for its defects so you don't port them.
2. Propose a plan (tables, routes, permissions, admin screens, API, tests) and get agreement.
3. `php artisan module:make <Name>`; RouteServiceProvider extends `ModuleRouteServiceProvider`.
4. Migrations with `_en`/`_hi` pairs; `is_active` + `is_published` where content is editorial;
   altitude band computed in `booted()` if the model has altitude.
5. Permission cases → `SystemRole::defaultPermissions()` → re-seed roles.
6. Policies registered in the module provider; `AdminMenu::add()` + `SitemapRegistry::register()`.
7. Admin views extend `layouts.admin` and reuse `x-form.*` / `x-admin.*`; public views extend
   `layouts.site` and set `SeoManager`. Behaviour in `admin.js`/`site.js` via `data-*` hooks.
8. API under `routes/api.php` with `JsonResource`s; eager-load everything.
9. Feature tests in `Modules/<Name>/tests/Feature`; `vendor/bin/pint --dirty --format agent`;
   `npm run build` if assets changed; one `composer test` at the end.

---

## 4. Design systems

There are **three** visual systems in the workspace. They share an apple-green idea but not values.

### 4.1 `baagvaani_web` (the one to build on)

Source: `resources/scss/_tokens.scss` — "the green is the admin panel's existing accent".

| Token | Value | | Token | Value |
|---|---|---|---|---|
| `$brand-green` (= `$primary`) | `#4a9278` | | `$brand-ink` (body text) | `#1a2332` |
| `$brand-green-dark` (links) | `#2d6b55` | | `$brand-muted` | `#515e75` |
| `$brand-green-soft` | `#eef6f2` | | `$brand-line` (borders) | `#eaecf0` |
| `$brand-canvas` | `#f5f7fa` | | `$brand-apple` | `#c2413b` |
| `$brand-sun` | `#e8a33d` | | `$success` / `$danger` | `#2f855a` / `#dc3545` |
| `$warning` / `$info` | `#d69e2e` / `#3182ce` | | footer mark mint | `#8fd3b6` |

Headings weight 800, line-height 1.6, radius `.5rem` (sm `.375`, lg `.875`, xl `1.25rem`), no
shadows, focus ring opacity .2. `site.scss` exposes them as CSS vars `--bv-green`, `--bv-green-dark`,
`--bv-green-soft`, `--bv-ink`, `--bv-muted`, `--bv-line`, `--bv-canvas`, `--bv-apple`, `--bv-sun`.
`core.site.theme_color` = `#4a9278`.

**Altitude band colours** (inline in `Modules/Core/resources/views/pages/home.blade.php`):
below 6000 `#b7791f` on `#fdf3e2` · 6000–8000 `#2d6b55` on `#eef6f2` · above 8000 `#c2413b` on `#fbeceb`.

**Type:** `'Nunito Variable', 'Noto Sans Devanagari', system-ui, …`; `[lang='hi']` puts Noto Sans
Devanagari first. Self-hosted through `@fontsource` in `resources/css/vendor.css` (Noto 400/600/700).
**Icons:** Bootstrap Icons (`bi-*`); the brand mark is `bi-flower1` in a 36 px green-soft tile.

**Public site (`site.scss`, layout `layouts/site.blade.php`):** sticky translucent `.site-header`
(white 92 % + blur, `.is-scrolled` adds border/shadow; navbar 68 px) with Home, Why altitude
(`#altitude`), About, FAQ (`#faq`), and Admin/My account or Log in/Get started. Building blocks:
`.section` (clamp 3.5–6 rem padding), `.section-muted`, `.eyebrow`, `.lead-muted`, `.display-title`,
`.section-title`, `.hero` (radial green + sun gradients, `.hero-badges`), `.feature-card` (hover
lift, 48 px `.feature-icon`), `.band-card` (5 px top bar via `--band-color`/`--band-soft`), `.faq`
accordion, `.cta-band` (green-dark → green), `.prose` (72ch), `.page-intro`, `.site-footer` (ink bg;
Explore / Legal / Contact / social / regions), `.auth-shell` + `.auth-card` (max 440 px),
`.error-code`, `.skip-link`, green `:focus-visible`. Partials: `head-common`, `brand`,
`site-header`, `site-footer`, `core::partials.{seo-head,page-intro,altitude-art}` (inline SVG).
Error pages 403/404/419/429/500/503.

**Admin (`admin.scss`, 676 lines, ported from the legacy admin):** `$font-size-base .9rem`, body bg
canvas. Vars `--sidebar-width 260px`, `--sidebar-collapsed-width 72px`, `--sidebar-bg #fff`,
`--sidebar-section #b0bac9`, `--topbar-h 62px`, `--card-radius 14px`. Structure: fixed white
`#sidebar` (`.sb-brand`, `.sb-nav`, `.sb-section`, `.sb-link.active`, `.sb-footer`; collapses to
icons ≥ lg, off-canvas < lg, state in localStorage), `#topbar` (`.tb-search` user search,
`.tb-icon-btn`, `.tb-user-btn`), `#main` → `.page-content` with optional page header from
`@section('page-title' | 'breadcrumb' | 'page-actions')`. Components: `.stat-card`, `.table-admin`,
`.filters-bar`, `.empty-state`, `.form-section-title`, `.permission-group`, `.upload-zone`,
`.media-grid`/`.media-tile`, `.status-dot`, `.toast-stack`, `.avatar(-sm/-lg)`; flash toasts and a
shared confirm modal.

**Blade components:** `x-form.input` (name, label, type, value, help, id, prefix), `x-form.select`
(options, placeholder), `x-form.textarea` (rows), `x-form.check` (checked, switch),
`x-admin.avatar` (user, size), `x-admin.delete-button` (action, confirm, label, iconOnly, method,
variant, icon), `x-admin.empty-state` (icon, title), `x-admin.status-badge` (active, on, off).

**JS hooks** — `core.js`: exposes `window.$`/`window.bootstrap`, CSRF header for AJAX, safe
`storage` wrapper, tooltips. `site.js`: header scroll class, closes mobile nav. `admin.js`:
`data-sidebar=open|close|toggle`, `window.adminToast()`, `form[data-confirm]` (+`data-confirm-button`)
→ modal, `form[data-autosubmit]`, `[data-copy]`, `input[data-preview]`, `[data-check-group]`,
`[data-upload-zone]` (drag-and-drop AJAX uploader with progress).
**Vite entries:** `resources/css/vendor.css`, `resources/scss/{site,admin}.scss`,
`resources/js/{site,admin}.js`; jQuery/Bootstrap/Popper in a `vendor` chunk.
**Assets:** `public/images/{logo.png, favicon.svg, apple-touch-icon.png, icon-192/512, icon-maskable-512, og-default.jpg}`.
**Site config** `core.site`: tagline "Orchard advice that knows your altitude", locale en_IN,
languages en-IN/hi-IN, regions HP/UK/J&K.

### 4.2 `web_baagicha` (legacy public site + admin)

- **Public (Tailwind 4 `@theme` in `resources/css/app.css`):** primary `#3CB371` (50 `#ecfdf3` …
  700 `#258B52`, 900 `#14522d`), accent `#F5A623`, background warm cream `#F5F0E8`, surface `#fff`,
  surface-subtle `#F7F5F2`, bg-primary `#258B52`; success `#22c55e`, warning `#f59e0b`, danger
  `#ef4444`, info `#0ea5e9`; warm greys `#F5F0E8` → `#1A1A1A`. Fonts DM Serif Display (display),
  DM Sans (body), Noto Sans Devanagari, Yatra One. Radius 8–28 px. Components `.btn-primary/
  -secondary/-accent/-ghost`, `.card` ("LeafSnap style", rounded-2xl). Icons Font Awesome 6.5.
- **Reality:** Tailwind's `@source` misses `Modules/**` (it only sees module classes through compiled
  views in `storage/framework/views`, if present at build time), so module-Blade utilities are unreliable; the real
  styling is 28 hand-written `public/css/*.css` (`style.css` 5,475 lines, with **slate** greys)
  pushed per page. Hero = `<x-core::page-hero>` + `public/css/hero.css` (`#1a4d2e` base, green
  gradient overlay). Layouts: `layouts.site` (current, 44 views), `layouts.app.base` (legacy, 19),
  `layouts.admin.app` (143), `layouts.guest`. 89 Core components.
- **Admin:** Bootstrap 5.3 Sass, Nunito, accent `#4a9278` — the origin of the rebuild's palette.
- Defects: `layouts.site` never loads its web fonts; manifest `theme_color #3a7d44` vs meta
  `#258B52` (known-issues #10).

### 4.3 `baagichaApp` (mobile)

`src/theme/colors.ts` mirrors the legacy public palette: primary `#3CB371` (bgPrimary `#258B52`),
accent `#F5A623`, cream `#F5F0E8` background, white surfaces, severity critical `#ef4444` /
high `#f97316` / medium `#f59e0b` / low `#22c55e`. Light theme only. Spacing `Space` 1–10 =
4/8/12/16/20/24/32/40/48/64; radius sm 8 / md 12 / lg 16 / xl 20 / 2xl 24 / 3xl 28 / full 999;
cards white with radius 24. Type tokens in `src/typography/` (hero 23, h1 20, h2 17, h3 15, body
14, caption 12) with DM Serif Display / DM Sans / Noto Sans Devanagari / Yatra One — **declared but
not bundled**, so system fonts render. Icons MaterialCommunityIcons. Custom components only.

**Open design question:** the rebuild uses `#4a9278` + Nunito; the app and legacy public site use
`#3CB371` + DM Sans/Serif. Nobody has decided whether the app follows the rebuild. Ask before
"unifying" anything.

---

## 5. `web_baagicha/` — the live legacy backend

Laravel 12.58 · PHP 8.5 runtime (`^8.2`) · MySQL `baagicha` · nwidart modular monolith.
**`web_baagicha/CLAUDE.md` is accurate — read it before any change here.** Use it as a reference
and for production fixes; new features go to the rebuild.

- **17 modules:** Auth, Blog, Comment, Community, Core, Disease, Fruit, Intelligence,
  KnowledgeBase, Newsletter, Notification, Orchard, Rootstock, Shop, VarietyStrain, Vendor, Weather.
  (`modules_statuses.json` still lists deleted `Variety`/`Strain`.) Feature code is in `Modules/`,
  `app/` is nearly empty. Tarun's working set: Fruit, VarietyStrain, Rootstock, Blog, Comment,
  Core, Notification, Newsletter (+ Auth). VarietyStrain is the house pattern for admin modules.
- **Routing:** per-module RouteServiceProvider; `web.php`; `api.php` → `/api`, `api.`; `admin.php` →
  `web,auth,role:admin|manager`, `/admin`, `admin.`. ~631–638 routes, **179 API routes**, almost all
  under `/api/v1`; legacy unversioned `api/brands*`, `api/weather/{current,coordinates,alerts,refresh}`.
- **Auth:** Breeze, login by email *or* phone; Sanctum bearer for mobile (`v1/auth/otp/send`,
  `otp/verify`, `login`, `register`, `social`, `refresh`, `logout(-all)`, `profile`,
  `change-password`); 18 Spatie roles (admin, manager, farmer, vendor_*, warehouse/content/…);
  `Gate::before` grants admin everything. SMS drivers mock (default) / msg91 / twilio.
- **Domain engines:** `Modules/Disease/app/Services/Prediction/` (Revised Mills scab, simplified
  Maryblyt fire blight, DMC powdery mildew, degree-day pests; never validated, **unscheduled and
  unrouted** — known-issues #9), `Modules/Intelligence` (Daily Orchard Intelligence Card, wired into
  the app), `Modules/Weather` (OpenWeatherMap + IMD with JWT, VPD/Delta-T/fertigation).
- **Assets:** `npm run build` = vite + `scripts/copy-assets.js` (mandatory). Page CSS in
  `public/css/<page>.css` via `@push('styles')` — never inline, never in `style.css`.
- **Tests:** `composer test` → 404 passed (2026-09-06), ~145 s. Pest runner, PHPUnit-style classes.
- **Deployment:** Hostinger shared hosting, manual, no CI. Cron runs `queue:work`
  per minute; the recorded line drains only `default,notifications` but jobs also use `intelligence`
  and three `weather-*` queues (known-issues #12). Scheduler: `routes/console.php` + module providers.
- **Known defects to not port:** see `.opencode/context/known-issues.md` (24 broken `route()` names,
  e.g. `varieties.show`; dead route files in Auth; coupon not validated at cart; no CSP; etc.).

---

## 6. `baagichaApp/` — React Native client

RN 0.85.3 · React 19.2.3 · TypeScript strict · CLI (not Expo) · Node ≥ 22.11 · Android-first
(`com.baagichaapp`, minSdk 24, target 36, new arch + Hermes). Talks to **`web_baagicha`** `/api/v1`.

- **Navigation:** root native stack picks Welcome → Auth → NotificationPermission →
  LocationPermission → MainTabs (first launch), Auth (logged out), EmailVerification (unverified
  email), MainTabs. AuthStack: Login, EmailRegister, PhoneAuth, ForgotPassword, EmailVerification,
  Onboarding. **Tabs:** Home · Spray · Shop (centre FAB) · Discover (labelled "Baagicha") ·
  MyOrchard (labelled "Orchard"), each a native stack. Home is a segmented My Farm / Community view
  and its stack also hosts varieties, diseases, weather, blog, rootstocks, community, groups,
  stories, notifications, tools. 55 `*Screen.tsx`. `CommunityStack.tsx` and `OnboardingStack.tsx` unused.
- **State:** 7 Zustand stores (auth, cart, intelligence, notification, onboarding, orchard, toast);
  5 hand-written MMKV instances (auth encrypted, cart, intelligence, onboarding, orchard). No Context,
  no Redux, no react-query.
- **API:** `src/services/api.ts` axios, 15 s timeout, bearer from MMKV; 401 → one `POST /auth/refresh`
  then logout; 403 "verify" → EmailVerification, other 403 → logout; 429 toast. 17 domain clients +
  19 hooks. Base URL from `react-native-config`, fallback LAN `http://192.168.1.100:8000/api/v1` —
  **no production URL exists**. Firebase messaging, Google/Facebook sign-in, Razorpay, geolocation
  (+ Nominatim reverse geocoding).
- **Health:** `tsc` 4 errors; only the default Jest test; release blockers in known-issues #7 / #11.
- **Broken calls:** several app endpoints have no backend route (variety endpoints use `/varieties`,
  backend has `/varietystrains`; pest-trackers; report-types; follow/connect) — known-issues #11.
- **Docs:** `baagichaApp/.opencode/AGENTS.md` + `CLAUDE.md` (corrected 2026-10-04) and skills
  `api-reference`, `data-models`, `design-spec`, `kisan-tools`, `prediction-types`, `screen-breakdown`.

---

## 7. `BaagvaaniBrain/` — content pipeline

Content only: no build, tests or server. Spec: `social-media-content/baagvaani-brain/INSTRUCTIONS.md`.
Rules: the agronomist's `.docx` is the truth; `english.md` is **verbatim**; `hindi.md` matches meaning
in spoken Hinglish per `hinglish-glossary.md` ("if a farmer wouldn't say it at a pahari tea shop, use
the English word in Devanagari"); HTML with 11 tags only (h1–h3, p, ul, ol, li, strong, em,
blockquote, br); special characters entity-encoded; `manifest.md` tracks status; never edit `raw-blog/`.

**Blog flow** (run in `social-media-content/baagvaani-brain/`, needs `python-docx` + `Pillow`):
`extract-docx.py --list` → `--report` (flags ambiguous bold lines) → `--write [--slug]` creates
`../blogs/<slug>/english.md` → AI fixes tags, adds `<!-- IMAGE n -->` markers and a ≤ 500-char
excerpt → AI writes `hindi.md`, `metadata.md` (slug, category, SEO title ≤ 60 / description ≤ 155 in
EN+HI, 5–10 tags, Facebook posts, related products/diseases/varieties/chemicals), `prompts.md`
(3–4 image prompts, 50–100 words, photoreal Himalayan, "No text, words, labels, or watermarks";
prompt 1 featured 1:1, 2–3 4:3) → `validate.py <slug> --source "<fragment>"` → manifest row `done`.
13 of 13 raw docx are done; 7 blogs have no images yet.
**Images:** generated by hand in ChatGPT/Gemini; `compress-images.py <slug> --quality 92` crops to
1200² / 1600×1200 JPEG; the site library (`social-media-content/images/`, `node processor.js`,
dashboard on :3099) crops and compresses to WebP per `resolutions.json` (17 sizes, e.g. blog
featured 1200×675 ≤ 300 KB, OG 1200×630).
**To the website:** manual — HTML pasted into the admin editor, images uploaded through Media
Library (`research/IMAGE_UPLOAD_GUIDE.md`). No importer in either Laravel app. Skills:
`.claude/skills/{harvest,compress-images}`, `.opencode/skills/content-harvest`. `PORTABLE-PROMPT.md`
for chat AIs without repo access. Research: `research/{market,competitors,revenue-model,prediction-engine}/`.

---

## 8. Environments, services, credentials (pointers only — no values here)

| Item | Where |
|---|---|
| Local PHP 8.5.4, MySQL on 127.0.0.1:3306, user `root` | password in each app's `.env` (untracked) |
| `baagvaani_web` | `.env` (from `.env.example`), DB `baagicha_db`, serve on **:8123** |
| `web_baagicha` | `.env` (untracked), DB `baagicha`, serve on :8000 |
| Port 8000 on 192.168.1.100 | may be occupied by another project (`wyldworkspace/wyld_web`) — check `ss -ltnp` |
| OpenWeatherMap, IMD, MSG91, Gmail SMTP, Google/Facebook OAuth, Razorpay, Firebase | keys in `web_baagicha/.env`; Firebase setup in `baagichaApp/FIREBASE_SETUP.md`, `google-services.json` |
| Mobile keys | `baagichaApp/.env` (**tracked — rotate/untrack**), `strings.xml`, `src/config/env.ts` fallbacks |
| Production | Hostinger, `/home/u896019069/domains/baagvaani.com/web_baagicha` |
| MSG91 for the rebuild | `MSG91_AUTH_KEY`, `MSG91_TEMPLATE_ID`, `MSG91_SENDER_ID` in `baagvaani_web/.env` (DLT template pending) |

`.claude/settings.local.json` contains the local MySQL password inside Claude permission rules —
local only; never copy it anywhere.

---

## 9. OpenCode setup in this workspace

- **Rules loading:** OpenCode walks *up* from the start directory and uses the first `AGENTS.md`
  (falling back to `CLAUDE.md`); it does not read `.opencode/AGENTS.md`. So:
  - root `AGENTS.md` — workspace rules (this handover's companion);
  - `baagvaani_web/AGENTS.md` — project section + Laravel Boost guidelines; its `opencode.json`
    also loads `../AGENTS.md`;
  - `web_baagicha/opencode.json` loads `.opencode/CLAUDE.md` and `../AGENTS.md`;
  - `baagichaApp/opencode.json` loads `../AGENTS.md`, `.opencode/AGENTS.md`, `.opencode/CLAUDE.md`.
- **Skills:** root `.opencode/skills/{cross-project-context, ecommerce-plan, laravel-api-architecture,
  prediction-engine}`; per repo under `*/.opencode/skills/`; `baagvaani_web/.agents/skills/`
  (Boost: infer-conventions, laravel-best-practices, testing-best-practices, deploying-to-cloud).
- **MCP:** `laravel-boost` (`php artisan boost:mcp`) in `baagvaani_web` and `web_baagicha`
  `opencode.json` — prefer its `search-docs`, `database-schema`, `database-query`,
  `get-absolute-url`, `browser-logs` tools. `database-query` on `web_baagicha` reads the live-mirror
  DB — read-only queries only.
- **Global:** `~/.config/opencode/opencode.jsonc` is empty apart from the schema.

---

## 10. Where to start

1. Ask Tarun what he wants next — most likely the next feature for `baagvaani_web` (open question
   R1) or one of the pending pushes/deploys in §2.
2. Before any rebuild feature: read §3 and the matching legacy module notes; propose a plan first.
3. Keep `.opencode/context/` (and `.claude/context/`) current when you learn something durable —
   that's how the next agent inherits it.
