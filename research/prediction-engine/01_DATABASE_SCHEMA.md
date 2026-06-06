# 01 — Database Schema & Migrations

> **Run these migrations FIRST** before any code. All tables use existing conventions.

---

## Migration 1: Create `orchard_blocks` Table

**File:** `database/migrations/2026_05_21_000001_create_orchard_blocks_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orchard_blocks', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_orchard_id')->constrained('user_orchards')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name', 100);                         // e.g. "Block A", "Upper Slope"
            $table->foreignId('variety_id')->nullable()->constrained('varieties')->nullOnDelete();
            $table->foreignId('rootstock_id')->nullable()->constrained('rootstocks')->nullOnDelete();
            $table->decimal('area_kanal', 8, 2)->nullable();
            $table->unsignedInteger('plant_count')->nullable();
            $table->unsignedTinyInteger('tree_age_years')->nullable();
            $table->string('spacing_meters', 20)->nullable();    // e.g. "4x4"
            $table->enum('soil_type', ['loam', 'clay', 'sandy', 'silty', 'peaty'])->nullable();
            $table->decimal('soil_ph', 3, 1)->nullable();
            $table->enum('irrigation_type', ['drip', 'sprinkler', 'flood', 'rainfed'])->nullable();
            $table->enum('aspect', ['north', 'south', 'east', 'west', 'flat'])->nullable();
            $table->unsignedTinyInteger('slope_percent')->nullable(); // e.g. 15 = 15%
            $table->boolean('is_sunny_exposure')->default(true);
            $table->enum('wind_exposure', ['sheltered', 'moderate', 'exposed'])->nullable();
            $table->enum('frost_pocket_risk', ['low', 'medium', 'high'])->nullable();
            $table->timestamps();

            $table->index('user_orchard_id');
            $table->index('user_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orchard_blocks');
    }
};
```

---

## Migration 2: Create `pest_models` Table

**File:** `database/migrations/2026_05_21_000002_create_pest_models_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('pest_models', function (Blueprint $table) {
            $table->smallIncrements('id');
            $table->string('name_en', 100);
            $table->string('name_hi', 100)->nullable();
            $table->string('scientific_name', 100)->nullable();
            $table->enum('type', ['insect', 'mite', 'mollusk', 'nematode']);
            $table->decimal('threshold_temp_c', 4, 1);           // Lower development threshold
            $table->decimal('cutoff_temp_c', 4, 1)->nullable();  // Upper cutoff (optional)
            $table->unsignedInteger('dd_target_first_event')->nullable();
            $table->unsignedInteger('dd_target_second_event')->nullable();
            $table->unsignedInteger('dd_target_third_event')->nullable();
            $table->json('event_labels')->nullable();            // ["First egg hatch", "Peak flight"]
            $table->json('applicable_months')->nullable();       // [4,5,6,7,8]
            $table->json('applicable_altitude_bands')->nullable(); // ["below_6000","6000_8000"]
            $table->boolean('is_active')->default(true);
            $table->unsignedSmallInteger('sort_order')->default(0);

            $table->index(['is_active', 'sort_order']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pest_models');
    }
};
```

---

## Migration 3: Create `pest_tracker` Table

**File:** `database/migrations/2026_05_21_000003_create_pest_tracker_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('pest_tracker', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_orchard_id')->constrained('user_orchards')->cascadeOnDelete();
            $table->foreignId('orchard_block_id')->nullable()->constrained('orchard_blocks')->cascadeOnDelete();
            $table->unsignedSmallInteger('pest_model_id');
            $table->unsignedSmallInteger('season_year');
            $table->date('biofix_date')->nullable();             // User-set or regional default
            $table->enum('biofix_source', ['trap', 'default', 'expert', 'user_reported'])->default('default');
            $table->decimal('cumulative_dd', 8, 1)->default(0);  // Current season accumulation
            $table->string('last_event_triggered', 50)->nullable();
            $table->unsignedInteger('next_event_at_dd')->nullable();
            $table->enum('risk_level', ['none', 'low', 'medium', 'high', 'critical'])->default('none');
            $table->timestamp('updated_at')->useCurrentOnUpdate();

            $table->unique(['user_orchard_id', 'orchard_block_id', 'pest_model_id', 'season_year'], 'uk_tracker');
            $table->index(['next_event_at_dd', 'risk_level']);
            $table->foreign('pest_model_id')->references('id')->on('pest_models')->cascadeOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pest_tracker');
    }
};
```

---

## Migration 4: Create `disease_pressure_log` Table

**File:** `database/migrations/2026_05_21_000004_create_disease_pressure_log_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('disease_pressure_log', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_orchard_id')->constrained('user_orchards')->cascadeOnDelete();
            $table->foreignId('orchard_block_id')->nullable()->constrained('orchard_blocks')->cascadeOnDelete();
            $table->foreignId('disease_id')->constrained('diseases')->cascadeOnDelete();
            $table->date('prediction_date');                     // Date this prediction is for
            $table->enum('prediction_type', ['rule', 'mills', 'maryblyt', 'dmc', 'dd_model', 'ml'])->default('rule');
            $table->unsignedTinyInteger('risk_score');           // 0-100
            $table->enum('risk_level', ['none', 'low', 'medium', 'high', 'critical']);
            $table->json('trigger_factors')->nullable();         // Which conditions triggered risk
            $table->json('weather_snapshot')->nullable();        // Temp, RH, rain, wind at time of calc
            $table->text('spray_recommendation')->nullable();    // Suggested action
            $table->text('spray_recommendation_hi')->nullable(); // Suggested action (Hindi)
            $table->boolean('is_confirmed')->nullable();         // Farmer feedback: was alert correct?
            $table->text('farmer_feedback')->nullable();
            $table->timestamp('created_at')->useCurrent();

            $table->index(['user_orchard_id', 'disease_id', 'prediction_date']);
            $table->index(['risk_level', 'prediction_date']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('disease_pressure_log');
    }
};
```

---

## Migration 5: Extend `diseases` Table

**File:** `database/migrations/2026_05_21_000005_add_model_fields_to_diseases_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('diseases', function (Blueprint $table) {
            // Mills Table fields for scab
            $table->boolean('is_mills_applicable')->default(false)->after('risk_humidity_pct');
            $table->tinyInteger('mills_temp_min_c')->nullable()->after('is_mills_applicable');
            $table->tinyInteger('mills_temp_max_c')->nullable()->after('mills_temp_min_c');
            $table->json('mills_wetness_hours')->nullable()->after('mills_temp_max_c');
            // Example: {"6": 18, "10": 12, "15": 9, "20": 8, "25": 6}

            // Maryblyt fields for fire blight
            $table->boolean('is_maryblyt_applicable')->default(false)->after('mills_wetness_hours');
            $table->unsignedInteger('maryblyt_dh_threshold')->nullable()->after('is_maryblyt_applicable');
            $table->decimal('maryblyt_temp_threshold_c', 4, 1)->nullable()->after('maryblyt_dh_threshold');

            // DMC fields for powdery mildew
            $table->boolean('is_dmc_applicable')->default(false)->after('maryblyt_temp_threshold_c');
            $table->unsignedTinyInteger('dmc_temp_min_c')->nullable()->after('is_dmc_applicable');
            $table->unsignedTinyInteger('dmc_temp_max_c')->nullable()->after('dmc_temp_min_c');
            $table->unsignedTinyInteger('dmc_rh_threshold_pct')->nullable()->after('dmc_temp_max_c');
            $table->unsignedTinyInteger('dmc_favorable_hours_threshold')->nullable()->after('dmc_rh_threshold_pct');
        });
    }

    public function down(): void
    {
        Schema::table('diseases', function (Blueprint $table) {
            $table->dropColumn([
                'is_mills_applicable', 'mills_temp_min_c', 'mills_temp_max_c', 'mills_wetness_hours',
                'is_maryblyt_applicable', 'maryblyt_dh_threshold', 'maryblyt_temp_threshold_c',
                'is_dmc_applicable', 'dmc_temp_min_c', 'dmc_temp_max_c',
                'dmc_rh_threshold_pct', 'dmc_favorable_hours_threshold',
            ]);
        });
    }
};
```

---

## Migration 6: Extend `weather` Table

**File:** `database/migrations/2026_05_21_000006_add_forecast_fields_to_weather_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('weather', function (Blueprint $table) {
            $table->json('hourly_forecast_48h')->nullable()->after('forecast_5day');
            $table->unsignedTinyInteger('leaf_wetness_estimated_hours')->nullable()->after('hourly_forecast_48h');
            $table->decimal('dew_point_c', 4, 1)->nullable()->after('leaf_wetness_estimated_hours');
        });
    }

    public function down(): void
    {
        Schema::table('weather', function (Blueprint $table) {
            $table->dropColumn(['hourly_forecast_48h', 'leaf_wetness_estimated_hours', 'dew_point_c']);
        });
    }
};
```

---

## Migration 7: Create `spray_logs` Table (Optional but Recommended)

**File:** `database/migrations/2026_05_21_000007_create_spray_logs_table.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('spray_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_orchard_id')->constrained('user_orchards')->cascadeOnDelete();
            $table->foreignId('orchard_block_id')->nullable()->constrained('orchard_blocks')->cascadeOnDelete();
            $table->foreignId('disease_id')->nullable()->constrained('diseases')->nullOnDelete();
            $table->foreignId('spray_schedule_stage_id')->nullable()->constrained('spray_schedule_stages')->nullOnDelete();
            $table->date('spray_date');
            $table->time('spray_time')->nullable();
            $table->string('chemical_name', 200)->nullable();
            $table->decimal('quantity_used', 8, 2)->nullable();
            $table->string('unit', 20)->nullable();              // g, ml, kg, L
            $table->decimal('water_used_liters', 8, 2)->nullable();
            $table->decimal('area_covered_kanal', 8, 2)->nullable();
            $table->enum('weather_condition', ['sunny', 'cloudy', 'windy', 'rainy'])->nullable();
            $table->text('notes')->nullable();
            $table->json('photos')->nullable();
            $table->unsignedInteger('reward_points')->default(0);
            $table->timestamps();

            $table->index(['user_orchard_id', 'spray_date']);
            $table->index('user_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('spray_logs');
    }
};
```

---

## Seeder: `DiseaseModelSeeder`

**File:** `database/seeders/DiseaseModelSeeder.php`

```php
<?php

namespace Database\Seeders;

use App\Models\Disease;
use Illuminate\Database\Seeder;

class DiseaseModelSeeder extends Seeder
{
    public function run(): void
    {
        // Apple Scab (Venturia inaequalis)
        Disease::where('name', 'like', '%Scab%')->orWhere('name_hi', 'like', '%छाई%')->update([
            'is_mills_applicable' => true,
            'mills_temp_min_c' => 0,
            'mills_temp_max_c' => 30,
            'mills_wetness_hours' => json_encode([
                '0' => 40, '3' => 30, '6' => 25, '9' => 21,
                '12' => 18, '15' => 15, '18' => 13, '21' => 12,
                '24' => 11, '27' => 10, '30' => 9
            ]),
        ]);

        // Fire Blight (Erwinia amylovora)
        Disease::where('name', 'like', '%Fire Blight%')->orWhere('name_hi', 'like', '%आग झुलसा%')->update([
            'is_maryblyt_applicable' => true,
            'maryblyt_dh_threshold' => 110,
            'maryblyt_temp_threshold_c' => 18.3,
        ]);

        // Powdery Mildew (Podosphaera leucotricha)
        Disease::where('name', 'like', '%Powdery Mildew%')->orWhere('name_hi', 'like', '%पाउडरी मिल्ड्यू%')->update([
            'is_dmc_applicable' => true,
            'dmc_temp_min_c' => 10,
            'dmc_temp_max_c' => 25,
            'dmc_rh_threshold_pct' => 70,
            'dmc_favorable_hours_threshold' => 6,
        ]);
    }
}
```

---

## Seeder: `PestModelSeeder`

**File:** `database/seeders/PestModelSeeder.php`

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class PestModelSeeder extends Seeder
{
    public function run(): void
    {
        DB::table('pest_models')->insert([
            [
                'name_en' => 'Codling Moth',
                'name_hi' => 'सेब का कीड़ा',
                'scientific_name' => 'Cydia pomonella',
                'type' => 'insect',
                'threshold_temp_c' => 10.0,
                'cutoff_temp_c' => 31.1,
                'dd_target_first_event' => 250,
                'dd_target_second_event' => 1060,
                'dd_target_third_event' => 2120,
                'event_labels' => json_encode(['3% Egg Hatch', '1st Gen Peak', '2nd Gen Peak']),
                'applicable_months' => json_encode([5, 6, 7, 8, 9]),
                'applicable_altitude_bands' => json_encode(['below_6000', '6000_8000', 'above_8000']),
                'sort_order' => 1,
            ],
            [
                'name_en' => 'San Jose Scale',
                'name_hi' => 'सैन जोसे स्केल',
                'scientific_name' => 'Quadraspidiotus perniciosus',
                'type' => 'insect',
                'threshold_temp_c' => 10.5,
                'cutoff_temp_c' => null,
                'dd_target_first_event' => 405,
                'dd_target_second_event' => 800,
                'dd_target_third_event' => 1200,
                'event_labels' => json_encode(['Crawler Emergence', '1st Gen Crawlers', '2nd Gen Crawlers']),
                'applicable_months' => json_encode([4, 5, 6, 7, 8]),
                'applicable_altitude_bands' => json_encode(['below_6000', '6000_8000', 'above_8000']),
                'sort_order' => 2,
            ],
            [
                'name_en' => 'Woolly Apple Aphid',
                'name_hi' => 'ऊनी सेब माहू',
                'scientific_name' => 'Eriosoma lanigerum',
                'type' => 'insect',
                'threshold_temp_c' => 7.0,
                'cutoff_temp_c' => null,
                'dd_target_first_event' => null,
                'dd_target_second_event' => null,
                'dd_target_third_event' => null,
                'event_labels' => json_encode(['Colony Detection']),
                'applicable_months' => json_encode([4, 5, 6, 7, 8, 9, 10]),
                'applicable_altitude_bands' => json_encode(['below_6000', '6000_8000']),
                'sort_order' => 3,
            ],
        ]);
    }
}
```

---

## ER Diagram (Relationships)

```
user_orchards ||--o{ orchard_blocks : has
user_orchards ||--o{ disease_pressure_log : generates
user_orchards ||--o{ pest_tracker : monitors
user_orchards ||--o{ spray_logs : records
user_orchards ||--o{ weather : tracks

orchard_blocks ||--o{ disease_pressure_log : block-level
orchard_blocks ||--o{ pest_tracker : block-level
orchard_blocks ||--o{ spray_logs : block-level

diseases ||--o{ disease_pressure_log : predicted
pest_models ||--o{ pest_tracker : tracked

users ||--o{ spray_logs : logs
users ||--o{ orchard_blocks : owns

disease_pressure_log ||--o{ notifications : may_trigger
pest_tracker ||--o{ notifications : may_trigger
```

---

## Indexes Summary

| Table | Index | Purpose |
|-------|-------|---------|
| `orchard_blocks` | `user_orchard_id` | Fetch blocks per orchard |
| `orchard_blocks` | `user_id` | Fetch all user's blocks |
| `pest_models` | `is_active, sort_order` | Active list ordering |
| `pest_tracker` | `user_orchard_id, orchard_block_id, pest_model_id, season_year` UNIQUE | One tracker per season |
| `pest_tracker` | `next_event_at_dd, risk_level` | Query upcoming events |
| `disease_pressure_log` | `user_orchard_id, disease_id, prediction_date` | Historical lookup |
| `disease_pressure_log` | `risk_level, prediction_date` | Dashboard aggregations |
| `spray_logs` | `user_orchard_id, spray_date` | Spray history |

---

*Next: Read `02_MODELS.md` to create Eloquent models.*
