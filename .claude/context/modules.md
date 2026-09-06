# Module analysis — Blog, VarietyStrain, Disease

Measured 2026-09-06 against the live tree and the local database. Blog and VarietyStrain are
the two modules Tarun considers "almost done" and are live; Disease is the next work area.

---

## The house pattern

VarietyStrain is the most evolved admin module and is the one to copy:

- Multi-tab admin form: `_form.blade.php` + `_form_tabN_*.blade.php` partials
- Full soft-delete lifecycle: `trashed` listing + `restore` + `force-delete`
- Toggle routes for `status` / `published` / `featured`
- Gallery management with per-media delete
- Dedicated pivot managers (attach / update-pivot / detach) per relationship
- Public `Web/` controller + Blade views, thin `Api/` controller for the app

Notably **none** of the three modules has a `Services/` directory or a single module test.
Logic lives in 500-line admin controllers. That is the current norm, not an aberration.

---

## Blog — close

| | |
|---|---|
| Controllers | 1,514 LOC; `Admin/BlogPostController` alone is 534 |
| Authorization | Policy-backed, 14 `authorize()` calls |
| Data | 12 blog posts, all published |
| Extras | revisions, scheduled publishing, RSS feed, search, OG-image → media command |

**Gaps:** no service layer (534 lines of orchestration in one controller); zero module tests.

**Fixed 2026-09-06:** three empty generator-stub controllers at
`app/Http/Controllers/{Blog,BlogCategory,BlogTag}Controller.php` — they carried
`namespace App;` while living under `Modules/Blog`, and were unrouted and unreferenced. Deleted.

---

## VarietyStrain — close, one defect found and fixed

| | |
|---|---|
| Controllers | 1,119 LOC; `Admin/VarietyStrainController` is 495 |
| Admin form | 7 tabs, 891 LOC — `_form_tab5_relationships` alone is 275 |
| Data | 211 variety strains |
| Pivots | rootstocks, diseases, pollinizers — each with attach/update/detach routes |

**Fixed 2026-09-06 — missing policy.** The admin controller made 22 `authorize()` calls across
nine abilities (`viewAny`, `view`, `create`, `update`, `delete`, `restore`, `forceDelete`,
`toggleStatus`, `togglePublished`) with **no `VarietyStrain` policy registered** — the only model
in the app in that state. `Gate::before` grants `admin` everything, hiding it; `manager`, which
`role:admin|manager` admits to the routes, was denied on every action. Latent, since the
`manager` role has 0 users. `VarietyStrainPolicy` added (mirrors `RootstockPolicy`), registered
in `AppServiceProvider`, and guarded by `tests/Feature/Admin/VarietyStrainAuthorizationTest.php`
— verified by deleting the policy file and watching `manager` drop to 403.

**Still open:**
- `toggle-featured` calls no `authorize()` at all — middleware-gated only.
- `variety_strain_disease` has **4 rows** against 211 strains. Essentially unpopulated.
- `database/seeders/VarietyStrainDatabaseSeeder.php.bak` is committed.
- No policy directory existed before; no tests, no services.

---

## Disease — the next work area

Ambitious code, thin data, and a chunk of it not wired up.

### Size

| | |
|---|---|
| Controllers | 9 files; `Admin/DiseaseController` 518 LOC, `Api/DiseaseController` 341 |
| Model | `Disease.php` 466 LOC — 7 scopes, 10 relationships |
| Admin form | 9 tabs, 1,155 LOC |
| Public views | 1,107 LOC; `app/disease/show.blade.php` alone is 707 |
| Services | 19 files, incl. the whole `Prediction/` engine |
| Jobs / commands | 5 jobs, 5 console commands |

### 457 lines that no route reaches

Checked against all 638 registered routes:

| Controller | LOC | Status |
|---|---|---|
| `Api/PredictionController` | 282 | **unrouted** |
| `Api/PestTrackerController` | 131 | **unrouted** |
| `Api/ReportTypeController` | 44 | **unrouted** |

The entire prediction engine — Revised Mills, simplified Maryblyt, DMC, degree-day — has no HTTP
surface. Nothing can consume it.

`routes/web_disease_reporter.php` was also never loaded (the provider maps only web/api/admin)
and duplicated routes already in `web.php`. **Deleted 2026-09-06.**

### The data behind the advanced features is largely empty

| Table | Rows |
|---|---|
| `diseases` | 46 (all published) |
| `disease_conditions` | 43 — **every row `optimum`; zero `moderate`, zero `safe`** |
| `fruit_disease` | 44 |
| `chemical_target_efficacies` | 78 |
| `variety_strain_disease` | 4 |
| `pest_models` | **0** |
| `pest_tracker` | 0 |
| `disease_pressure_log` | 0 |
| `disease_reports` | 0 |
| `report_types` | 25 |

Breakdown: 14 fungal, 22 pest, 8 physiological, 2 bacterial · 35 disease / 9 insect / 2 mite.

Of 46 diseases, **1** is flagged `is_mills_applicable`, **1** `is_maryblyt_applicable`, **1**
`is_dmc_applicable`. The 22 pest diseases have no `pest_models` rows to drive the degree-day
model. The 2026-08-30 "optimum/moderate/safe bands" work is one-third populated.

### The mobile app cannot see the newest content

`Api/DiseaseController::show()` returns `ipm`, `chemical_control`, `conditions`, `chemicals`,
`efficacy_stars` (added 2026-08-15 and 2026-08-30). The app's `DiseaseDetail` interface in
`baagichaApp/src/services/diseaseApi.ts` stops at `risk_humidity_pct` + `related` — none of those
fields are declared, so the app renders none of them. The public web view uses all of them.

### Parity gaps against VarietyStrain

- `_form_tab7_relationships.blade.php` is an **11-line stub** (three `<x-*-selector>` components);
  VarietyStrain's equivalent is 275 lines of real pivot editing.
- **No trashed listing view**, though `restore` and `force-delete` routes exist and the policy
  implements both — the routes are unreachable from the UI.
- No `is_featured` column or toggle, unlike varieties / rootstocks / chemicals.
- `disease_conditions` has **no altitude dimension** — no `altitude_band` column — even though
  altitude is the product's central business rule and spray timing shifts ±14 days by band.

### Things that are genuinely good here

`DiseasePolicy` is registered and used (12 `authorize()` calls). `DiseaseConditionTest` exists —
one of only four modules with any test at all. The `ValidatesDiseaseConditions` trait centralises
band validation. `Api/DiseaseController` already shapes bilingual label objects for the app.

---

## Module inventory after the 2026-09-06 cleanup

17 modules. `OrchardActivities` was removed — the only one outside the transitive dependency
closure of everything in use, with zero inbound references and three empty tables.

**The working set Tarun actually uses (8 modules + Auth):**
Fruit · VarietyStrain · Rootstock · Blog · Comment · Core · Notification · Newsletter

Mapped from the live admin URLs: `/admin/fruits` `/admin/variety-strains` `/admin/rootstocks`
`/admin/blog/posts` `/admin/blog-categories` `/admin/blog-tags` `/admin/comments` `/admin/media`
`/admin/dashboard/queue-health` `/admin/activity-logs` `/admin/notifications/send`
`/admin/waitlist` (Notification) `/admin/newsletter` (Newsletter).

**Why nothing else can be removed yet.** Blog and VarietyStrain are not separable:

- VarietyStrain → `Fruit` (belongsTo), `Rootstock` + `Disease` (pivots), `Comment` (morphMany),
  `Community` (`Likeable` trait), `Core`, `Auth`
- Blog → `VarietyStrain`, `Disease`, `KnowledgeBase\Chemical`, `Shop\Product`, `Rootstock` via
  `BlogPostRelated`; plus `Comment`, `Community\Likeable`, `Shop\HasProducts`

And Disease — the next work area — depends on the removal candidates heavily:

| Disease needs | Files |
|---|---|
| `Orchard` (`UserOrchard` drives the whole prediction engine) | 23 |
| `Weather` (`Weather` model feeds every prediction model) | 9 |
| `KnowledgeBase` (`Chemical`, `ChemicalTargetEfficacy`, `DevelopmentStage`) | 4 |
| `Shop` (`HasProducts`, `Product`) | 2 |
| `Community` (`Post` in a job) | 1 |

**Removing Orchard, Weather or KnowledgeBase would sabotage the Disease work.**

`Intelligence` is removable server-side (0 rows, only Core's base layout references it) **but the
mobile app renders `DailyIntelligenceCard` inside `ScreenLayout`, which 13 screens use including
Home.** Deleting the backend 404s all of them. Held pending a decision.

Live data that must never be dropped casually: Community 1,012 rows (253 follows, 182
connections, 180 group members), Shop 277 incl. 42 orders, Orchard 207 user orchards, Auth 113
users, KnowledgeBase 1,406, VarietyStrain 3,872, Blog 259 incl. 173 comments (all on Community
`Post`, not blog posts).

## Cross-cutting: 24 broken route() calls

An audit of every `route('name')` in the codebase against the 631 registered routes found **24
names that do not exist** — these throw `RouteNotFoundException` when their code path runs.
Pre-existing, not caused by the cleanup. The notable ones:

| Route name | Called from | Likely cause |
|---|---|---|
| `varieties.show` | `Blog\BlogPostRelated`, Core `variety-card` components, `Newsletter\SendContentPublishedNewsletter` | leftover from the Variety → VarietyStrain rename; the route is now `variety-strain.show` |
| `admin.spray.stages.{store,edit,update}` | KnowledgeBase spray stage admin views | |
| `admin.varieties.show`, `api.predictions.index`, `api.spray-window` | `Notification\NotificationService` | |
| `api.intelligence.{dismiss,expand,items.done}` | Intelligence blade components | double `api.` prefix — actual names are `api.api.intelligence.*` |
| `shop.orders.invoice` | Shop order view | |
| `user-preferences.update` | Auth preferences view | |

`varieties.show` is the one worth fixing first: it sits in the blog related-content renderer and
in the newsletter listener, so it can break a live page and a live email.

## Cross-cutting: dead route files

`Modules/Auth/routes/` contains three files the module's `RouteServiceProvider` never loads:
`admin-roles.php`, `admin-users.php`, `web-preferences.php`. Their routes are declared inline in
`admin.php` instead, so these are stale duplicates. (`web-profile.php` **is** loaded, via a
`require` inside `mapWebRoutes`.) Left in place — not yet approved for deletion.
