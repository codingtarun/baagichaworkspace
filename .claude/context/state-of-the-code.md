# State of the code — measured audit

Everything below was measured on **2026-09-06**, not read from the project's own docs. Where the
docs disagree with these numbers, the docs are wrong.

## Headline

This is a **large, genuinely well-built codebase** that has drifted out of alignment with its own
documentation, and whose repository hygiene has not kept up with the code. The code quality is
better than the surrounding paperwork suggests.

Evidence for "well-built": strict types and `final` classes enforced by Pint, thin controllers
with 62 extracted services, Form Requests for validation, policy-based authorization, only **2
TODO comments** across all of `Modules/` and `app/`, and **zero** `dd()`/`dump()`/`var_dump()`
leftovers. That is unusually disciplined for a solo AI-assisted project.

## Test suite

`composer test` → **404 passed, 0 failed, 1 deprecated** (838 assertions, 141 s), as of the
2026-09-06 stabilisation pass.

It was 387 passed / 17 failed when I took over. The 17 collapsed into 3 root causes, all now
fixed — see [known-issues.md](known-issues.md) #1, #2 and #6.

61 test files, but they are almost all in the root `tests/` tree. Module test coverage is nearly
absent — only Weather (6 files), Intelligence (3), OrchardActivities (3) and Disease (1) have any
tests inside the module. **Shop (148 php files), Auth (113), KnowledgeBase (143), Core (172),
Community (77) and Blog (65) have no module tests at all.**

What those 17 were:

| Root cause | Failures | Status |
|---|---|---|
| `Chemical::getDisplayName()` missing | 14 | fixed |
| `ContentPublished` re-dispatched on edit-after-create | 2 | fixed |
| `area_unit` rejected `acre` | 1 | fixed |

Full detail in [known-issues.md](known-issues.md).

## Repository hygiene — the weakest area

| Repo | Branch | State |
|---|---|---|
| `web_baagicha` | `feature/fruit-module` | `master` was **98 commits behind** with `origin/HEAD` pointing at it. Fast-forwarded locally on 2026-09-06 — `master` and `feature/fruit-module` are now identical. **Not yet pushed**, and `origin/HEAD` still points at the stale remote `master`. |
| `baagichaApp` | `main` | 2 files dirty (`RootstockDetailScreen.tsx`, `rootstockApi.ts`) |
| `BaagvaaniBrain` | `main` | 19 files dirty, incl. 2 whole untracked blog packages and an untracked `CLAUDE.md` + `.claude/` |
| workspace root | `main` | `BaagvaaniBrain` gitlink modified; ~100 untracked Playwright artifacts |

Three months of work — the Fruit refactor, VarietyStrain, Intelligence, IMD weather, the Disease
rework — lived only on `feature/fruit-module`. Resolved locally by fast-forward (`master` was a
clean ancestor, so no merge commit and no conflicts). **Still needs pushing**, which is a
deliberate outward-facing step and is waiting on Tarun.

## Documentation drift

The project accumulated instruction files from several AI tools (`.ai/`, `.kimi/`, `.opencode/`,
`.claude/`). They are now of very mixed reliability:

| Document | Verdict |
|---|---|
| `web_baagicha/CLAUDE.md` | **Accurate.** The best document in the project. Trust it. |
| `BaagvaaniBrain/CLAUDE.md` | **Accurate.** |
| `.opencode/AGENTS.md` (workspace) | Accurate |
| `.opencode/skills/cross-project-context/SKILL.md` | **Corrected 2026-09-06.** Its hero-styling section told agents to use Tailwind utilities, which are purged in module views. |
| `baagichaApp/.opencode/AGENTS.md` | **Corrected 2026-09-06.** Had prescribed React Context + AsyncStorage + react-query and tabs Home/Spray/Disease/Varieties/Rootstock, plus `baagicha://` deep links that are not registered and a `https://api.baagicha.app` base URL never used. |
| `baagichaApp/.opencode/CLAUDE.md` | **Corrected 2026-09-06.** Had described the app as an empty bootstrap rendering the default RN template screen, with no navigation, state or API client. |
| `web_baagicha/DOCS/backend-status.md`, `DOCS/progress.md` | Last audited 2026-03-13, before the `Modules/` migration. Controller paths and "still hardcoded demo data" claims are unverifiable against today's tree. |
| `web_baagicha/.opencode/skills/*` | Conventions right, paths stale ("no API layer", "no repository pattern" — both now false) |

## Feature reality check

| Area | State |
|---|---|
| Admin panel | Largest surface: 337 admin routes, 52 admin controllers. Genuinely complete CRUD. |
| Public website | ~70 public GET routes. Fruits, varieties/strains, rootstocks (with compare + PDF), diseases, chemicals, blog, spray schedule, weather, orchards, saved items, notifications, disease reporter. |
| Knowledge content | Real: 9 fruits, 211 variety strains, 123 rootstocks, 46 diseases, 50 chemicals. This is the moat and it is populated. |
| Prediction engine | Backend complete (Mills / Maryblyt / DMC / degree-day). Documented as awaiting "shadow mode validation" — i.e. **never validated against real outcomes**. |
| Intelligence card | Full pipeline built, wired into the mobile app. |
| Shop / eCommerce | 25 models, 69 admin + 38 api routes, Razorpay, GST, invoices, coupons, warehouses, vendor onboarding. Substantial. `CartService` still has a `TODO: Validate coupon ... in Phase 5`. |
| Community | 77 php files, 44 api routes, but only 5 Blade views — effectively **mobile-only**. |
| Spray schedule | Only **1** `spray_schedule_templates` row in the local DB against 9 fruits. Thin. |
| PWA | `site.webmanifest` only. **No service worker** — not installable-offline, despite "Web PWA" language throughout the docs. |
| Hindi UI | Data layer bilingual; interface is not. No `lang/` dir, 7 Blade files use `__()`. |

## Mobile app health

`npx tsc --noEmit` → **4 errors**:

- `__tests__/App.test.tsx:9` — `@types/jest` not installed
- `src/screens/OrchardDetailScreen.tsx:71` — `[never, never]` navigation arg
- `src/screens/WeatherScreen.tsx:74,77` — passing `{message, type}` where `string` is expected

Test coverage is a single default `App.test.tsx`. No component or hook tests exist despite the
AGENTS.md prescribing Jest + Testing Library + Detox.

## Local database

`baagicha` on local MySQL, 138 tables, all 180 migrations applied (179 at handover, plus the
`acre` enum migration). **Every user (113) and order
(42) row was created on 2026-08-14** — this is a seeded/imported development database, not a
mirror of production traffic. Do not read product signal from these counts.

`weather_data` and `community_posts` do not exist under those names; check actual table names
before writing raw SQL.

## Stray files worth cleaning

`web_baagicha/`: `test.php`, `test2.php`, `variety-console-errors.log`,
`social-media-content.zip`, `agent-test-reports/`.
Workspace root: ~100 untracked `.playwright-mcp/` logs and page snapshots (and ~200 already
committed).

## Security notes

- `web_baagicha/.env` is correctly untracked.
- **`baagichaApp/.env` IS tracked in git.** It currently holds placeholders plus a real
  `FACEBOOK_CLIENT_TOKEN`. Worth rotating and untracking.
- `SecurityHeaders` sets nosniff / DENY / referrer / permissions policy but **no CSP**.
- Local dev MySQL uses `root` with a password that appears in `.claude/settings.local.json`
  permission entries. Fine locally; make sure it is not the production credential.
