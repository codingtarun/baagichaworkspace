# Baagicha — API Reference

> **Source of truth:** `web_baagicha/` (Laravel backend)
> All API endpoints are implemented in the Laravel project and consumed by the React Native mobile app.
>
> **Architecture rule:** APIs live in Laravel. React Native is the pure frontend client.
> **Updated:** 2026-06-06 — added prediction engine APIs, orchard blocks, spray logs, Sanctum auth

---

## Base URL

```
https://api.baagicha.app/api/v1
```

All requests must include:
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <sanctum_token>
```

> **Mobile Auth:** Laravel Sanctum token-based auth. Token stored in MMKV on device.  
> **Web Auth:** Session-based (CSRF token) — not used by mobile.

---

## 1. Authentication (Mobile — Sanctum)

### Login
```
POST /auth/login
```
**Body:**
```json
{
  "phone": "9876543210",
  "password": "password"
}
```
**Response:**
```json
{
  "token": "1|abc123...",
  "user": { "id": 1, "name": "Ramesh Negi", "phone": "9876543210" }
}
```

### Register
```
POST /auth/register
```
**Body:**
```json
{
  "name": "Ramesh Negi",
  "phone": "9876543210",
  "password": "password",
  "password_confirmation": "password",
  "location": "Shimla, HP"
}
```

### Logout
```
POST /auth/logout
```
**Headers:** `Authorization: Bearer <token>`

### Get User
```
GET /auth/user
```

---

## 2. Actions

### Like / Unlike
```
POST /actions/like
```
**Body:**
```json
{
  "type": "Variety | Rootstock | BlogPost | Chemical",
  "id": "123"
}
```
**Response:**
```json
{
  "success": true,
  "count": 145,
  "liked": true
}
```

### Save / Bookmark
```
POST /actions/save
```
**Body:**
```json
{
  "type": "Variety | Rootstock | BlogPost | Chemical",
  "id": "123"
}
```

### Report / Seen Here
```
POST /actions/like
```
**Body:**
```json
{
  "type": "Disease",
  "id": "123",
  "sub": "report"
}
```

### Mark Task Done
```
POST /actions/task-done
```
**Body:**
```json
{
  "task_key": "spray_0"
}
```

---

## 3. Weather

### Select Weather Source
```
POST /weather/select-source
```
**Body (Orchard):**
```json
{
  "source": "orchard",
  "orchard_id": 5
}
```
**Body (Device GPS):**
```json
{
  "source": "device"
}
```

### Get Forecast
```
GET /weather/forecast
```
**Response:** Array of `ForecastDay` objects.

---

## 4. Notifications

### Get Recent Notifications
```
GET /notifications/recent
```

### Get Unread Count
```
GET /notifications/unread-count
```

---

## 5. Predictions (Disease & Pest)

> Backend complete. See `../Laravel/PREDICTION_ENGINE.md` for full architecture.

### Get All Predictions for Orchard
```
GET /orchard/{id}/predictions
```
**Query params:** `date` (optional, ISO)
**Response:** `PredictionsResponse` (disease + pest + warnings)

### Get Disease Prediction
```
GET /orchard/{id}/predictions/disease/{diseaseId}
```

### Get Pest Prediction
```
GET /orchard/{id}/predictions/pest/{pestModelId}
```

### Get Spray Window
```
GET /orchard/{id}/spray-window
```
**Response:** `{ windows: SprayWindow[], best_window: SprayWindow | null }`

### Get Detailed Forecast
```
GET /orchard/{id}/forecast/detailed
```
**Response:** Hourly data for 48h (temp, rain, humidity, wind)

### Submit Prediction Feedback
```
POST /predictions/{logId}/feedback
```
**Body:**
```json
{
  "was_correct": true,
  "notes": "Sprayed but scab still appeared on lower branches"
}
```

---

## 6. Orchard Blocks

### List Blocks
```
GET /orchards/{id}/blocks
```

### Create Block
```
POST /orchards/{id}/blocks
```
**Body:** `Partial<OrchardBlock>`

### Update Block
```
PUT /orchards/{id}/blocks/{blockId}
```

### Delete Block
```
DELETE /orchards/{id}/blocks/{blockId}
```

### Get Block Predictions
```
GET /orchard/{id}/blocks/{blockId}/predictions
```

---

## 7. Spray Logs

### List Spray Logs
```
GET /orchard/{id}/spray-logs
```
**Query params:** `from`, `to` (ISO dates)

### Create Spray Log
```
POST /orchard/{id}/spray-logs
```
**Body:**
```json
{
  "spray_date": "2026-05-20",
  "spray_time": "08:30",
  "chemical_name": "Copper Oxychloride",
  "quantity_used": 300,
  "unit": "g",
  "water_used_liters": 200,
  "area_covered_kanal": 2.5,
  "weather_condition": "sunny",
  "notes": "Good coverage on lower branches"
}
```

---

## 8. Pages / Routes

| Route | Method | Description |
|-------|--------|-------------|
| `GET /` | — | Home page |
| `GET /spray-schedule` | — | Spray schedule |
| `GET /disease` | — | Disease library |
| `GET /diseases/{slug}` | — | Disease detail |
| `GET /chemicals` | — | Chemical index |
| `GET /chemicals/{slug}` | — | Chemical detail |
| `GET /chemicals/{slug}/{brand}` | — | Brand detail |
| `GET /variety` | — | Variety guide |
| `GET /rootstock` | — | Rootstock guide |
| `GET /blog` | — | Blog home |
| `GET /weather/forecast` | — | Weather forecast |
| `GET /orchards` | — | My orchards |
| `GET /disease-reporter` | — | Disease reporter |
| `GET /profile` | — | Profile dashboard |
| `GET /notifications` | — | Notifications |
| `GET /saved` | — | Saved items |

---

## 9. Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| `200` | Success | — |
| `401` | Unauthorized | Show "Please login" toast, redirect to login |
| `422` | Validation Error | Show field errors |
| `500` | Server Error | Show generic error toast |

---

## 10. Toast Notification Types

Used for in-app feedback (not API endpoints):

| Type | Icon | Use Case |
|------|------|----------|
| `success` | `fas fa-check` | Action completed |
| `saved` | `fas fa-bookmark` | Item saved |
| `liked` | `fas fa-heart` | Item liked |
| `report` | `fas fa-flag` | Report submitted |
| `done` | `fas fa-circle-check` | Task marked done |
| `pinned` | `fas fa-thumbtack` | Task pinned |
| `info` | `fas fa-circle-info` | General info |
| `warn` | `fas fa-triangle-exclamation` | Warning |
| `error` | `fas fa-xmark` | Error occurred |

---

*All mobile endpoints use `Bearer` token auth via Laravel Sanctum. The token is stored in MMKV on the device and refreshed as needed.*
