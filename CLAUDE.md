# Baagicha — Workspace Map

Baagicha is being built fresh (from 2026-10-07) in **plain PHP** and **React Native**, as a
production app and a learning project at the same time. Tarun writes some of the code himself
to revise concepts; Claude writes the rest. **Who writes a piece is decided per task — ask
before writing code in a new area.** When Tarun writes code, review and explain it; don't
rewrite it.

| Directory | Stack | Role |
|---|---|---|
| `baagicha_php/` | Plain PHP, built level by level from the basics · MySQL `baagicha_db` | **The new backend**: web site, admin and mobile API |
| `baagicha_mobile/` | Expo SDK 57 · React Native · TypeScript · Expo Router | **The new mobile app**, a pure API client (own repo; run guide: `baagicha_mobile/RUN-ON-ANDROID.md`) |
| `old_apps/web_baagicha/` | Laravel 12 | Old app (live DB `baagicha`). **Reference only**, don't build on it |
| `old_apps/baagichaApp/` | React Native 0.85 | Old mobile app. **Reference only** |
| `BaagvaaniBrain/` | Python + Markdown | Content and marketing pipeline (git submodule) |

**Backend rules live in [`baagicha_php/CLAUDE.md`](baagicha_php/CLAUDE.md)** and the level-by-level plan in
[`baagicha_php/docs/roadmap.md`](baagicha_php/docs/roadmap.md). Tarun is learning PHP as a fresher: he types, Claude guides.

`.claude/context/` describes the **old** Laravel app. Use it to understand the domain and the
old schema, not as a description of the new code.

## Rules

- All business logic lives in PHP. The mobile app has no business logic of its own.
- No framework in `baagicha_php/`. Keep the code simple enough to learn from.
- Database `baagicha_db` uses `utf8mb4_unicode_ci`. The schema is designed table by table
  as features are built; the old schema is a reference, not a template to copy.
- Domain rules from the old app still hold: the altitude band (`below_6000` / `6000_8000` /
  `above_8000`) is computed, never set by hand. Bilingual columns come in `_en` / `_hi`
  pairs. `is_active` is not the same as `is_published`. Phone is the main login identifier.
- Conventional Commits. Batch edits and verify once at the end.
