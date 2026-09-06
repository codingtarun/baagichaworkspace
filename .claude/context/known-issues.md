# Known issues — confirmed, with evidence

Ranked by consequence. Every item here was reproduced on 2026-09-06, not inferred.
Nothing has been fixed — this is a findings list awaiting your decisions.

---

## 1. Publishing a Chemical crashes, and takes 14 tests with it

**Severity: high — user-facing, blocks a whole content type.**

`Modules/Newsletter/resources/views/emails/content-published.blade.php:25` calls
`$content->getDisplayName('en')` unguarded, inside the featured-image block:

```blade
@if (isset($content) && method_exists($content, 'getFeaturedImageUrl') && $content->getFeaturedImageUrl('large'))
    <img ... alt="{{ $content->getDisplayName('en') ?? '' }}" ...>
```

`Modules\KnowledgeBase\Models\Chemical` implements `HasMedia` and so passes the
`getFeaturedImageUrl` guard, but **defines no `getDisplayName()`** →
`BadMethodCallException` → `ViewException`.

Nine other content models do define it (`Fruit`, `Disease`, `VarietyStrain`, `ChemicalGroup`,
`DevelopmentStage`, `Product`, `Brand`, `BlogCategory`, `BlogTag`, `OrchardVariety`) — and note
two different shapes are in use: `getDisplayName(string $locale)` on knowledge models vs. the
Eloquent accessor `getDisplayNameAttribute()` on Blog/Shop models. The template assumes the first.

**Blast radius:** `Modules/Newsletter/app/Traits/PublishesNewsletterContent.php:33` renders this
view synchronously, so every path that publishes a chemical throws. 14 of the 17 suite failures
are this one bug: all of `Tests\Unit\Models\ChemicalTest` (6), `Tests\Feature\Admin\ChemicalTest`
(4), `Tests\Feature\App\ChemicalPageTest` (3), `Tests\Feature\App\SprayScheduleServiceTest` (1).

**Two candidate fixes** — needs your call: add `getDisplayName()` to `Chemical`, or harden the
template with a `method_exists` guard. I'd do both, plus unify on one naming convention.

---

## 2. Duplicate newsletters and notifications on edit-after-create

**Severity: high — sends real email to real subscribers, twice.**

`Modules/Core/app/Observers/ContentObserver.php` hooks `saved()`, which fires on **both** create
and update. `dispatchPublishedEvent()` then fires when:

```php
$isNewlyPublished = $model->wasRecentlyCreated;
$transitionedToPublished = $model->wasChanged('is_published');
if ($isNewlyPublished || $transitionedToPublished) { ContentPublished::dispatch(...); }
```

`wasRecentlyCreated` stays `true` on that model instance for the rest of the request — it is not
reset by a subsequent save. So creating a published item and then editing it in the same request
dispatches `ContentPublished` **again**. `ContentPublished` is listened to by both
`SendContentPublishedNewsletter` and `SendContentPublishedNotification`, so the duplicate reaches
every subscriber.

Reproduced by `Tests\Feature\NotificationSystemTest`: the unpublish test sees 1 dispatch, the
non-publish-update test sees **2**.

The fix is to split the observer into `created()` and `updated()` rather than sharing `saved()`.
Note that two of those test cases are also arranged in a way that would trip the intended
create-path dispatch regardless, so the tests need adjusting alongside the fix.

---

## 3. Tailwind never sees the module Blade files

**Severity: medium — it explains the whole CSS situation and it is a trap for future work.**

This is Tailwind **v4**. The real config is the `@source` block in `resources/css/app.css`:

```css
@source '../**/*.blade.php';   /* resolves to resources/**  → 10 files */
```

There are **425 Blade files in `Modules/`** and **10 in `resources/views/`**. Module views are
outside every `@source` glob, so any utility class used only in a module Blade is purged.

Confirmed against the built `public/css/app.css`: `Modules/Core/.../page-hero.blade.php` uses
`bg-primary-900/90`, `lg:px-8`, `from-primary-900/90` — the built stylesheet contains **zero**
occurrences of `bg-primary-900` and **zero** of `lg:px-8`.

Two consequences:

- The site still looks right because `public/css/hero.css` hand-implements `.page-hero`,
  `.page-hero-overlay`, `.page-hero-content` etc. as semantic CSS. **The 28 hand-written
  `public/css/*.css` files are the real styling system; the Tailwind classes in module Blades
  are decorative no-ops.**
- `.opencode/skills/cross-project-context/SKILL.md` tells agents to build heroes out of Tailwind
  utilities (`bg-gradient-to-r from-primary-900/90 ...`). Following that advice produces
  invisible styling. **That guidance is wrong as written.**

`tailwind.config.js` is a leftover **v3** config that Tailwind 4 ignores entirely — its `content`
array is dead code and misleads anyone who reads it first.

Decision needed: extend `@source` to `Modules/**` and go Tailwind-first, or delete the Tailwind
pretence from module views and commit to the semantic CSS. Doing neither is the current state.

---

## 4. `BaagvaaniBrain` is an unclonable submodule

**Severity: medium — the workspace cannot be reconstructed from git.**

The workspace repo records `BaagvaaniBrain` as a gitlink:

```
160000 fb9d2b181f32a3e9e977a1da6b512ea2892d060d 0  BaagvaaniBrain
```

but there is **no `.gitmodules` file**. A fresh clone yields an empty directory that
`git submodule update --init` cannot fill, because git has no URL to fetch from. Four workspace
commits are titled "update BaagvaaniBrain submodule", so this has been silently half-working for
a while.

Fix is a one-liner (`git submodule add https://github.com/codingtarun/BaagvaaniBrain.git`) but it
needs a decision on whether the workspace should track it as a submodule at all, given the other
two sub-projects are simply gitignored.

---

## 5. Three months of work sits on an unmerged feature branch

**Severity: medium — process, not code, but it is the biggest single risk.**

`web_baagicha` is on `feature/fruit-module`, **98 commits ahead of `master`**, which is 0 ahead.
`master`'s last commit is 2026-06-16; the branch's is 2026-08-30. `origin/HEAD` still points at
`master`, so anyone (or any tool) cloning the default branch gets a June snapshot missing the
Fruit refactor, VarietyStrain consolidation, Intelligence module, IMD weather, and the Disease
rework.

There is also a `backup/modular-migration-20260611-221110` branch still hanging around.

---

## 6. `area_unit` has no `acre`, but the product speaks in acres

**Severity: low-medium — a units inconsistency worth resolving deliberately.**

`user_orchards.area_unit` and `orchard_blocks.area_unit` are
`enum('bigha','kanal','nali','hectare')`, and all six validation sites agree
(`nullable|in:bigha,kanal,nali,hectare`). But migration
`2026_07_16_113712_rename_density_per_ha_columns_to_density_per_acre` moved tree density to
**per-acre**, and `Tests\Unit\Models\UserOrchardTest > area hectare syncs from acre` expects
`acre` to be storable — it fails with `CHECK constraint failed: area_unit`.

So density is per-acre while area cannot be expressed in acres. Acre is one of the units
Himalayan growers actually use. Either add it to the enum (a migration plus six validation
sites) or delete the stale test.

---

## 7. Mobile app: 4 TypeScript errors, no production API URL

**Severity: low individually, but #7c blocks any real release.**

```
__tests__/App.test.tsx:9         TS2582  @types/jest not installed
src/screens/OrchardDetailScreen.tsx:71   TS2345  navigation arg typed [never, never]
src/screens/WeatherScreen.tsx:74,77      TS2345  {message,type} passed where string expected
```

The two `WeatherScreen` errors look like a real shape mismatch between what the error handler
produces and what the toast store accepts, not just a typing nit.

**7c:** `src/config/env.ts` defaults `API_BASE_URL` to `http://192.168.1.100:8000/api/v1` — a LAN
address. There is no production API base URL anywhere in the repo, and `baagichaApp/.env` (which
is committed) has placeholder Google and Facebook credentials. The app cannot currently be built
for anyone outside your WiFi.

---

## 8. Smaller things

- **`baagichaApp/.env` is tracked in git** and contains a real `FACEBOOK_CLIENT_TOKEN`. Rotate
  and untrack. (`web_baagicha/.env` is correctly ignored.)
- **No CSP header.** `Modules/Core/app/Http/Middleware/SecurityHeaders.php` sets nosniff,
  `X-Frame-Options: DENY`, referrer and permissions policy, but no Content-Security-Policy.
- **No service worker**, so the "Web PWA" is a manifest and an install prompt, nothing offline.
- **Six unversioned API routes** — `api/brands`, `api/brands/{slug}`,
  `api/weather/{current,coordinates,alerts,refresh}` — against 138 under `/api/v1`.
- **Module test coverage is near zero** for the biggest modules: Shop, Auth, KnowledgeBase, Core,
  Community, Blog have no tests inside the module.
- **Prediction engine has never been validated.** Its own docs put it at "awaiting shadow mode
  validation (weeks 11–12)". It is giving spray advice derived from Mills/Maryblyt/DMC with no
  measured accuracy against Himalayan outcomes.
- **`CartService.php:104`** — `TODO: Validate coupon via CouponService in Phase 5`. Coupons are
  not validated at cart time.
- **Stray files:** `web_baagicha/{test.php,test2.php,variety-console-errors.log,
  social-media-content.zip,agent-test-reports/}`; ~100 untracked `.playwright-mcp/` artifacts at
  the workspace root (plus ~200 already committed).
- **`modules_statuses.json`** still lists `Variety` and `Strain` as disabled modules whose
  directories no longer exist.
