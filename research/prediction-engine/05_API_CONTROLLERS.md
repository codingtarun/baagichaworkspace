# 05 — API Routes & Controllers

> **Copy routes to `routes/api.php` and controllers to `app/Http/Controllers/Api/`**

---

## API Routes

**File:** Add to `routes/api.php`

```php
<?php

use App\Http\Controllers\Api\OrchardBlockController;
use App\Http\Controllers\Api\PredictionController;
use App\Http\Controllers\Api\SprayLogController;
use Illuminate\Support\Facades\Route;

// ─── PREDICTION & ALERTS ──────────────────────────────────────
Route::middleware(['auth:sanctum'])->group(function () {

    // Predictions for an orchard
    Route::get('/orchard/{orchard}/predictions', [PredictionController::class, 'index'])
        ->name('api.predictions.index');

    Route::get('/orchard/{orchard}/predictions/disease/{disease}', [PredictionController::class, 'showDisease'])
        ->name('api.predictions.disease');

    Route::get('/orchard/{orchard}/predictions/pest/{pestModel}', [PredictionController::class, 'showPest'])
        ->name('api.predictions.pest');

    // Spray window
    Route::get('/orchard/{orchard}/spray-window', [PredictionController::class, 'sprayWindow'])
        ->name('api.spray-window');

    // Detailed forecast
    Route::get('/orchard/{orchard}/forecast/detailed', [PredictionController::class, 'detailedForecast'])
        ->name('api.forecast.detailed');

    // Farmer feedback on predictions
    Route::post('/predictions/{log}/feedback', [PredictionController::class, 'feedback'])
        ->name('api.predictions.feedback');

    // ─── ORCHARD BLOCKS ───────────────────────────────────────
    Route::apiResource('orchards.blocks', OrchardBlockController::class)
        ->parameters(['orchards' => 'orchard', 'blocks' => 'block'])
        ->names('api.orchard-blocks');

    // Block-level predictions
    Route::get('/orchard/{orchard}/blocks/{block}/predictions', [PredictionController::class, 'blockPredictions'])
        ->name('api.blocks.predictions');

    // ─── SPRAY LOGS ───────────────────────────────────────────
    Route::get('/orchard/{orchard}/spray-logs', [SprayLogController::class, 'index'])
        ->name('api.spray-logs.index');

    Route::post('/orchard/{orchard}/spray-logs', [SprayLogController::class, 'store'])
        ->name('api.spray-logs.store');

    Route::get('/spray-logs/{log}', [SprayLogController::class, 'show'])
        ->name('api.spray-logs.show');
});
```

---

## `PredictionController.php`

**File:** `app/Http/Controllers/Api/PredictionController.php`

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Disease;
use App\Models\DiseasePressureLog;
use App\Models\OrchardBlock;
use App\Models\PestModel;
use App\Models\PestTracker;
use App\Models\UserOrchard;
use App\Services\Prediction\DiseasePressureService;
use App\Services\Prediction\LeafWetnessEstimator;
use App\Services\Prediction\SprayWindowService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class PredictionController extends Controller
{
    public function __construct(
        private DiseasePressureService $diseaseService,
        private SprayWindowService $sprayService,
        private LeafWetnessEstimator $wetnessEstimator,
    ) {}

    /**
     * Get all predictions for an orchard.
     */
    public function index(Request $request, UserOrchard $orchard): JsonResponse
    {
        $this->authorize('view', $orchard);

        $date = $request->date('date', now());

        // Check cached predictions first
        $cached = DiseasePressureLog::with('disease')
            ->forOrchard($orchard->id)
            ->forDate($date->toDateString())
            ->get();

        if ($cached->isNotEmpty()) {
            return $this->formatPredictions($cached, $orchard);
        }

        // Compute on-demand (or queue if slow)
        $results = $this->diseaseService->computeForOrchard($orchard, $date);

        return response()->json([
            'orchard_id' => $orchard->id,
            'date' => $date->toDateString(),
            'generated_at' => now()->toIso8601String(),
            'predictions' => array_map(fn($r) => $this->mapPrediction($r), $results),
        ]);
    }

    /**
     * Get prediction for a specific disease.
     */
    public function showDisease(UserOrchard $orchard, Disease $disease): JsonResponse
    {
        $this->authorize('view', $orchard);

        $weather = $orchard->weather()->latest()->first();
        if (!$weather) {
            return response()->json(['error' => 'No weather data'], 404);
        }

        $result = $this->diseaseService->computeForDisease($disease, $weather, $orchard);

        return response()->json([
            'orchard_id' => $orchard->id,
            'disease' => [
                'id' => $disease->id,
                'name' => $disease->name,
                'name_hi' => $disease->name_hi,
            ],
            'prediction' => $this->mapPrediction($result),
        ]);
    }

    /**
     * Get pest tracking data.
     */
    public function showPest(UserOrchard $orchard, PestModel $pestModel): JsonResponse
    {
        $this->authorize('view', $orchard);

        $tracker = PestTracker::where('user_orchard_id', $orchard->id)
            ->where('pest_model_id', $pestModel->id)
            ->where('season_year', now()->year)
            ->first();

        if (!$tracker) {
            return response()->json(['error' => 'No tracker found'], 404);
        }

        $nextEvent = (new \App\Services\Prediction\Models\Pests\DegreeDayModel())
            ->getNextEvent($pestModel, $tracker->cumulative_dd);

        return response()->json([
            'orchard_id' => $orchard->id,
            'pest' => [
                'id' => $pestModel->id,
                'name' => $pestModel->name_en,
                'name_hi' => $pestModel->name_hi,
            ],
            'tracker' => [
                'cumulative_dd' => $tracker->cumulative_dd,
                'biofix_date' => $tracker->biofix_date?->toDateString(),
                'last_event' => $tracker->last_event_triggered,
                'risk_level' => $tracker->risk_level,
            ],
            'next_event' => $nextEvent,
        ]);
    }

    /**
     * Get spray windows for an orchard.
     */
    public function sprayWindow(UserOrchard $orchard): JsonResponse
    {
        $this->authorize('view', $orchard);

        $hourly = $this->wetnessEstimator->fetchHourlyForecast($orchard);
        $windows = $this->sprayService->evaluateWindows($hourly);

        return response()->json([
            'orchard_id' => $orchard->id,
            'generated_at' => now()->toIso8601String(),
            'windows' => $windows,
            'best_window' => $windows[0] ?? null,
        ]);
    }

    /**
     * Get detailed hourly forecast.
     */
    public function detailedForecast(UserOrchard $orchard): JsonResponse
    {
        $this->authorize('view', $orchard);

        $hourly = $this->wetnessEstimator->fetchHourlyForecast($orchard);

        return response()->json([
            'orchard_id' => $orchard->id,
            'generated_at' => now()->toIso8601String(),
            'hourly' => $hourly,
            'summary' => [
                'wetness_hours' => (new \App\Services\Prediction\LeafWetnessEstimator())->estimateWetnessHours(
                    $orchard->weather()->latest()->first() ?? new \App\Models\Weather(['hourly_forecast_48h' => $hourly])
                ),
            ],
        ]);
    }

    /**
     * Get predictions for a specific block.
     */
    public function blockPredictions(UserOrchard $orchard, OrchardBlock $block): JsonResponse
    {
        $this->authorize('view', $orchard);

        if ($block->user_orchard_id !== $orchard->id) {
            return response()->json(['error' => 'Block does not belong to orchard'], 403);
        }

        $weather = $orchard->weather()->latest()->first();
        if (!$weather) {
            return response()->json(['error' => 'No weather data'], 404);
        }

        $diseases = \App\Models\Disease::withPredictionModels()->get();
        $predictions = [];

        foreach ($diseases as $disease) {
            $predictions[] = $this->diseaseService->computeForDisease($disease, $weather, $orchard, $block);
        }

        return response()->json([
            'orchard_id' => $orchard->id,
            'block_id' => $block->id,
            'block_name' => $block->name,
            'predictions' => array_map(fn($r) => $this->mapPrediction($r), $predictions),
        ]);
    }

    /**
     * Submit farmer feedback on a prediction.
     */
    public function feedback(Request $request, DiseasePressureLog $log): JsonResponse
    {
        $this->authorize('update', $log->userOrchard);

        $validated = $request->validate([
            'was_correct' => 'required|boolean',
            'notes' => 'nullable|string|max:500',
        ]);

        $log->update([
            'is_confirmed' => $validated['was_correct'],
            'farmer_feedback' => $validated['notes'],
        ]);

        return response()->json([
            'message' => 'Feedback recorded. Thank you!',
            'message_hi' => 'प्रतिक्रिया दर्ज की गई। धन्यवाद!',
            'log_id' => $log->id,
        ]);
    }

    // ─── Private Helpers ──────────────────────────────────────

    private function formatPredictions($cached, UserOrchard $orchard): JsonResponse
    {
        $predictions = $cached->map(function ($log) {
            return [
                'type' => 'disease',
                'name' => $log->disease->name,
                'name_hi' => $log->disease->name_hi,
                'risk_level' => $log->risk_level,
                'risk_score' => $log->risk_score,
                'model_used' => $log->prediction_type,
                'factors' => $log->trigger_factors,
                'recommended_action' => $log->spray_recommendation,
                'recommended_action_hi' => $log->spray_recommendation_hi,
            ];
        });

        return response()->json([
            'orchard_id' => $orchard->id,
            'date' => now()->toDateString(),
            'generated_at' => $cached->first()?->created_at?->toIso8601String(),
            'predictions' => $predictions,
            'cached' => true,
        ]);
    }

    private function mapPrediction(array $result): array
    {
        return [
            'type' => 'disease',
            'id' => $result['disease_id'] ?? null,
            'name' => $result['disease_name'] ?? null,
            'name_hi' => $result['disease_name_hi'] ?? null,
            'risk_level' => $result['level'],
            'risk_score' => $result['score'],
            'model_used' => $result['model'],
            'prediction_window' => 'Next 48 hours',
            'factors' => $result['factors'] ?? [],
            'infection_periods' => $result['infection_periods'] ?? [],
            'spray_window' => $result['spray_window'] ?? null,
            'recommended_action' => $result['recommendation']['action_en'] ?? null,
            'recommended_action_hi' => $result['recommendation']['action_hi'] ?? null,
            'action_needed' => $result['recommendation']['action_needed'] ?? false,
        ];
    }
}
```

---

## `OrchardBlockController.php`

**File:** `app/Http/Controllers/Api/OrchardBlockController.php`

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\OrchardBlock;
use App\Models\UserOrchard;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class OrchardBlockController extends Controller
{
    public function index(UserOrchard $orchard): JsonResponse
    {
        $this->authorize('view', $orchard);

        $blocks = $orchard->orchardBlocks()->with(['variety', 'rootstock'])->get();

        return response()->json([
            'orchard_id' => $orchard->id,
            'blocks' => $blocks,
        ]);
    }

    public function store(Request $request, UserOrchard $orchard): JsonResponse
    {
        $this->authorize('update', $orchard);

        $validated = $request->validate([
            'name' => 'required|string|max:100',
            'variety_id' => 'nullable|exists:varieties,id',
            'rootstock_id' => 'nullable|exists:rootstocks,id',
            'area_kanal' => 'nullable|numeric|min:0',
            'plant_count' => 'nullable|integer|min:0',
            'tree_age_years' => 'nullable|integer|min:0|max:100',
            'spacing_meters' => 'nullable|string|max:20',
            'soil_type' => ['nullable', Rule::in(['loam', 'clay', 'sandy', 'silty', 'peaty'])],
            'soil_ph' => 'nullable|numeric|between:0,14',
            'irrigation_type' => ['nullable', Rule::in(['drip', 'sprinkler', 'flood', 'rainfed'])],
            'aspect' => ['nullable', Rule::in(['north', 'south', 'east', 'west', 'flat'])],
            'slope_percent' => 'nullable|integer|min:0|max:100',
            'is_sunny_exposure' => 'nullable|boolean',
            'wind_exposure' => ['nullable', Rule::in(['sheltered', 'moderate', 'exposed'])],
            'frost_pocket_risk' => ['nullable', Rule::in(['low', 'medium', 'high'])],
        ]);

        $block = $orchard->orchardBlocks()->create(array_merge($validated, [
            'user_id' => $request->user()->id,
        ]));

        return response()->json([
            'message' => 'Block created successfully',
            'block' => $block->load(['variety', 'rootstock']),
        ], 201);
    }

    public function show(UserOrchard $orchard, OrchardBlock $block): JsonResponse
    {
        $this->authorize('view', $orchard);

        if ($block->user_orchard_id !== $orchard->id) {
            return response()->json(['error' => 'Block not found'], 404);
        }

        return response()->json([
            'block' => $block->load(['variety', 'rootstock']),
        ]);
    }

    public function update(Request $request, UserOrchard $orchard, OrchardBlock $block): JsonResponse
    {
        $this->authorize('update', $orchard);

        if ($block->user_orchard_id !== $orchard->id) {
            return response()->json(['error' => 'Block not found'], 404);
        }

        $validated = $request->validate([
            'name' => 'sometimes|string|max:100',
            'variety_id' => 'nullable|exists:varieties,id',
            'rootstock_id' => 'nullable|exists:rootstocks,id',
            'area_kanal' => 'nullable|numeric|min:0',
            'plant_count' => 'nullable|integer|min:0',
            'tree_age_years' => 'nullable|integer|min:0|max:100',
            'spacing_meters' => 'nullable|string|max:20',
            'soil_type' => ['nullable', Rule::in(['loam', 'clay', 'sandy', 'silty', 'peaty'])],
            'soil_ph' => 'nullable|numeric|between:0,14',
            'irrigation_type' => ['nullable', Rule::in(['drip', 'sprinkler', 'flood', 'rainfed'])],
            'aspect' => ['nullable', Rule::in(['north', 'south', 'east', 'west', 'flat'])],
            'slope_percent' => 'nullable|integer|min:0|max:100',
            'is_sunny_exposure' => 'nullable|boolean',
            'wind_exposure' => ['nullable', Rule::in(['sheltered', 'moderate', 'exposed'])],
            'frost_pocket_risk' => ['nullable', Rule::in(['low', 'medium', 'high'])],
        ]);

        $block->update($validated);

        return response()->json([
            'message' => 'Block updated successfully',
            'block' => $block->fresh()->load(['variety', 'rootstock']),
        ]);
    }

    public function destroy(UserOrchard $orchard, OrchardBlock $block): JsonResponse
    {
        $this->authorize('update', $orchard);

        if ($block->user_orchard_id !== $orchard->id) {
            return response()->json(['error' => 'Block not found'], 404);
        }

        $block->delete();

        return response()->json([
            'message' => 'Block deleted successfully',
        ]);
    }
}
```

---

## `SprayLogController.php`

**File:** `app/Http/Controllers/Api/SprayLogController.php`

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\SprayLog;
use App\Models\UserOrchard;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class SprayLogController extends Controller
{
    public function index(Request $request, UserOrchard $orchard): JsonResponse
    {
        $this->authorize('view', $orchard);

        $logs = $orchard->sprayLogs()
            ->with(['disease', 'orchardBlock'])
            ->when($request->date('from'), fn($q, $d) => $q->whereDate('spray_date', '>=', $d))
            ->when($request->date('to'), fn($q, $d) => $q->whereDate('spray_date', '<=', $d))
            ->orderByDesc('spray_date')
            ->paginate($request->integer('per_page', 20));

        return response()->json($logs);
    }

    public function store(Request $request, UserOrchard $orchard): JsonResponse
    {
        $this->authorize('update', $orchard);

        $validated = $request->validate([
            'orchard_block_id' => 'nullable|exists:orchard_blocks,id',
            'disease_id' => 'nullable|exists:diseases,id',
            'spray_schedule_stage_id' => 'nullable|exists:spray_schedule_stages,id',
            'spray_date' => 'required|date',
            'spray_time' => 'nullable|date_format:H:i',
            'chemical_name' => 'required|string|max:200',
            'quantity_used' => 'nullable|numeric|min:0',
            'unit' => ['nullable', Rule::in(['g', 'ml', 'kg', 'L'])],
            'water_used_liters' => 'nullable|numeric|min:0',
            'area_covered_kanal' => 'nullable|numeric|min:0',
            'weather_condition' => ['nullable', Rule::in(['sunny', 'cloudy', 'windy', 'rainy'])],
            'notes' => 'nullable|string|max:1000',
            'photos' => 'nullable|array',
            'photos.*' => 'string', // URLs or base64
        ]);

        $log = $orchard->sprayLogs()->create(array_merge($validated, [
            'user_id' => $request->user()->id,
            'reward_points' => 20, // Base points for logging a spray
        ]));

        // TODO: Trigger reward points update on user

        return response()->json([
            'message' => 'Spray logged successfully',
            'message_hi' => 'स्प्रे दर्ज हो गया',
            'log' => $log->load(['disease', 'orchardBlock']),
            'points_earned' => 20,
        ], 201);
    }

    public function show(SprayLog $log): JsonResponse
    {
        $this->authorize('view', $log->userOrchard);

        return response()->json([
            'log' => $log->load(['disease', 'orchardBlock']),
        ]);
    }
}
```

---

## Request/Response Examples

### GET `/api/orchard/{id}/predictions`

**Response:**
```json
{
  "orchard_id": 42,
  "date": "2026-05-21",
  "generated_at": "2026-05-21T05:30:00+05:30",
  "predictions": [
    {
      "type": "disease",
      "id": 7,
      "name": "Apple Scab",
      "name_hi": "सेब की छाई",
      "risk_level": "high",
      "risk_score": 75,
      "model_used": "mills",
      "prediction_window": "Next 48 hours",
      "factors": [
        {"key": "mills_infection_period", "label": "Wetness 18h at 16°C (needs 15h)", "label_hi": "नमी 18 घंटे 16°C पर (जरूरत 15 घंटे)"}
      ],
      "infection_periods": [
        {"start": "2026-05-21T14:00:00+05:30", "hours": 18, "avg_temp": 16.2, "severity": "moderate"}
      ],
      "spray_window": {
        "start": "2026-05-21T06:00:00+05:30",
        "hours": 6,
        "rating": "excellent"
      },
      "recommended_action": "Apple Scab risk is HIGH. Spray Copper Oxychloride 50WP 300g per 200L water x 2 tanks. Best window: Wed, May 21 at 6:00 AM (6h excellent).",
      "recommended_action_hi": "सेब की छाई का जोखिम उच्च है। बुधवार, मई 21 सुबह 6:00 बजे तक कॉपर ऑक्सीक्लोराइड 50WP 300g प्रति 200L पानी x 2 टैंक छिड़कें।",
      "action_needed": true
    }
  ]
}
```

### GET `/api/orchard/{id}/spray-window`

**Response:**
```json
{
  "orchard_id": 42,
  "generated_at": "2026-05-21T05:30:00+05:30",
  "windows": [
    {"start": "2026-05-21T06:00:00+05:30", "hours": 6, "rating": "excellent", "avg_temp": 16, "max_wind": 2.5},
    {"start": "2026-05-22T06:00:00+05:30", "hours": 4, "rating": "good", "avg_temp": 17, "max_wind": 3.1}
  ],
  "best_window": {"start": "2026-05-21T06:00:00+05:30", "hours": 6, "rating": "excellent", "avg_temp": 16, "max_wind": 2.5}
}
```

### POST `/api/predictions/{logId}/feedback`

**Request:**
```json
{
  "was_correct": true,
  "notes": "Sprayed as recommended, no scab appeared"
}
```

**Response:**
```json
{
  "message": "Feedback recorded. Thank you!",
  "message_hi": "प्रतिक्रिया दर्ज की गई। धन्यवाद!",
  "log_id": 1523
}
```

---

*Next: Read `06_NOTIFICATIONS.md` for push notification templates.*
