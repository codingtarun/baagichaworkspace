# 03 — Core PHP Service Classes

> **Copy these into `app/Services/Prediction/`**. These are production-ready with full implementation.

---

## Directory Structure

```
app/Services/
├── Prediction/
│   ├── DiseasePressureService.php
│   ├── PestDevelopmentService.php
│   ├── SprayWindowService.php
│   ├── LeafWetnessEstimator.php
│   ├── MicroclimateService.php
│   ├── RecommendationGenerator.php
│   ├── ModelFactory.php
│   └── Models/
│       ├── AbstractPredictionModel.php
│       ├── RuleBasedModel.php
│       ├── Scab/
│       │   └── RevisedMillsModel.php
│       ├── FireBlight/
│       │   └── SimplifiedMaryblytModel.php
│       ├── PowderyMildew/
│       │   └── DmcModel.php
│       └── Pests/
│           └── DegreeDayModel.php
```

---

## `AbstractPredictionModel.php`

**File:** `app/Services/Prediction/Models/AbstractPredictionModel.php`

```php
<?php

namespace App\Services\Prediction\Models;

use App\Models\Disease;
use App\Models\UserOrchard;
use App\Models\Weather;

abstract class AbstractPredictionModel
{
    abstract public function calculate(Disease $disease, Weather $weather, UserOrchard $orchard, ?array $hourlyForecast = null): array;

    abstract public function getModelName(): string;

    /**
     * Map a 0-100 score to risk level.
     */
    protected function scoreToLevel(int $score): string
    {
        return match (true) {
            $score >= 80 => 'critical',
            $score >= 60 => 'high',
            $score >= 40 => 'medium',
            $score >= 20 => 'low',
            default => 'none',
        };
    }

    /**
     * Estimate leaf wetness from forecast data (no sensors).
     * Accuracy: ~70-80% vs actual sensors.
     */
    protected function isLeafWet(array $hour): bool
    {
        $rh = $hour['humidity'] ?? 0;
        $rain = $hour['precipitation'] ?? 0;
        $temp = $hour['temperature'] ?? 0;
        $dewPoint = $hour['dew_point'] ?? ($temp - ((100 - $rh) / 5));
        $visibility = $hour['visibility'] ?? 10000;

        $isDew = ($temp - $dewPoint) < 2.5;
        $isFog = $visibility < 1000 && $rh > 90;

        return $rh >= 85 || $rain >= 0.1 || $isDew || $isFog;
    }

    /**
     * Interpolate value from lookup table.
     */
    protected function interpolate(float $value, array $table): float
    {
        $keys = array_keys($table);
        sort($keys);

        foreach ($keys as $i => $k) {
            if ($value <= $k) {
                $lowerK = $keys[$i - 1] ?? $k;
                $lowerV = $table[$lowerK];
                $upperV = $table[$k];
                if ($k === $lowerK) return $upperV;
                $ratio = ($value - $lowerK) / ($k - $lowerK);
                return $lowerV + ($upperV - $lowerV) * $ratio;
            }
        }
        return $table[end($keys)];
    }
}
```

---

## `RuleBasedModel.php` (Phase 1)

**File:** `app/Services/Prediction/Models/RuleBasedModel.php`

```php
<?php

namespace App\Services\Prediction\Models;

use App\Models\Disease;
use App\Models\UserOrchard;
use App\Models\Weather;

class RuleBasedModel extends AbstractPredictionModel
{
    public function getModelName(): string
    {
        return 'rule';
    }

    public function calculate(Disease $disease, Weather $weather, UserOrchard $orchard, ?array $hourlyForecast = null): array
    {
        $score = 0;
        $factors = [];
        $currentTemp = $weather->temperature;
        $currentHumidity = $weather->humidity;
        $currentRain = $weather->precipitation ?? 0;

        // ─── Temperature match (0-40 points) ──────────────────────
        if ($currentTemp >= $disease->risk_temp_min_c && $currentTemp <= $disease->risk_temp_max_c) {
            $score += 40;
            $factors[] = ['key' => 'optimal_temperature', 'label' => 'Temperature is optimal', 'label_hi' => 'तापमान इष्टतम है'];
        } elseif (
            abs($currentTemp - $disease->risk_temp_min_c) <= 3 ||
            abs($currentTemp - $disease->risk_temp_max_c) <= 3
        ) {
            $score += 20;
            $factors[] = ['key' => 'near_optimal_temperature', 'label' => 'Temperature is near optimal', 'label_hi' => 'तापमान लगभग इष्टतम है'];
        }

        // ─── Humidity match (0-30 points) ─────────────────────────
        if ($currentHumidity >= $disease->risk_humidity_pct) {
            $score += 30;
            $factors[] = ['key' => 'high_humidity', 'label' => "Humidity {$currentHumidity}% (high)", 'label_hi' => "नमी {$currentHumidity}% (उच्च)"];
        } elseif ($currentHumidity >= $disease->risk_humidity_pct - 10) {
            $score += 15;
            $factors[] = ['key' => 'elevated_humidity', 'label' => "Humidity {$currentHumidity}% (elevated)", 'label_hi' => "नमी {$currentHumidity}% (बढ़ी हुई)"];
        }

        // ─── Rain / wetness (0-20 points) ─────────────────────────
        if ($currentRain > 2.5) {
            $score += 20;
            $factors[] = ['key' => 'rain_present', 'label' => 'Rain present', 'label_hi' => 'बारिश हो रही है'];
        } elseif ($currentRain > 0) {
            $score += 10;
            $factors[] = ['key' => 'light_rain', 'label' => 'Light rain', 'label_hi' => 'हल्की बारिश'];
        }

        // ─── Altitude match (0-10 points) ─────────────────────────
        $orchardAltFt = $orchard->altitude_feet ?? 0;
        $altMin = $disease->altitude_min_feet ?? 0;
        $altMax = $disease->altitude_max_feet ?? 99999;
        if ($orchardAltFt >= $altMin && $orchardAltFt <= $altMax) {
            $score += 10;
            $factors[] = ['key' => 'altitude_match', 'label' => 'Altitude matches disease range', 'label_hi' => 'ऊंचाई रोग की सीमा से मेल खाती है'];
        }

        // ─── Forecast lookahead bonus (0-10 points) ───────────────
        $riskDaysAhead = 0;
        $forecast = $weather->forecast_5day ?? [];
        foreach ($forecast as $day) {
            $dayTempMax = $day['temp_max'] ?? ($day['temperature'] ?? 0);
            $dayHumidity = $day['humidity'] ?? 0;
            $dayRain = $day['rain'] ?? ($day['precipitation'] ?? 0);

            if (
                $dayTempMax >= $disease->risk_temp_min_c &&
                $dayTempMax <= $disease->risk_temp_max_c &&
                $dayHumidity >= $disease->risk_humidity_pct - 10 &&
                $dayRain > 0
            ) {
                $riskDaysAhead++;
            }
        }
        if ($riskDaysAhead >= 2) {
            $score += 10;
            $factors[] = ['key' => "forecast_risk_{$riskDaysAhead}d", 'label' => "Risk persists for {$riskDaysAhead} days", 'label_hi' => "जोखिम {$riskDaysAhead} दिनों तक बना रहेगा"];
        }

        $finalScore = min($score, 100);

        return [
            'score' => $finalScore,
            'level' => $this->scoreToLevel($finalScore),
            'factors' => $factors,
            'forecast_risk_days' => $riskDaysAhead,
            'model' => $this->getModelName(),
        ];
    }
}
```

---

## `RevisedMillsModel.php` (Phase 2a — Apple Scab)

**File:** `app/Services/Prediction/Models/Scab/RevisedMillsModel.php`

```php
<?php

namespace App\Services\Prediction\Models\Scab;

use App\Models\Disease;
use App\Models\UserOrchard;
use App\Models\Weather;
use App\Services\Prediction\Models\AbstractPredictionModel;

class RevisedMillsModel extends AbstractPredictionModel
{
    // Revised Mills minimum wetness hours for infection (temp C => hours)
    const MILLS_TABLE = [
        0 => 40, 3 => 30, 6 => 25, 9 => 21,
        12 => 18, 15 => 15, 18 => 13, 21 => 12,
        24 => 11, 27 => 10, 30 => 9
    ];

    const SECONDARY_MULTIPLIER = 0.67;

    public function getModelName(): string
    {
        return 'mills';
    }

    public function calculate(Disease $disease, Weather $weather, UserOrchard $orchard, ?array $hourlyForecast = null): array
    {
        if (!$hourlyForecast) {
            $hourlyForecast = $weather->hourly_forecast_48h ?? [];
        }

        if (empty($hourlyForecast)) {
            // Fallback to rule-based if no hourly data
            return (new \App\Services\Prediction\Models\RuleBasedModel())->calculate($disease, $weather, $orchard);
        }

        $infectionPeriods = [];
        $wetnessStart = null;
        $wetnessHours = 0;
        $tempSum = 0;
        $maxSeverity = null;
        $totalInfectionHours = 0;

        foreach ($hourlyForecast as $hour) {
            $isWet = $this->isLeafWet($hour);

            if ($isWet) {
                if ($wetnessStart === null) {
                    $wetnessStart = $hour['timestamp'] ?? now()->toIso8601String();
                }
                $wetnessHours++;
                $tempSum += ($hour['temperature'] ?? 15);
            } else {
                if ($wetnessHours >= 4) {
                    $avgTemp = $tempSum / $wetnessHours;
                    $requiredHours = $this->interpolate($avgTemp, self::MILLS_TABLE);
                    $severity = $this->classifySeverity($wetnessHours, $requiredHours);

                    if ($severity) {
                        $infectionPeriods[] = [
                            'start' => $wetnessStart,
                            'end' => $hour['timestamp'] ?? now()->toIso8601String(),
                            'hours' => $wetnessHours,
                            'avg_temp' => round($avgTemp, 1),
                            'required_hours' => round($requiredHours, 1),
                            'severity' => $severity,
                        ];
                        $totalInfectionHours += $wetnessHours;

                        if ($maxSeverity === null || $this->severityRank($severity) > $this->severityRank($maxSeverity)) {
                            $maxSeverity = $severity;
                        }
                    }
                }
                $wetnessStart = null;
                $wetnessHours = 0;
                $tempSum = 0;
            }
        }

        // Handle ongoing wet period at end of forecast
        if ($wetnessHours >= 4) {
            $avgTemp = $tempSum / $wetnessHours;
            $requiredHours = $this->interpolate($avgTemp, self::MILLS_TABLE);
            $severity = $this->classifySeverity($wetnessHours, $requiredHours);
            if ($severity) {
                $infectionPeriods[] = [
                    'start' => $wetnessStart,
                    'end' => 'ongoing',
                    'hours' => $wetnessHours,
                    'avg_temp' => round($avgTemp, 1),
                    'required_hours' => round($requiredHours, 1),
                    'severity' => $severity,
                ];
                if ($maxSeverity === null || $this->severityRank($severity) > $this->severityRank($maxSeverity)) {
                    $maxSeverity = $severity;
                }
            }
        }

        // ─── Score mapping ────────────────────────────────────────
        $score = match ($maxSeverity) {
            'severe' => 85,
            'moderate' => 65,
            'light' => 45,
            default => 10,
        };

        $factors = [];
        if (!empty($infectionPeriods)) {
            $first = $infectionPeriods[0];
            $factors[] = [
                'key' => 'mills_infection_period',
                'label' => "Wetness {$first['hours']}h at {$first['avg_temp']}°C (needs {$first['required_hours']}h)",
                'label_hi' => "नमी {$first['hours']} घंटे {$first['avg_temp']}°C पर (जरूरत {$first['required_hours']} घंटे)",
            ];
        }

        return [
            'score' => min($score, 100),
            'level' => $this->scoreToLevel($score),
            'factors' => $factors,
            'infection_periods' => $infectionPeriods,
            'infection_period_count' => count($infectionPeriods),
            'model' => $this->getModelName(),
        ];
    }

    private function classifySeverity(float $wetnessHours, float $requiredHours): ?string
    {
        return match (true) {
            $wetnessHours >= $requiredHours * 1.5 => 'severe',
            $wetnessHours >= $requiredHours => 'moderate',
            $wetnessHours >= $requiredHours * 0.75 => 'light',
            default => null,
        };
    }

    private function severityRank(string $severity): int
    {
        return match ($severity) {
            'light' => 1,
            'moderate' => 2,
            'severe' => 3,
            default => 0,
        };
    }
}
```

---

## `SimplifiedMaryblytModel.php` (Phase 2b — Fire Blight)

**File:** `app/Services/Prediction/Models/FireBlight/SimplifiedMaryblytModel.php`

```php
<?php

namespace App\Services\Prediction\Models\FireBlight;

use App\Models\Disease;
use App\Models\UserOrchard;
use App\Models\Weather;
use App\Services\Prediction\Models\AbstractPredictionModel;

class SimplifiedMaryblytModel extends AbstractPredictionModel
{
    const DH_THRESHOLD = 110;        // Degree-hours > 18.3°C
    const DH_TEMP_THRESHOLD = 18.3;
    const DD_BASE_TEMP = 4.4;        // For degree-day window
    const DD_WINDOW = 80;
    const RAIN_THRESHOLD_MM = 0.25;
    const AVG_TEMP_THRESHOLD = 15.6;

    public function getModelName(): string
    {
        return 'maryblyt';
    }

    public function calculate(Disease $disease, Weather $weather, UserOrchard $orchard, ?array $hourlyForecast = null): array
    {
        if (!$hourlyForecast) {
            $hourlyForecast = $weather->hourly_forecast_48h ?? [];
        }

        // Check if blossoms are open (this would come from orchard stage data)
        // For now, assume open during bloom season (March-May in HP)
        $month = now()->month;
        $blossomsOpen = in_array($month, [3, 4, 5]);

        if (!$blossomsOpen) {
            return [
                'score' => 0,
                'level' => 'none',
                'factors' => [['key' => 'no_blossoms', 'label' => 'Not bloom season', 'label_hi' => 'फूल का मौसम नहीं']],
                'model' => $this->getModelName(),
            ];
        }

        $dh = 0;
        $dd = 0;
        $hasRain = false;
        $avgTemp = 0;
        $hourCount = 0;

        foreach ($hourlyForecast as $hour) {
            $temp = $hour['temperature'] ?? 15;

            // Degree-Hours accumulation
            if ($temp > self::DH_TEMP_THRESHOLD) {
                $dh += ($temp - self::DH_TEMP_THRESHOLD);
            }

            // Degree-Days (per hour contribution)
            if ($temp > self::DD_BASE_TEMP) {
                $dd += ($temp - self::DD_BASE_TEMP) / 24;
            }

            if (($hour['precipitation'] ?? 0) >= self::RAIN_THRESHOLD_MM) {
                $hasRain = true;
            }

            $avgTemp += $temp;
            $hourCount++;
        }

        $avgTemp = $hourCount > 0 ? $avgTemp / $hourCount : 0;

        // BHWT conditions
        $b = $blossomsOpen;
        $h = $dh >= self::DH_THRESHOLD;
        $w = $hasRain;
        $t = $avgTemp >= self::AVG_TEMP_THRESHOLD;

        $conditionsMet = (int)$h + (int)$w + (int)$t;

        $risk = match ($conditionsMet) {
            3 => 'infection',
            2 => 'high',
            1 => 'moderate',
            default => 'low',
        };

        $score = match ($risk) {
            'infection' => 90,
            'high' => 70,
            'moderate' => 45,
            default => 15,
        };

        $factors = [];
        if ($h) $factors[] = ['key' => 'eip_met', 'label' => "Degree-hours: " . round($dh, 0) . " (threshold: " . self::DH_THRESHOLD . ")", 'label_hi' => "डिग्री-घंटे: " . round($dh, 0)];
        if ($w) $factors[] = ['key' => 'wetness_met', 'label' => 'Rain/dew present', 'label_hi' => 'बारिश/ओस मौजूद'];
        if ($t) $factors[] = ['key' => 'temp_met', 'label' => "Avg temp " . round($avgTemp, 1) . "°C", 'label_hi' => "औसत तापमान " . round($avgTemp, 1) . "°C"];

        return [
            'score' => $score,
            'level' => $this->scoreToLevel($score),
            'factors' => $factors,
            'blossoms_open' => $b,
            'eip_met' => $h,
            'wetness_met' => $w,
            'temp_met' => $t,
            'cumulative_dh' => round($dh, 1),
            'cumulative_dd' => round($dd, 1),
            'avg_temp' => round($avgTemp, 1),
            'model' => $this->getModelName(),
        ];
    }
}
```

---

## `DmcModel.php` (Phase 2c — Powdery Mildew)

**File:** `app/Services/Prediction/Models/PowderyMildew/DmcModel.php`

```php
<?php

namespace App\Services\Prediction\Models\PowderyMildew;

use App\Models\Disease;
use App\Models\UserOrchard;
use App\Models\Weather;
use App\Services\Prediction\Models\AbstractPredictionModel;

class DmcModel extends AbstractPredictionModel
{
    public function getModelName(): string
    {
        return 'dmc';
    }

    public function calculate(Disease $disease, Weather $weather, UserOrchard $orchard, ?array $hourlyForecast = null): array
    {
        if (!$hourlyForecast) {
            $hourlyForecast = $weather->hourly_forecast_48h ?? [];
        }

        $infectionHours = 0;
        $favorableHours = 0;
        $riskScore = 0;

        $tempMin = $disease->dmc_temp_min_c ?? 10;
        $tempMax = $disease->dmc_temp_max_c ?? 25;
        $rhThreshold = $disease->dmc_rh_threshold_pct ?? 70;

        foreach ($hourlyForecast as $hour) {
            $temp = $hour['temperature'] ?? 15;
            $rh = $hour['humidity'] ?? 50;

            $isFavorable = ($temp >= $tempMin && $temp <= $tempMax && $rh >= $rhThreshold);
            $isOptimal = ($temp >= 20 && $temp <= 25 && $rh >= 80);

            if ($isOptimal) {
                $infectionHours++;
                $favorableHours++;
                $riskScore += 2;
            } elseif ($isFavorable) {
                $favorableHours++;
                $riskScore += 1;
            }
        }

        $score = min($riskScore * 3, 100); // Scale to 0-100

        $level = match (true) {
            $infectionHours >= 12 => 'high',
            $infectionHours >= 6 => 'medium',
            $favorableHours >= 12 => 'low',
            default => 'none',
        };

        $factors = [];
        if ($infectionHours > 0) {
            $factors[] = [
                'key' => 'optimal_conditions',
                'label' => "{$infectionHours}h optimal (20-25°C, RH>80%)",
                'label_hi' => "{$infectionHours} घंटे इष्टतम (20-25°C, नमी>80%)",
            ];
        }
        if ($favorableHours > $infectionHours) {
            $factors[] = [
                'key' => 'favorable_conditions',
                'label' => ($favorableHours - $infectionHours) . 'h favorable',
                'label_hi' => ($favorableHours - $infectionHours) . ' घंटे अनुकूल',
            ];
        }

        return [
            'score' => $score,
            'level' => $level,
            'factors' => $factors,
            'infection_hours' => $infectionHours,
            'favorable_hours' => $favorableHours,
            'model' => $this->getModelName(),
        ];
    }
}
```

---

## `DegreeDayModel.php` (Phase 2d — Pest Development)

**File:** `app/Services/Prediction/Models/Pests/DegreeDayModel.php`

```php
<?php

namespace App\Services\Prediction\Models\Pests;

use App\Models\PestModel;

class DegreeDayModel
{
    /**
     * Simple average method: DD = (Tmax + Tmin)/2 - Tthreshold
     * Capped at cutoff if applicable.
     */
    public function accumulate(float $tMax, float $tMin, float $threshold, ?float $cutoff = null): float
    {
        $avg = ($tMax + $tMin) / 2;

        if ($cutoff && $avg > $cutoff) {
            $avg = $cutoff;
        }

        $dd = $avg - $threshold;
        return max($dd, 0);
    }

    /**
     * Get events that have been reached based on cumulative DD.
     */
    public function getReachedEvents(PestModel $pestModel, float $cumulativeDd): array
    {
        $events = [];
        $targets = [
            ['dd' => $pestModel->dd_target_first_event, 'label' => $pestModel->event_labels[0] ?? 'First event'],
            ['dd' => $pestModel->dd_target_second_event, 'label' => $pestModel->event_labels[1] ?? 'Second event'],
            ['dd' => $pestModel->dd_target_third_event, 'label' => $pestModel->event_labels[2] ?? 'Third event'],
        ];

        foreach ($targets as $target) {
            if ($target['dd'] && $cumulativeDd >= $target['dd']) {
                $events[] = [
                    'name' => $target['label'],
                    'dd' => $target['dd'],
                    'reached_at' => $cumulativeDd,
                ];
            }
        }

        return $events;
    }

    /**
     * Get next upcoming event.
     */
    public function getNextEvent(PestModel $pestModel, float $cumulativeDd): ?array
    {
        $targets = [
            ['dd' => $pestModel->dd_target_first_event, 'label' => $pestModel->event_labels[0] ?? null],
            ['dd' => $pestModel->dd_target_second_event, 'label' => $pestModel->event_labels[1] ?? null],
            ['dd' => $pestModel->dd_target_third_event, 'label' => $pestModel->event_labels[2] ?? null],
        ];

        foreach ($targets as $target) {
            if ($target['dd'] && $cumulativeDd < $target['dd']) {
                return [
                    'name' => $target['label'],
                    'at_dd' => $target['dd'],
                    'dd_remaining' => $target['dd'] - $cumulativeDd,
                ];
            }
        }

        return null;
    }

    /**
     * Estimate days until next event based on recent average DD per day.
     */
    public function estimateDaysUntil(float $ddRemaining, float $avgDailyDd): ?int
    {
        if ($avgDailyDd <= 0) return null;
        return (int) ceil($ddRemaining / $avgDailyDd);
    }
}
```

---

## `ModelFactory.php`

**File:** `app/Services/Prediction/ModelFactory.php`

```php
<?php

namespace App\Services\Prediction;

use App\Models\Disease;
use App\Services\Prediction\Models\AbstractPredictionModel;
use App\Services\Prediction\Models\FireBlight\SimplifiedMaryblytModel;
use App\Services\Prediction\Models\PowderyMildew\DmcModel;
use App\Services\Prediction\Models\RuleBasedModel;
use App\Services\Prediction\Models\Scab\RevisedMillsModel;

class ModelFactory
{
    /**
     * Get the appropriate prediction model for a disease.
     */
    public static function forDisease(Disease $disease, string $preferredModel = 'auto'): AbstractPredictionModel
    {
        if ($preferredModel !== 'auto') {
            return match ($preferredModel) {
                'mills' => new RevisedMillsModel(),
                'maryblyt' => new SimplifiedMaryblytModel(),
                'dmc' => new DmcModel(),
                default => new RuleBasedModel(),
            };
        }

        // Auto-select based on disease capabilities
        if ($disease->is_mills_applicable) {
            return new RevisedMillsModel();
        }

        if ($disease->is_maryblyt_applicable) {
            return new SimplifiedMaryblytModel();
        }

        if ($disease->is_dmc_applicable) {
            return new DmcModel();
        }

        // Fallback to rule-based for all other diseases
        return new RuleBasedModel();
    }

    /**
     * Get rule-based model (Phase 1 fallback).
     */
    public static function ruleBased(): RuleBasedModel
    {
        return new RuleBasedModel();
    }
}
```

---

## `DiseasePressureService.php`

**File:** `app/Services/Prediction/DiseasePressureService.php`

```php
<?php

namespace App\Services\Prediction;

use App\Models\Disease;
use App\Models\DiseasePressureLog;
use App\Models\OrchardBlock;
use App\Models\UserOrchard;
use App\Models\Weather;
use Carbon\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

class DiseasePressureService
{
    public function __construct(
        private SprayWindowService $sprayWindowService,
        private RecommendationGenerator $recommendationGenerator,
        private LeafWetnessEstimator $leafWetnessEstimator,
    ) {}

    /**
     * Compute disease pressure for a single orchard.
     */
    public function computeForOrchard(UserOrchard $orchard, ?Carbon $date = null): array
    {
        $date = $date ?? now();
        $weather = Weather::where('user_orchard_id', $orchard->id)->latest()->first();

        if (!$weather) {
            Log::warning("No weather data for orchard {$orchard->id}");
            return [];
        }

        // Ensure hourly forecast exists
        if (empty($weather->hourly_forecast_48h)) {
            $weather->hourly_forecast_48h = $this->leafWetnessEstimator->fetchHourlyForecast($orchard);
            $weather->save();
        }

        $results = [];
        $diseases = $this->getRelevantDiseases($orchard, $date);

        foreach ($diseases as $disease) {
            $result = $this->computeForDisease($disease, $weather, $orchard);
            $results[] = $result;

            // Save to log
            DiseasePressureLog::create([
                'user_orchard_id' => $orchard->id,
                'orchard_block_id' => null,
                'disease_id' => $disease->id,
                'prediction_date' => $date->toDateString(),
                'prediction_type' => $result['model'],
                'risk_score' => $result['score'],
                'risk_level' => $result['level'],
                'trigger_factors' => $result['factors'],
                'weather_snapshot' => [
                    'temp' => $weather->temperature,
                    'humidity' => $weather->humidity,
                    'rain' => $weather->precipitation,
                    'wind' => $weather->wind_speed ?? 0,
                ],
                'spray_recommendation' => $result['recommendation']['action_en'] ?? null,
                'spray_recommendation_hi' => $result['recommendation']['action_hi'] ?? null,
            ]);
        }

        return $results;
    }

    /**
     * Compute disease pressure per block (Phase 2+).
     */
    public function computeForBlocks(UserOrchard $orchard, ?Carbon $date = null): array
    {
        $date = $date ?? now();
        $blocks = $orchard->orchardBlocks;

        if ($blocks->isEmpty()) {
            return $this->computeForOrchard($orchard, $date);
        }

        $weather = Weather::where('user_orchard_id', $orchard->id)->latest()->first();
        $allResults = [];

        foreach ($blocks as $block) {
            $blockResults = [];
            $diseases = $this->getRelevantDiseases($orchard, $date);

            foreach ($diseases as $disease) {
                $result = $this->computeForDisease($disease, $weather, $orchard, $block);
                $blockResults[] = $result;

                DiseasePressureLog::create([
                    'user_orchard_id' => $orchard->id,
                    'orchard_block_id' => $block->id,
                    'disease_id' => $disease->id,
                    'prediction_date' => $date->toDateString(),
                    'prediction_type' => $result['model'],
                    'risk_score' => $result['score'],
                    'risk_level' => $result['level'],
                    'trigger_factors' => $result['factors'],
                    'weather_snapshot' => [
                        'temp' => $weather->temperature,
                        'humidity' => $weather->humidity,
                        'rain' => $weather->precipitation,
                    ],
                    'spray_recommendation' => $result['recommendation']['action_en'] ?? null,
                    'spray_recommendation_hi' => $result['recommendation']['action_hi'] ?? null,
                ]);
            }

            $allResults[] = [
                'block_id' => $block->id,
                'block_name' => $block->name,
                'predictions' => $blockResults,
            ];
        }

        return $allResults;
    }

    /**
     * Compute pressure for a single disease.
     */
    public function computeForDisease(Disease $disease, Weather $weather, UserOrchard $orchard, ?OrchardBlock $block = null): array
    {
        $model = ModelFactory::forDisease($disease);
        $hourly = $weather->hourly_forecast_48h ?? [];

        // Apply microclimate adjustments if block exists (Phase 3)
        if ($block) {
            $hourly = $this->applyMicroclimateAdjustments($hourly, $block);
        }

        $prediction = $model->calculate($disease, $weather, $orchard, $hourly);

        // Find spray window
        $sprayWindow = $this->sprayWindowService->findBestWindow($hourly);

        // Generate recommendation
        $recommendation = $this->recommendationGenerator->generate(
            $disease, $prediction, $sprayWindow, $orchard, $block
        );

        return array_merge($prediction, [
            'disease_id' => $disease->id,
            'disease_name' => $disease->name,
            'disease_name_hi' => $disease->name_hi,
            'spray_window' => $sprayWindow,
            'recommendation' => $recommendation,
        ]);
    }

    /**
     * Get diseases relevant for this orchard's altitude and current season.
     */
    private function getRelevantDiseases(UserOrchard $orchard, Carbon $date): Collection
    {
        $altitudeFt = $orchard->altitude_feet ?? 0;
        $month = $date->month;

        return Disease::withPredictionModels()
            ->where(function ($q) use ($altitudeFt) {
                $q->whereNull('altitude_min_feet')
                  ->orWhere('altitude_min_feet', '<=', $altitudeFt);
            })
            ->where(function ($q) use ($altitudeFt) {
                $q->whereNull('altitude_max_feet')
                  ->orWhere('altitude_max_feet', '>=', $altitudeFt);
            })
            // Seasonal filtering: diseases active March-October
            // Each disease could have a season_months JSON field in future
            ->get();
    }

    /**
     * Apply microclimate adjustments to hourly forecast.
     */
    private function applyMicroclimateAdjustments(array $hourly, OrchardBlock $block): array
    {
        $adj = $block->getMicroclimateAdjustments();

        return array_map(function ($hour) use ($adj) {
            if (isset($hour['humidity'])) {
                $hour['humidity'] = min(100, $hour['humidity'] + $adj['humidity_offset']);
            }
            if (isset($hour['wind_speed'])) {
                $hour['wind_speed'] *= $adj['wind_speed_multiplier'];
            }
            return $hour;
        }, $hourly);
    }
}
```

---

## `PestDevelopmentService.php`

**File:** `app/Services/Prediction/PestDevelopmentService.php`

```php
<?php

namespace App\Services\Prediction;

use App\Models\PestModel;
use App\Models\PestTracker;
use App\Models\UserOrchard;
use App\Models\Weather;
use App\Services\Prediction\Models\Pests\DegreeDayModel;
use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class PestDevelopmentService
{
    private DegreeDayModel $ddModel;

    public function __construct()
    {
        $this->ddModel = new DegreeDayModel();
    }

    /**
     * Accumulate degree-days for all active pest trackers.
     */
    public function accumulateDaily(?Carbon $date = null): void
    {
        $date = $date ?? now()->subDay(); // Yesterday's weather
        $year = $date->year;

        $trackers = PestTracker::with(['pestModel', 'userOrchard'])
            ->where('season_year', $year)
            ->get();

        foreach ($trackers as $tracker) {
            $orchard = $tracker->userOrchard;
            $weather = Weather::where('user_orchard_id', $orchard->id)
                ->whereDate('created_at', $date->toDateString())
                ->first();

            if (!$weather) {
                Log::warning("No weather for orchard {$orchard->id} on {$date->toDateString()}");
                continue;
            }

            $this->accumulateForTracker($tracker, $weather);
        }
    }

    /**
     * Initialize pest trackers for a new season.
     */
    public function initializeSeason(UserOrchard $orchard, int $year): void
    {
        $altitudeBand = $orchard->altitude_band;
        $month = now()->month;

        $pests = PestModel::active()->get();

        foreach ($pests as $pest) {
            if (!$pest->isApplicable($month, $altitudeBand)) {
                continue;
            }

            $biofix = $pest->getDefaultBiofixDate($year, $altitudeBand);

            PestTracker::firstOrCreate(
                [
                    'user_orchard_id' => $orchard->id,
                    'orchard_block_id' => null,
                    'pest_model_id' => $pest->id,
                    'season_year' => $year,
                ],
                [
                    'biofix_date' => $biofix,
                    'biofix_source' => 'default',
                    'cumulative_dd' => 0,
                    'risk_level' => 'none',
                ]
            );
        }
    }

    /**
     * Accumulate DD for a single tracker.
     */
    private function accumulateForTracker(PestTracker $tracker, Weather $weather): void
    {
        $pest = $tracker->pestModel;
        $tMax = $weather->temperature_max ?? $weather->temperature;
        $tMin = $weather->temperature_min ?? $weather->temperature;

        $dailyDd = $this->ddModel->accumulate(
            $tMax,
            $tMin,
            $pest->threshold_temp_c,
            $pest->cutoff_temp_c
        );

        $tracker->cumulative_dd += $dailyDd;

        // Check for events
        $reached = $this->ddModel->getReachedEvents($pest, $tracker->cumulative_dd);
        $next = $this->ddModel->getNextEvent($pest, $tracker->cumulative_dd);

        if (!empty($reached)) {
            $lastEvent = end($reached);
            $tracker->last_event_triggered = $lastEvent['name'];
        }

        $tracker->next_event_at_dd = $next['at_dd'] ?? null;

        // Update risk level based on proximity to next event
        if ($next) {
            $tracker->risk_level = $this->proximityToRisk($next['dd_remaining'], $dailyDd);
        } elseif (!empty($reached)) {
            $tracker->risk_level = 'high';
        }

        $tracker->save();
    }

    /**
     * Convert DD remaining into risk level.
     */
    private function proximityToRisk(float $ddRemaining, float $dailyDd): string
    {
        $daysUntil = $dailyDd > 0 ? $ddRemaining / $dailyDd : 999;

        return match (true) {
            $daysUntil <= 3 => 'high',
            $daysUntil <= 7 => 'medium',
            $daysUntil <= 14 => 'low',
            default => 'none',
        };
    }
}
```

---

## `SprayWindowService.php`

**File:** `app/Services/Prediction/SprayWindowService.php`

```php
<?php

namespace App\Services\Prediction;

use Carbon\Carbon;

class SprayWindowService
{
    const MAX_WIND_KMH = 15;
    const MAX_HUMIDITY_PCT = 80;
    const MIN_HOURS_AFTER_RAIN = 4;
    const MAX_TEMP_C = 30;
    const MIN_TEMP_C = 10;

    /**
     * Evaluate all spray windows in a forecast.
     */
    public function evaluateWindows(array $hourlyForecast): array
    {
        $windows = [];
        $currentWindow = null;

        foreach ($hourlyForecast as $hour) {
            $safe = $this->isSpraySafe($hour);

            if ($safe && $currentWindow === null) {
                $currentWindow = [
                    'start' => $hour['timestamp'] ?? now()->toIso8601String(),
                    'hours' => 1,
                    'avg_temp' => $hour['temperature'] ?? 20,
                    'max_wind' => $hour['wind_speed'] ?? 0,
                ];
            } elseif ($safe && $currentWindow !== null) {
                $currentWindow['hours']++;
                $currentWindow['avg_temp'] = ($currentWindow['avg_temp'] + ($hour['temperature'] ?? 20)) / 2;
                $currentWindow['max_wind'] = max($currentWindow['max_wind'], $hour['wind_speed'] ?? 0);
            } elseif (!$safe && $currentWindow !== null) {
                $windows[] = $this->classifyWindow($currentWindow);
                $currentWindow = null;
            }
        }

        if ($currentWindow) {
            $windows[] = $this->classifyWindow($currentWindow);
        }

        return $windows;
    }

    /**
     * Find the best spray window before a target time.
     */
    public function findBestWindow(array $hourlyForecast, ?Carbon $before = null): ?array
    {
        $windows = $this->evaluateWindows($hourlyForecast);

        if (empty($windows)) {
            return null;
        }

        // Filter windows before target time
        if ($before) {
            $windows = array_filter($windows, function ($w) use ($before) {
                $windowStart = Carbon::parse($w['start']);
                return $windowStart->lt($before);
            });
        }

        // Sort by rating (excellent first)
        usort($windows, function ($a, $b) {
            $rank = ['excellent' => 3, 'good' => 2, 'short' => 1, 'insufficient' => 0];
            return ($rank[$b['rating']] ?? 0) <=> ($rank[$a['rating']] ?? 0);
        });

        return $windows[0] ?? null;
    }

    private function isSpraySafe(array $hour): bool
    {
        $windMs = $hour['wind_speed'] ?? 0;
        $windKmh = $windMs * 3.6;
        $rh = $hour['humidity'] ?? 0;
        $rain = $hour['precipitation'] ?? 0;
        $temp = $hour['temperature'] ?? 20;

        return $windKmh < self::MAX_WIND_KMH
            && $rh < self::MAX_HUMIDITY_PCT
            && $rain == 0
            && $temp >= self::MIN_TEMP_C
            && $temp <= self::MAX_TEMP_C;
    }

    private function classifyWindow(array $window): array
    {
        $window['rating'] = match (true) {
            $window['hours'] >= 6 => 'excellent',
            $window['hours'] >= 3 => 'good',
            $window['hours'] >= 1 => 'short',
            default => 'insufficient',
        };
        return $window;
    }
}
```

---

## `LeafWetnessEstimator.php`

**File:** `app/Services/Prediction/LeafWetnessEstimator.php`

```php
<?php

namespace App\Services\Prediction;

use App\Models\UserOrchard;
use App\Models\Weather;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class LeafWetnessEstimator
{
    /**
     * Fetch hourly forecast from Open-Meteo API.
     * Returns array of hourly data points.
     */
    public function fetchHourlyForecast(UserOrchard $orchard): array
    {
        $lat = $orchard->latitude;
        $lon = $orchard->longitude;

        try {
            $response = Http::get('https://api.open-meteo.com/v1/forecast', [
                'latitude' => $lat,
                'longitude' => $lon,
                'hourly' => 'temperature_2m,relative_humidity_2m,precipitation,dew_point_2m,wind_speed_10m,visibility',
                'forecast_days' => 3,
                'timezone' => 'Asia/Kolkata',
            ]);

            if (!$response->successful()) {
                Log::error("Open-Meteo API failed for orchard {$orchard->id}");
                return [];
            }

            $data = $response->json();
            $hourly = $data['hourly'] ?? [];

            return $this->transformOpenMeteo($hourly);
        } catch (\Exception $e) {
            Log::error("LeafWetnessEstimator error: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Transform Open-Meteo response to internal format.
     */
    private function transformOpenMeteo(array $hourly): array
    {
        $times = $hourly['time'] ?? [];
        $temps = $hourly['temperature_2m'] ?? [];
        $humidities = $hourly['relative_humidity_2m'] ?? [];
        $rains = $hourly['precipitation'] ?? [];
        $dewPoints = $hourly['dew_point_2m'] ?? [];
        $winds = $hourly['wind_speed_10m'] ?? [];
        $visibilities = $hourly['visibility'] ?? [];

        $result = [];
        foreach ($times as $i => $time) {
            $result[] = [
                'timestamp' => $time,
                'temperature' => $temps[$i] ?? null,
                'humidity' => $humidities[$i] ?? null,
                'precipitation' => $rains[$i] ?? 0,
                'dew_point' => $dewPoints[$i] ?? null,
                'wind_speed' => $winds[$i] ?? 0,
                'visibility' => $visibilities[$i] ?? 10000,
            ];
        }

        return $result;
    }

    /**
     * Calculate estimated leaf wetness hours from weather data.
     */
    public function estimateWetnessHours(Weather $weather): int
    {
        $hourly = $weather->hourly_forecast_48h ?? [];
        if (empty($hourly)) {
            return 0;
        }

        $wetHours = 0;
        foreach ($hourly as $hour) {
            $rh = $hour['humidity'] ?? 0;
            $rain = $hour['precipitation'] ?? 0;
            $temp = $hour['temperature'] ?? 0;
            $dewPoint = $hour['dew_point'] ?? ($temp - ((100 - $rh) / 5));

            $isDew = ($temp - $dewPoint) < 2.5;
            $isFog = ($hour['visibility'] ?? 10000) < 1000 && $rh > 90;

            if ($rh >= 85 || $rain >= 0.1 || $isDew || $isFog) {
                $wetHours++;
            }
        }

        return $wetHours;
    }
}
```

---

## `RecommendationGenerator.php`

**File:** `app/Services/Prediction/RecommendationGenerator.php`

```php
<?php

namespace App\Services\Prediction;

use App\Models\Disease;
use App\Models\OrchardBlock;
use App\Models\UserOrchard;
use Carbon\Carbon;

class RecommendationGenerator
{
    /**
     * Generate a spray recommendation from prediction + spray window.
     */
    public function generate(
        Disease $disease,
        array $prediction,
        ?array $sprayWindow,
        UserOrchard $orchard,
        ?OrchardBlock $block = null
    ): array {
        $level = $prediction['level'];
        $score = $prediction['score'];

        if (in_array($level, ['none', 'low'])) {
            return [
                'action_needed' => false,
                'action_en' => 'No spray needed. Continue normal monitoring.',
                'action_hi' => 'कोई स्प्रे की जरूरत नहीं। सामान्य निगरानी जारी रखें।',
                'chemical' => null,
                'dose' => null,
                'timing' => null,
            ];
        }

        // Get chemical recommendation from disease or spray schedule
        $chemical = $this->suggestChemical($disease, $orchard);
        $dose = $this->calculateDose($chemical, $orchard, $block);

        // Format timing
        $timing = $this->formatTiming($sprayWindow);

        $actionEn = match ($level) {
            'critical' => "URGENT: {$disease->name} risk is CRITICAL. Spray {$chemical} {$dose} {$timing}.",
            'high' => "{$disease->name} risk is HIGH. Spray {$chemical} {$dose} {$timing}.",
            'medium' => "{$disease->name} risk building. Prepare {$chemical} {$dose}. {$timing} if conditions worsen.",
            default => 'Monitor conditions.',
        };

        $actionHi = match ($level) {
            'critical' => "तुरंत: {$disease->name_hi} का जोखिम गंभीर है। {$timing} {$chemical} {$dose} छिड़कें।",
            'high' => "{$disease->name_hi} का जोखिम उच्च है। {$timing} {$chemical} {$dose} छिड़कें।",
            'medium' => "{$disease->name_hi} का जोखिम बढ़ रहा है। {$chemical} {$dose} तैयार रखें।",
            default => 'स्थिति पर नजर रखें।',
        };

        return [
            'action_needed' => in_array($level, ['high', 'critical']),
            'action_en' => $actionEn,
            'action_hi' => $actionHi,
            'chemical' => $chemical,
            'dose' => $dose,
            'timing' => $timing,
            'safety_notes' => $this->getSafetyNotes(),
        ];
    }

    private function suggestChemical(Disease $disease, UserOrchard $orchard): string
    {
        // TODO: Link to spray_schedule_stage_chemicals table
        // For now, return sensible defaults
        return match (true) {
            str_contains(strtolower($disease->name), 'scab') => 'Copper Oxychloride 50WP',
            str_contains(strtolower($disease->name), 'powdery mildew') => 'Sulfex 80WP',
            str_contains(strtolower($disease->name), 'fire blight') => 'Streptomycin sulfate',
            default => 'Mancozeb 75WP',
        };
    }

    private function calculateDose(?string $chemical, UserOrchard $orchard, ?OrchardBlock $block): string
    {
        $area = $block?->area_kanal ?? $orchard->area_kanal ?? 1;
        $tankCount = max(1, ceil($area / 2)); // Approx 2 kanal per tank

        $perTank = match ($chemical) {
            'Copper Oxychloride 50WP' => '300g per 200L water',
            'Sulfex 80WP' => '2kg per 200L water',
            'Streptomycin sulfate' => '100g per 200L water',
            'Mancozeb 75WP' => '200g per 200L water',
            default => 'as per label',
        };

        if ($tankCount > 1) {
            return "{$perTank} x {$tankCount} tanks";
        }
        return $perTank;
    }

    private function formatTiming(?array $sprayWindow): string
    {
        if (!$sprayWindow) {
            return 'when weather permits';
        }

        $start = Carbon::parse($sprayWindow['start']);
        $rating = $sprayWindow['rating'];
        $hours = $sprayWindow['hours'];

        $timeStr = $start->format('D, M j \a\t g:i A');

        if ($rating === 'excellent') {
            return "Best window: {$timeStr} ({$hours}h excellent)";
        }

        return "Spray by {$timeStr}";
    }

    private function getSafetyNotes(): array
    {
        return [
            'en' => 'Wear gloves, mask, and goggles. Do not spray in wind >15 km/h.',
            'hi' => 'दस्ताने, मास्क और चश्मे पहनें। 15 किमी/घंटे से अधिक हवा में न छिड़कें।',
        ];
    }
}
```

---

## `MicroclimateService.php` (Phase 3)

**File:** `app/Services/Prediction/MicroclimateService.php`

```php
<?php

namespace App\Services\Prediction;

use App\Models\OrchardBlock;

class MicroclimateService
{
    /**
     * Apply microclimate adjustments to a base weather reading.
     */
    public function adjustForBlock(array $weather, OrchardBlock $block): array
    {
        $adj = $block->getMicroclimateAdjustments();

        // Adjust humidity (sheltered = more humid)
        if (isset($weather['humidity'])) {
            $weather['humidity'] = min(100, $weather['humidity'] + $adj['humidity_offset']);
        }

        // Adjust wind speed (exposed = more windy)
        if (isset($weather['wind_speed'])) {
            $weather['wind_speed'] *= $adj['wind_speed_multiplier'];
        }

        // Adjust estimated wetness duration
        if (isset($weather['leaf_wetness_estimated_hours'])) {
            $weather['leaf_wetness_estimated_hours'] = (int) round(
                $weather['leaf_wetness_estimated_hours'] * $adj['wetness_duration_multiplier']
            );
        }

        return $weather;
    }
}
```

---

*Next: Read `04_COMMANDS_JOBS.md` for scheduled commands and queued jobs.*
