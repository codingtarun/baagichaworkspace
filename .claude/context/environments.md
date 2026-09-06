# Environments, setup and operations

## Local machine

Verified 2026-09-06: PHP **8.5.4** CLI, Laravel **12.58.0**, MySQL local, Node ≥ 22.11 required
by the RN app. `composer.json` requires `php: ^8.2`, so 8.5 is ahead of what the project declares
— worth knowing if something behaves oddly.

## Commands — always run inside a sub-project

### `web_baagicha/`

```bash
composer setup      # install + key:generate + migrate + npm install + npm run build
composer dev        # server + queue:listen + pail + vite, concurrently
composer test       # config:clear + php artisan test        ← use this, not bare `artisan test`
php artisan pint    # format PHP — run before committing
npm run build       # vite build + scripts/copy-assets.js    ← copy-assets is NOT optional
php artisan migrate:fresh --seed
```

**`composer test` does `config:clear` first for a reason.** With cached config the suite reads
the cached MySQL connection instead of the sqlite `:memory:` that `phpunit.xml` forces, and runs
against the live development database.

Targeted runs:

```bash
php artisan test --filter=test_show_returns_404
php artisan test Modules/Weather/tests/Unit/WeatherEngineTest.php
php artisan test --testsuite=Unit          # or Feature
```

`phpunit.xml` covers both `tests/{Unit,Feature}` and `Modules/*/tests/{Unit,Feature}`. A full run
takes ~145 s.

Modules:

```bash
php artisan module:list
php artisan module:make-controller Admin/ThingController Fruit
php artisan module:enable Fruit      # writes modules_statuses.json
```

### `baagichaApp/`

```bash
npm start            # Metro (devtools suppressed by default)
npm run android      # build & run Android
npm test             # Jest — currently one default test
npm run lint         # ESLint
npx tsc --noEmit     # typecheck — currently 4 errors
```

### `BaagvaaniBrain/`

No build, no tests, no server. The pipeline:

```bash
cd social-media-content/baagvaani-brain
python3 extract-docx.py --list                  # what still needs processing
python3 extract-docx.py "fragment" --write      # verbatim .docx → ../blogs/<slug>/english.md
python3 validate.py <slug> --source "fragment"  # grade output against every rule
```

Needs `python3 -m pip install --user python-docx Pillow`.

## Local database

`baagicha` on `127.0.0.1:3306`, user `root`. 138 tables, all 179 migrations applied.

Content as measured 2026-09-06:

| Table | Rows |
|---|---|
| `variety_strains` | 211 |
| `rootstocks` | 123 |
| `users` | 113 |
| `chemicals` | 50 |
| `diseases` | 46 |
| `orders` | 42 |
| `user_orchards` | 207 |
| `products` | 21 |
| `blog_posts` | 12 (all published) |
| `fruits` | 9 |
| `spray_schedule_templates` | 1 |
| `notifications` | 0 |

Every `users` and `orders` row has `created_at = 2026-08-14` — **seeded, not real traffic.**

`weather_data` and `community_posts` are not real table names; check `SHOW TABLES` before
writing raw SQL.

## Deployment

Shared hosting (Hostinger), `baagvaani.com`, path
`/home/u896019069/domains/baagvaani.com/web_baagicha`. That path is hardcoded into
`web_baagicha/.env` as `SITEMAP_PATH`.

There is **no deploy script, no CI, no pipeline** anywhere in the workspace. Deployment appears
to be manual.

### Queue

No long-running daemon — a per-minute cron runs `queue:work`. From `cronjobs/crons-bacup.md`:

```
* * * * * /usr/bin/php .../artisan queue:work --queue=default,notifications --timeout=60 --tries=3 \
    >> .../storage/logs/queue-cron.log 2>&1
```

**The `--queue=default,notifications` form is the correct one.** The file also records an older
line without it; with that one, notification jobs never drain.

### Scheduler

`routes/console.php` — weather refresh /15min, sitemap 03:00, weather alerts 06:00, spray
reminders 08:00, activity-log prune 03:30, weather recommendations 06:00 & 18:00, forecast
archive cleanup 02:00. Intelligence jobs are scheduled separately inside
`IntelligenceServiceProvider`.

## Third-party services in play

| Service | Purpose | Configured |
|---|---|---|
| OpenWeatherMap | primary weather | key present |
| IMD (India Met Dept) | warnings, rainfall — JWT auth | key + credentials present, `IMD_ENABLED=true` |
| MSG91 | SMS / OTP | key present, but `SMS_DRIVER=mock` locally |
| Twilio | SMS fallback | **empty SID / phone number** |
| Google OAuth | social login | web key present; **mobile key is a placeholder** |
| Facebook Login | social login | web key present; **mobile app ID is a placeholder** |
| Razorpay | payments | mobile falls back to a **test key** `rzp_test_…` |
| Firebase (kreait + RN messaging) | push notifications | see `baagichaApp/FIREBASE_SETUP.md` |
| Gmail SMTP | transactional mail from `baagvaani@gmail.com` | present |
| AWS S3 | — | `AWS_BUCKET` empty; `FILESYSTEM_DISK=local` |

Locally `CACHE_STORE`, `QUEUE_CONNECTION` and `SESSION_DRIVER` are all `database`; Redis is
configured but unused.

## Credentials hygiene

- `web_baagicha/.env` — **not tracked.** Correct.
- `baagichaApp/.env` — **tracked in git.** Contains a real `FACEBOOK_CLIENT_TOKEN` plus
  placeholders. Should be rotated and untracked.
- `.claude/settings.local.json` at the workspace root contains the local MySQL root password
  inside pre-approved Bash permission entries. Harmless locally; confirm it is not reused in
  production.
