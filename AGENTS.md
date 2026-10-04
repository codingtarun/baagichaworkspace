# Baagvaani — workspace rules for OpenCode

Loaded automatically when OpenCode starts in this directory, and pulled into each sub-repo via
its `opencode.json` `instructions`. For the full story — history, design systems, open work —
read [`HANDOVER.md`](HANDOVER.md). For measured detail read [`.opencode/context/`](.opencode/context/).

Owner: **Tarun Chauhan** (solo developer). Product: **Baagvaani** (internal/legacy name *Baagicha*,
बागीचा = "orchard") — altitude-aware orchard advice for Himalayan apple growers. Live at
`baagvaani.com` with real users.

## Workspace map — four independent git repos, no root dev scripts

| Directory | Stack | Role | Read first |
|---|---|---|---|
| `baagvaani_web/` | Laravel 13 · PHP 8.5 · MySQL `baagicha_db` · Bootstrap 5.3 + jQuery 4 · no Tailwind | **The rebuild — where new backend work goes** (started 2026-09-22) | `baagvaani_web/AGENTS.md` |
| `web_baagicha/` | Laravel 12 · PHP 8.2+ · MySQL `baagicha` · Blade + hand-written CSS | **Live legacy backend**: website, admin, mobile API. Source to port from | `web_baagicha/CLAUDE.md` (accurate) |
| `baagichaApp/` | React Native 0.85.3 · TypeScript · Zustand + MMKV | Android-first mobile client of `web_baagicha`'s `/api/v1` | `baagichaApp/.opencode/AGENTS.md` |
| `BaagvaaniBrain/` | Python + Markdown (git submodule) | Blog/image content pipeline | `BaagvaaniBrain/CLAUDE.md` |

The root repo only tracks docs (`AGENTS.md`, `HANDOVER.md`, `CLAUDE.md`, `.claude/`, `.opencode/`).
`baagvaani_web/`, `web_baagicha/`, `baagichaApp/` are gitignored here; `BaagvaaniBrain` is a submodule.
**Run every command inside a sub-project.** Commit in the repo the file belongs to.

## Hard rules

1. **Never port a feature from `web_baagicha` into `baagvaani_web` unprompted.** Wait for Tarun to
   name it, then plan it against `baagvaani_web` conventions (not the old app's).
2. **Production data is sacred.** `web_baagicha` is live. Migrations there must be additive. Never
   run `migrate:fresh`, `db:wipe` or seeders against `baagicha` (the live-mirror DB) without asking.
3. **All API logic lives in Laravel.** The React Native app is a pure client — no business logic,
   no schema, no route definitions.
4. **Altitude band** (`below_6000` / `6000_8000` / `above_8000`) is the central filter. It is derived
   from `altitude_meters` in the model's `booted()` hook — **never set it by hand.**
5. **Bilingual columns come in `_en` / `_hi` pairs.** Never add one without the other.
6. **`is_active` ≠ `is_published`.** Active = visibility toggle; published = editorial state. Public
   queries chain `->active()->published()`.
7. Phone is the primary identity (E.164, `+91…`); email optional.
8. **Ask before outward-facing actions** — `git push`, deploys, sending email/SMS, deleting branches,
   rotating credentials. Several pushes are deliberately pending Tarun's go-ahead.
9. **No new dependencies** (composer or npm) without approval.
10. Never write secret values into docs, commits or chat. Point at where they live instead.

## Working preferences (Tarun's, carried over from Claude Code)

- **Batch edits; verify once at the end.** Do not run the test suite after every change — the
  legacy suite takes ~2.5 min. Prefer a single targeted test file when a check is genuinely needed.
- **Always `composer test`, never bare `php artisan test`.** It runs `config:clear` first. With a
  cached `bootstrap/cache/config.php` the suite ignores `phpunit.xml`'s sqlite `:memory:` and runs
  `RefreshDatabase` against the real MySQL database. If tests fail "environmentally", check for
  that cache file before debugging the tests.
- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:` …). Commit only when asked. If on
  the default branch for real feature work, branch first.
- **Format PHP before committing:** `vendor/bin/pint --dirty --format agent` (baagvaani_web) or
  `php artisan pint` (web_baagicha).
- When unsure about a product decision, ask — see `.opencode/context/open-questions.md`. Don't guess.
- Read sibling files and copy their structure before creating a new file.

## Commands

```bash
# baagvaani_web/  (serve on 8123 — port 8000 belongs to web_baagicha)
composer setup | composer dev | composer test
php artisan serve --port=8123          # dev login admin@baagvaani.test / password
npm run build                          # after any SCSS/JS change
vendor/bin/pint --dirty --format agent

# web_baagicha/
composer dev | composer test | php artisan pint
npm run build                          # runs scripts/copy-assets.js — NOT optional

# baagichaApp/   (Node >= 22.11)
npm start | npm run android | npm test | npm run lint | npx tsc --noEmit

# BaagvaaniBrain/social-media-content/baagvaani-brain/
python3 extract-docx.py --list | python3 validate.py <slug> --source "<fragment>"
```

## Traps that have bitten before

- `web_baagicha`: feature code lives in `Modules/<Name>/`, not `app/`. Tailwind's `@source` does
  not reach `Modules/**` (it only catches them via compiled views in `storage/framework/views`, if
  those happen to exist at build time), so **Tailwind utilities in module Blades are unreliable** —
  the real styling is the hand-written `public/css/*.css`. Use page-named CSS files via `@push('styles')`.
- `web_baagicha`: `app/Console/Kernel.php` is dead code (Laravel 12 never loads it) — anything
  scheduled only there (the prediction jobs, `stories:expire`) never runs. Schedules belong in
  `routes/console.php` or a module service provider.
- `web_baagicha` queues: jobs go to `default`, `notifications`, `intelligence`, `weather-fetch`,
  `weather-alerts`, `weather-engine` (plus `disease-pressure`/`spray-windows`, never scheduled). The
  recorded production cron drains only `default,notifications` — see known-issues #12 before
  touching queue config. A worker must list every queue: `--queue=default,notifications,intelligence,weather-fetch,weather-alerts,weather-engine`.
- `baagvaani_web`: CSP is nonce-based — inline scripts need `<script type="module" @cspNonce>`, no
  `onclick=`; bind behaviour in `resources/js/admin.js` via `data-*` hooks. Strict mode forbids lazy
  loading — eager-load relations.
- `baagvaani_web`: `super-admin` passes every gate via `Gate::before`, so invariants go in
  `AccountSafeguards`, never in policies.
- `baagichaApp/.env` is tracked in git and holds a real Facebook client token — never add more
  secrets to it.
- "Baagicha" in code and "Baagvaani" in user-facing copy are the same product.

## Documentation reliability

Trust: this file, `HANDOVER.md`, `.opencode/context/*`, `web_baagicha/CLAUDE.md`,
`baagvaani_web/CLAUDE.md` + `AGENTS.md`, `BaagvaaniBrain/CLAUDE.md`, `baagichaApp/.opencode/AGENTS.md`
and `CLAUDE.md` (both corrected 2026-10-04).

Do not trust: `web_baagicha/DOCS/backend-status.md` and `DOCS/progress.md` (pre-`Modules/`, March 2026),
`.opencode/anchored-summaries/*` (historical session logs), `BaagvaaniBrain/.opencode/README.md` (stub).
`.claude/context/` is the same content as `.opencode/context/`, kept for Claude Code.
