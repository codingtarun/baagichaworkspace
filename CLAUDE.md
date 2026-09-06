# Baagvaani — Workspace Map

Three independent git repos in one directory. There are **no root-level dev scripts**;
all commands run inside a sub-project.

| Directory | Stack | Role | Own instructions |
|---|---|---|---|
| `web_baagicha/` | Laravel 12 · PHP 8.2+ · MySQL · Blade | **The whole backend** — web site, admin panel, and the mobile API | `web_baagicha/CLAUDE.md` |
| `baagichaApp/` | React Native 0.85.3 · TypeScript | Mobile client (Android-first) | `baagichaApp/.opencode/AGENTS.md` ⚠️ stale — see below |
| `BaagvaaniBrain/` | Python scripts + Markdown | Content & marketing pipeline (blogs, images) | `BaagvaaniBrain/CLAUDE.md` |

**Ground rule:** all API logic lives in Laravel. The React Native app is a pure client —
no business logic, no schema, no route definitions.

## Read before working

| File | When |
|---|---|
| [`.claude/context/product.md`](.claude/context/product.md) | who this is for, the domain rules that drive everything |
| [`.claude/context/architecture.md`](.claude/context/architecture.md) | how the three repos fit together, module layout, API contract |
| [`.claude/context/state-of-the-code.md`](.claude/context/state-of-the-code.md) | measured audit — sizes, test results, what is real vs. aspirational |
| [`.claude/context/known-issues.md`](.claude/context/known-issues.md) | confirmed defects with evidence, ranked |
| [`.claude/context/modules.md`](.claude/context/modules.md) | Blog / VarietyStrain / Disease — measured module analysis, data coverage, gaps |
| [`.claude/context/environments.md`](.claude/context/environments.md) | local setup, database, deployment, credentials map |
| [`.claude/context/open-questions.md`](.claude/context/open-questions.md) | decisions only Tarun can make — ask before assuming |

`web_baagicha/CLAUDE.md` is accurate and detailed; trust it for Laravel work.

## Documentation that is STALE — do not trust

- `baagichaApp/.opencode/AGENTS.md` — says React Context + AsyncStorage + 5 named tabs.
  Reality: **Zustand + MMKV**, tabs are Home / Spray / Shop / Discover / MyOrchard.
  Also names a `web_baagicha` path that no longer exists.
- `web_baagicha/DOCS/backend-status.md`, `DOCS/progress.md` — audited 2026-03-13, before the
  move to `Modules/`. Controller/path references are wrong.
- `web_baagicha/.opencode/skills/*` — conventions still broadly right, paths wrong.
- `.opencode/skills/cross-project-context/SKILL.md` — its "hero sections use Tailwind
  utilities" standard does not match how the site is actually styled (see known-issues #3).

## Conventions that hold everywhere

- **Altitude band** (`below_6000` / `6000_8000` / `above_8000`) is the central filter. Auto-computed
  in model `booted()` hooks — never set it by hand.
- **Bilingual columns come in `_en` / `_hi` pairs.** Never add one without the other.
- **`is_active` ≠ `is_published`.** Active = visibility toggle; published = editorial state.
  Public queries chain `->active()->published()`.
- Phone is the primary auth identifier; email is optional.
- Conventional Commits. Run `php artisan pint` before committing PHP.

## Workflow preferences

- Batch edits; verify once at the end rather than running the suite after every change.
- `composer test` (which does `config:clear` first) — without the clear, cached config
  points the suite at the live MySQL database instead of sqlite `:memory:`.
