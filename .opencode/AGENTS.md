# Baagicha Workspace — AGENTS.md

## Workspace structure

Three independent projects in one directory. **Each has its own git repo** — root `.gitignore` excludes `baagichaApp/` and `web_baagicha/`:

| Directory | Stack | Role | Instructions |
|-----------|-------|------|-------------|
| `web_baagicha/` | Laravel 12 + Blade + Tailwind 4 + Bootstrap 5 (admin) | Backend API + Web PWA | `web_baagicha/.opencode/CLAUDE.md`, `web_baagicha/.opencode/skills/` |
| `baagichaApp/` | React Native 0.85 (CLI) | Mobile frontend (iOS & Android) | `baagichaApp/.opencode/AGENTS.md`, `baagichaApp/.opencode/CLAUDE.md`, `baagichaApp/.opencode/KIMI.md` |
| `BaagvaaniBrain/` | — | Content creation & marketing | `BaagvaaniBrain/.opencode/README.md`, `BaagvaaniBrain/.opencode/skills/` |

## What an agent needs to know

- **Work at the sub-project level.** Commands, tests, lint, typecheck — run inside `web_baagicha/` or `baagichaApp/`. There are no root-level dev scripts.
- **Each sub-project has its own instruction file** — read those before making changes.

## Product (cross-cutting)

- **Target:** Himalayan apple farmers (Himachal Pradesh, Uttarakhand, Jammu & Kashmir)
- **Core business rule:** Everything filters by **altitude band** (`below_6000` / `6000_8000` / `above_8000`)
- **Bilingual:** All user-visible content in English + Hindi (`_en` / `_hi` column pairs)
- **Content flags:** Public queries must filter `is_published = true AND is_active = true`
- **Backend auth:** Laravel Breeze (phone-first, session-based) + Spatie roles (`admin`/`manager`/`farmer`)
- **Mobile auth:** Sanctum token-based (Bearer token stored in MMKV)

## Commands (run inside each sub-project)

```bash
# Laravel (web_baagicha/)
composer setup           # install, key:generate, migrate, seed, build
composer dev             # server + queue + pail + vite (concurrent)
composer test            # config:clear + phpunit
php artisan pint         # code formatting

# React Native (baagichaApp/)
npm start                # Metro bundler
npm run android          # Build & run Android
npm test                 # Jest
npm run lint             # ESLint
```

## Useful context

- `web_baagicha/` uses **nwidart/laravel-modules** — domain logic lives in `Modules/` (Auth, Blog, Disease, Fruit, Variety, etc.)
- `baagichaApp/` uses **Zustand** for state management, **MMKV** for local storage, **React Navigation** (bottom tabs + native stack)
- Queue worker must listen on both `default` and `notifications` queues (see cross-project-context skill for cron details)
