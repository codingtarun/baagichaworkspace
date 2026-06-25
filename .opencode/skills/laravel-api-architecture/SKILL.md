---
name: laravel-api-architecture
description: Laravel API architecture rules — versioning, auth (Sanctum vs session), response format, and the ground rule that all APIs live in Laravel. Use when building or maintaining API endpoints in web_baagicha/.
---

# Baagicha — Laravel API Architecture

> **Ground Rule:** All APIs live in Laravel. React Native is the pure frontend client.

## Principle

The `web_baagicha/` Laravel application is the **sole backend** for the entire Baagicha ecosystem. It serves:

1. **Web PWA** — Blade views + web routes for browser users
2. **Mobile API** — JSON API endpoints consumed by the React Native app

## API Organization

Mobile endpoints must live under a versioned API namespace:

```
/api/v1/...
```

Example:
- `GET /api/v1/weather/forecast`
- `POST /api/v1/actions/like`
- `GET /api/v1/notifications/recent`

## Authentication

- Web PWA: Laravel session auth (web guard)
- Mobile API: Laravel Sanctum token auth (API guard)

## Response Format

All mobile API responses must be JSON:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

## Rules

1. Never put API logic in the React Native codebase.
2. Never duplicate backend business logic in the frontend.
3. React Native calls Laravel. Laravel talks to the database. Period.
