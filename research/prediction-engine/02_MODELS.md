# 02 — Eloquent Models

> Create these models AFTER running migrations. All relationships follow existing conventions.

---

## `OrchardBlock` Model

**File:** `app/Models/OrchardBlock.php`

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class OrchardBlock extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_orchard_id', 'user_id', 'name', 'variety_id', 'rootstock_id',
        'area_kanal', 'plant_count', 'tree_age_years', 'spacing_meters',
        'soil_type', 'soil_ph', 'irrigation_type', 'aspect', 'slope_percent',
        'is_sunny_exposure', 'wind_exposure', 'frost_pocket_risk',
    ];

    protected $casts = [
        'area_kanal' => 'decimal:2',
        'soil_ph' => 'decimal:1',
        'is_sunny_exposure' => 'boolean',
        'slope_percent' => 'integer',
    ];

    // ─── Relationships ──────────────────────────────────────────

    public function userOrchard(): BelongsTo
    {
        return $this->belongsTo(UserOrchard::class, 'user_orchard_id');
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function variety(): BelongsTo
    {
        return $this->belongsTo(Variety::class);
    }

    public function rootstock(): BelongsTo
    {
        return $this->belongsTo(Rootstock::class);
    }

    public function diseasePressureLogs(): HasMany
    {
        return $this->hasMany(DiseasePressureLog::class, 'orchard_block_id');
    }

    public function pestTrackers(): HasMany
    {
        return $this->hasMany(PestTracker::class, 'orchard_block_id');
    }

    public function sprayLogs(): HasMany
    {
        return $this->hasMany(SprayLog::class, 'orchard_block_id');
    }

    // ─── Scopes ─────────────────────────────────────────────────

    public function scopeForUser($query, int $userId)
    {
        return $query->where('user_id', $userId);
    }

    public function scopeForOrchard($query, int $orchardId)
    {
        return $query->where('user_orchard_id', $orchardId);
    }

    public function scopeActive($query)
    {
        return $query->whereHas('userOrchard', fn ($q) => $q->where('is_active', true));
    }

    // ─── Helpers ────────────────────────────────────────────────

    /**
     * Get microclimate adjustment factors for this block.
     * Used by prediction engine to tweak risk scores.
     */
    public function getMicroclimateAdjustments(): array
    {
        $adjustments = [
            'wetness_duration_multiplier' => 1.0,
            'humidity_offset' => 0,
            'wind_speed_multiplier' => 1.0,
            'frost_threshold_offset' => 0,
        ];

        // Shady / north slope stays wet longer
        if (in_array($this->aspect, ['north', 'east'])) {
            $adjustments['wetness_duration_multiplier'] += 0.10;
        }
        if (!$this->is_sunny_exposure) {
            $adjustments['wetness_duration_multiplier'] += 0.10;
        }

        // Sheltered valley = higher humidity
        if ($this->wind_exposure === 'sheltered') {
            $adjustments['humidity_offset'] += 5;
        }

        // Exposed ridge = more wind
        if ($this->wind_exposure === 'exposed') {
            $adjustments['wind_speed_multiplier'] += 0.20;
        }

        // Frost pocket
        if ($this->frost_pocket_risk === 'high') {
            $adjustments['frost_threshold_offset'] += 2;
        } elseif ($this->frost_pocket_risk === 'medium') {
            $adjustments['frost_threshold_offset'] += 1;
        }

        return $adjustments;
    }
}
```

---

## `PestModel` Model

**File:** `app/Models/PestModel.php`

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class PestModel extends Model
{
    use HasFactory;

    protected $primaryKey = 'id';
    public $incrementing = true;
    protected $keyType = 'int';

    protected $fillable = [
        'name_en', 'name_hi', 'scientific_name', 'type',
        'threshold_temp_c', 'cutoff_temp_c',
        'dd_target_first_event', 'dd_target_second_event', 'dd_target_third_event',
        'event_labels', 'applicable_months', 'applicable_altitude_bands',
        'is_active', 'sort_order',
    ];

    protected $casts = [
        'threshold_temp_c' => 'decimal:1',
        'cutoff_temp_c' => 'decimal:1',
        'dd_target_first_event' => 'integer',
        'dd_target_second_event' => 'integer',
        'dd_target_third_event' => 'integer',
        'event_labels' => 'array',
        'applicable_months' => 'array',
        'applicable_altitude_bands' => 'array',
        'is_active' => 'boolean',
        'sort_order' => 'integer',
    ];

    public function pestTrackers(): HasMany
    {
        return $this->hasMany(PestTracker::class, 'pest_model_id');
    }

    public function scopeActive($query)
    {
        return $query->where('is_active', true)->orderBy('sort_order');
    }

    /**
     * Get regional default biofix date based on altitude band.
     */
    public function getDefaultBiofixDate(int $year, string $altitudeBand): ?string
    {
        $defaults = [
            'Codling Moth' => [
                'below_6000' => "{$year}-05-15",
                '6000_8000'  => "{$year}-05-25",
                'above_8000' => "{$year}-06-05",
            ],
            'San Jose Scale' => [
                'below_6000' => "{$year}-04-20",
                '6000_8000'  => "{$year}-05-01",
                'above_8000' => "{$year}-05-10",
            ],
            'Woolly Apple Aphid' => [
                'below_6000' => "{$year}-04-01",
                '6000_8000'  => "{$year}-04-15",
            ],
        ];

        return $defaults[$this->name_en][$altitudeBand] ?? null;
    }

    /**
     * Check if this pest is applicable for given month and altitude.
     */
    public function isApplicable(int $month, string $altitudeBand): bool
    {
        $months = $this->applicable_months ?? [];
        $bands = $this->applicable_altitude_bands ?? [];

        return in_array($month, $months) && in_array($altitudeBand, $bands);
    }
}
```

---

## `PestTracker` Model

**File:** `app/Models/PestTracker.php`

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PestTracker extends Model
{
    use HasFactory;

    protected $table = 'pest_tracker';

    protected $fillable = [
        'user_orchard_id', 'orchard_block_id', 'pest_model_id',
        'season_year', 'biofix_date', 'biofix_source',
        'cumulative_dd', 'last_event_triggered', 'next_event_at_dd', 'risk_level',
    ];

    protected $casts = [
        'biofix_date' => 'date',
        'cumulative_dd' => 'decimal:1',
        'next_event_at_dd' => 'integer',
    ];

    public function userOrchard(): BelongsTo
    {
        return $this->belongsTo(UserOrchard::class, 'user_orchard_id');
    }

    public function orchardBlock(): BelongsTo
    {
        return $this->belongsTo(OrchardBlock::class, 'orchard_block_id');
    }

    public function pestModel(): BelongsTo
    {
        return $this->belongsTo(PestModel::class, 'pest_model_id');
    }

    public function scopeForSeason($query, int $year)
    {
        return $query->where('season_year', $year);
    }

    public function scopeActive($query)
    {
        return $query->whereHas('pestModel', fn ($q) => $q->where('is_active', true));
    }
}
```

---

## `DiseasePressureLog` Model

**File:** `app/Models/DiseasePressureLog.php`

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class DiseasePressureLog extends Model
{
    use HasFactory;

    protected $table = 'disease_pressure_log';
    public $timestamps = false;

    protected $fillable = [
        'user_orchard_id', 'orchard_block_id', 'disease_id',
        'prediction_date', 'prediction_type', 'risk_score', 'risk_level',
        'trigger_factors', 'weather_snapshot',
        'spray_recommendation', 'spray_recommendation_hi',
        'is_confirmed', 'farmer_feedback',
    ];

    protected $casts = [
        'prediction_date' => 'date',
        'risk_score' => 'integer',
        'trigger_factors' => 'array',
        'weather_snapshot' => 'array',
        'is_confirmed' => 'boolean',
    ];

    public function userOrchard(): BelongsTo
    {
        return $this->belongsTo(UserOrchard::class, 'user_orchard_id');
    }

    public function orchardBlock(): BelongsTo
    {
        return $this->belongsTo(OrchardBlock::class, 'orchard_block_id');
    }

    public function disease(): BelongsTo
    {
        return $this->belongsTo(Disease::class);
    }

    public function scopeForOrchard($query, int $orchardId)
    {
        return $query->where('user_orchard_id', $orchardId);
    }

    public function scopeForDate($query, string $date)
    {
        return $query->where('prediction_date', $date);
    }

    public function scopeHighRisk($query)
    {
        return $query->whereIn('risk_level', ['high', 'critical']);
    }

    public function scopePendingFeedback($query)
    {
        return $query->whereNull('is_confirmed')
            ->where('prediction_date', '<', now()->subDays(10)->toDateString());
    }
}
```

---

## `SprayLog` Model

**File:** `app/Models/SprayLog.php`

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SprayLog extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'user_orchard_id', 'orchard_block_id',
        'disease_id', 'spray_schedule_stage_id',
        'spray_date', 'spray_time', 'chemical_name',
        'quantity_used', 'unit', 'water_used_liters',
        'area_covered_kanal', 'weather_condition', 'notes', 'photos', 'reward_points',
    ];

    protected $casts = [
        'spray_date' => 'date',
        'quantity_used' => 'decimal:2',
        'water_used_liters' => 'decimal:2',
        'area_covered_kanal' => 'decimal:2',
        'photos' => 'array',
        'reward_points' => 'integer',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function userOrchard(): BelongsTo
    {
        return $this->belongsTo(UserOrchard::class, 'user_orchard_id');
    }

    public function orchardBlock(): BelongsTo
    {
        return $this->belongsTo(OrchardBlock::class, 'orchard_block_id');
    }

    public function disease(): BelongsTo
    {
        return $this->belongsTo(Disease::class);
    }
}
```

---

## Extended `Disease` Model (Add these methods)

**File:** Add to existing `app/Models/Disease.php`

```php
    protected $casts = [
        // ... existing casts ...
        'is_mills_applicable' => 'boolean',
        'mills_wetness_hours' => 'array',
        'is_maryblyt_applicable' => 'boolean',
        'maryblyt_dh_threshold' => 'integer',
        'maryblyt_temp_threshold_c' => 'decimal:1',
        'is_dmc_applicable' => 'boolean',
        'dmc_temp_min_c' => 'integer',
        'dmc_temp_max_c' => 'integer',
        'dmc_rh_threshold_pct' => 'integer',
        'dmc_favorable_hours_threshold' => 'integer',
    ];

    public function diseasePressureLogs(): HasMany
    {
        return $this->hasMany(DiseasePressureLog::class, 'disease_id');
    }

    public function sprayLogs(): HasMany
    {
        return $this->hasMany(SprayLog::class, 'disease_id');
    }

    public function scopeWithPredictionModels($query)
    {
        return $query->where(function ($q) {
            $q->where('is_mills_applicable', true)
              ->orWhere('is_maryblyt_applicable', true)
              ->orWhere('is_dmc_applicable', true)
              ->orWhereNotNull('risk_temp_min_c');
        });
    }
```

---

## Extended `UserOrchard` Model (Add these relationships)

**File:** Add to existing `app/Models/UserOrchard.php`

```php
    public function orchardBlocks(): HasMany
    {
        return $this->hasMany(OrchardBlock::class, 'user_orchard_id');
    }

    public function diseasePressureLogs(): HasMany
    {
        return $this->hasMany(DiseasePressureLog::class, 'user_orchard_id');
    }

    public function pestTrackers(): HasMany
    {
        return $this->hasMany(PestTracker::class, 'user_orchard_id');
    }

    public function sprayLogs(): HasMany
    {
        return $this->hasMany(SprayLog::class, 'user_orchard_id');
    }

    public function latestDiseasePressure(): HasOne
    {
        return $this->hasOne(DiseasePressureLog::class, 'user_orchard_id')
            ->latest('prediction_date');
    }

    /**
     * Get altitude band string used throughout the system.
     */
    public function getAltitudeBandAttribute(): string
    {
        $ft = $this->altitude_feet ?? 0;

        return match (true) {
            $ft < 6000 => 'below_6000',
            $ft <= 8000 => '6000_8000',
            default => 'above_8000',
        };
    }
```

---

*Next: Read `03_SERVICES.md` for the core business logic.*
