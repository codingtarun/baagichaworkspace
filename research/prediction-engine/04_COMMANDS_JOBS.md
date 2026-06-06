# 04 — Artisan Commands & Queued Jobs

> **Copy commands to `app/Console/Commands/` and jobs to `app/Jobs/`**

---

## Command: `ComputeDiseasePressure`

**File:** `app/Console/Commands/ComputeDiseasePressure.php`

```php
<?php

namespace App\Console\Commands;

use App\Models\UserOrchard;
use App\Services\Prediction\DiseasePressureService;
use Carbon\Carbon;
use Illuminate\Console\Command;

class ComputeDiseasePressure extends Command
{
    protected $signature = 'app:compute-disease-pressure
                            {--orchard= : Specific orchard ID}
                            {--date= : Date to compute for (YYYY-MM-DD)}
                            {--blocks : Compute per-block (Phase 2+)}
                            {--dry-run : Show results without saving}';

    protected $description = 'Compute disease pressure predictions for all orchards or a specific one';

    public function handle(DiseasePressureService $service): int
    {
        $date = $this->option('date') ? Carbon::parse($this->option('date')) : now();
        $dryRun = $this->option('dry-run');
        $useBlocks = $this->option('blocks');

        $query = UserOrchard::query();

        if ($this->option('orchard')) {
            $query->where('id', $this->option('orchard'));
        }

        $orchards = $query->where('is_active', true)->get();
        $this->info("Computing disease pressure for {$orchards->count()} orchard(s) on {$date->toDateString()}...");

        $bar = $this->output->createProgressBar($orchards->count());
        $bar->start();

        foreach ($orchards as $orchard) {
            if ($dryRun) {
                $results = $useBlocks
                    ? $service->computeForBlocks($orchard, $date)
                    : [$service->computeForOrchard($orchard, $date)];

                foreach ($results as $result) {
                    if (isset($result['predictions'])) {
                        // Block-level result
                        foreach ($result['predictions'] as $pred) {
                            $this->line("  Block: {$result['block_name']} | {$pred['disease_name']} = {$pred['level']} ({$pred['score']})");
                        }
                    } else {
                        // Orchard-level result
                        foreach ($result as $pred) {
                            $this->line("  {$pred['disease_name']} = {$pred['level']} ({$pred['score']})");
                        }
                    }
                }
            } else {
                if ($useBlocks) {
                    $service->computeForBlocks($orchard, $date);
                } else {
                    $service->computeForOrchard($orchard, $date);
                }
            }
            $bar->advance();
        }

        $bar->finish();
        $this->newLine();
        $this->info('Done.');

        return self::SUCCESS;
    }
}
```

---

## Command: `AccumulatePestDegreeDays`

**File:** `app/Console/Commands/AccumulatePestDegreeDays.php`

```php
<?php

namespace App\Console\Commands;

use App\Services\Prediction\PestDevelopmentService;
use Carbon\Carbon;
use Illuminate\Console\Command;

class AccumulatePestDegreeDays extends Command
{
    protected $signature = 'app:accumulate-pest-dd
                            {--date= : Date to process (YYYY-MM-DD, default: yesterday)}';

    protected $description = 'Accumulate degree-days for all pest trackers';

    public function handle(PestDevelopmentService $service): int
    {
        $date = $this->option('date') ? Carbon::parse($this->option('date')) : now()->subDay();

        $this->info("Accumulating degree-days for {$date->toDateString()}...");

        $service->accumulateDaily($date);

        $this->info('Done.');
        return self::SUCCESS;
    }
}
```

---

## Command: `InitializePestSeason`

**File:** `app/Console/Commands/InitializePestSeason.php`

```php
<?php

namespace App\Console\Commands;

use App\Models\UserOrchard;
use App\Services\Prediction\PestDevelopmentService;
use Illuminate\Console\Command;

class InitializePestSeason extends Command
{
    protected $signature = 'app:initialize-pest-season
                            {--year= : Season year (default: current)}
                            {--orchard= : Specific orchard ID}';

    protected $description = 'Initialize pest trackers for a new growing season';

    public function handle(PestDevelopmentService $service): int
    {
        $year = $this->option('year') ?? now()->year;

        $query = UserOrchard::where('is_active', true);
        if ($this->option('orchard')) {
            $query->where('id', $this->option('orchard'));
        }

        $orchards = $query->get();
        $this->info("Initializing pest season {$year} for {$orchards->count()} orchard(s)...");

        foreach ($orchards as $orchard) {
            $service->initializeSeason($orchard, $year);
            $this->line("  Orchard {$orchard->id}: OK");
        }

        $this->info('Done.');
        return self::SUCCESS;
    }
}
```

---

## Command: `ComputeSprayWindows`

**File:** `app/Console/Commands/ComputeSprayWindows.php`

```php
<?php

namespace App\Console\Commands;

use App\Models\UserOrchard;
use App\Services\Prediction\LeafWetnessEstimator;
use App\Services\Prediction\SprayWindowService;
use Illuminate\Console\Command;

class ComputeSprayWindows extends Command
{
    protected $signature = 'app:compute-spray-windows
                            {--orchard= : Specific orchard ID}';

    protected $description = 'Compute optimal spray windows for all orchards';

    public function handle(SprayWindowService $sprayService, LeafWetnessEstimator $estimator): int
    {
        $query = UserOrchard::where('is_active', true);
        if ($this->option('orchard')) {
            $query->where('id', $this->option('orchard'));
        }

        $orchards = $query->get();
        $this->info("Computing spray windows for {$orchards->count()} orchard(s)...");

        foreach ($orchards as $orchard) {
            $hourly = $estimator->fetchHourlyForecast($orchard);
            $windows = $sprayService->evaluateWindows($hourly);

            $excellent = count(array_filter($windows, fn($w) => $w['rating'] === 'excellent'));
            $this->line("  Orchard {$orchard->id}: {$excellent} excellent window(s) found");
        }

        $this->info('Done.');
        return self::SUCCESS;
    }
}
```

---

## Job: `SendPredictionAlert`

**File:** `app/Jobs/SendPredictionAlert.php`

```php
<?php

namespace App\Jobs;

use App\Models\DiseasePressureLog;
use App\Models\User;
use App\Notifications\DiseaseRiskAlert;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class SendPredictionAlert implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        private int $diseasePressureLogId
    ) {}

    public function handle(): void
    {
        $log = DiseasePressureLog::with(['userOrchard.user', 'disease'])->find($this->diseasePressureLogId);

        if (!$log) return;

        $user = $log->userOrchard->user ?? null;
        if (!$user) return;

        // Only send for medium+ risk
        if (!in_array($log->risk_level, ['medium', 'high', 'critical'])) {
            return;
        }

        // Check deduplication: don't send same alert within 24h
        $recent = DiseasePressureLog::where('user_orchard_id', $log->user_orchard_id)
            ->where('disease_id', $log->disease_id)
            ->where('created_at', '>', now()->subHours(24))
            ->where('id', '!=', $log->id)
            ->exists();

        if ($recent) {
            return;
        }

        $user->notify(new DiseaseRiskAlert($log));
    }
}
```

---

## Job: `ComputePredictionsForUser`

**File:** `app/Jobs/ComputePredictionsForUser.php`

```php
<?php

namespace App\Jobs;

use App\Models\UserOrchard;
use App\Services\Prediction\DiseasePressureService;
use Carbon\Carbon;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ComputePredictionsForUser implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        private int $userOrchardId,
        private ?string $date = null,
    ) {}

    public function handle(DiseasePressureService $service): void
    {
        $orchard = UserOrchard::find($this->userOrchardId);
        if (!$orchard) return;

        $date = $this->date ? Carbon::parse($this->date) : now();
        $results = $service->computeForOrchard($orchard, $date);

        // Queue alerts for high-risk predictions
        foreach ($results as $result) {
            if (in_array($result['level'], ['high', 'critical'])) {
                // Find the log we just created
                $log = \App\Models\DiseasePressureLog::where('user_orchard_id', $orchard->id)
                    ->where('disease_id', $result['disease_id'])
                    ->whereDate('prediction_date', $date->toDateString())
                    ->latest()
                    ->first();

                if ($log) {
                    SendPredictionAlert::dispatch($log->id)->delay(now()->addMinutes(5));
                }
            }
        }
    }
}
```

---

## Scheduler Configuration

**File:** Add to `app/Console/Kernel.php`

```php
<?php

namespace App\Console;

use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Console\Kernel as ConsoleKernel;

class Kernel extends ConsoleKernel
{
    protected function schedule(Schedule $schedule): void
    {
        // ─── EXISTING COMMANDS ──────────────────────────────────
        $schedule->command('app:update-weather-data')->everyFifteenMinutes();
        $schedule->command('app:process-weather-alerts')->dailyAt('06:00');
        $schedule->command('app:send-spray-reminders')->dailyAt('08:00');

        // ─── NEW PREDICTION ENGINE COMMANDS ─────────────────────

        // 5:30 AM: Compute disease pressure for all orchards (before farmer wake-up)
        $schedule->command('app:compute-disease-pressure')->dailyAt('05:30');

        // 6:30 AM: Accumulate pest degree-days (yesterday's weather)
        $schedule->command('app:accumulate-pest-dd')->dailyAt('06:30');

        // 7:00 AM & 7:00 PM: Compute spray windows
        $schedule->command('app:compute-spray-windows')->twiceDaily(7, 19);

        // 1st day of each year: Initialize pest season
        $schedule->command('app:initialize-pest-season')->yearlyOn(1, 1, '00:00');

        // ─── OPTIONAL: Per-orchard queued jobs for scale ─────────
        // If you have many orchards, queue individual jobs instead:
        // foreach (UserOrchard::active()->cursor() as $orchard) {
        //     $schedule->job(new \App\Jobs\ComputePredictionsForUser($orchard->id))->dailyAt('05:30');
        // }
    }

    protected function commands(): void
    {
        $this->load(__DIR__ . '/Commands');
    }
}
```

---

## Queue Configuration

**File:** Add to `.env` or queue config

```bash
# Use database queue for prediction jobs (reliable, no extra deps)
QUEUE_CONNECTION=database

# Run workers:
# php artisan queue:work --queue=default,predictions --sleep=3 --tries=3
```

**File:** `config/queue.php` — add custom queue

```php
'queues' => [
    'default' => 'default',
    'predictions' => 'predictions',   // For prediction computation jobs
    'notifications' => 'notifications', // For alert sending jobs
],
```

---

## Testing Commands Locally

```bash
# Test disease pressure for a specific orchard (dry run)
php artisan app:compute-disease-pressure --orchard=1 --dry-run

# Test with block-level (Phase 2)
php artisan app:compute-disease-pressure --orchard=1 --blocks --dry-run

# Test for a specific date
php artisan app:compute-disease-pressure --date=2026-05-25 --dry-run

# Test pest DD accumulation
php artisan app:accumulate-pest-dd --date=2026-05-20

# Initialize pest season
php artisan app:initialize-pest-season --year=2026

# Test spray windows
php artisan app:compute-spray-windows --orchard=1
```

---

*Next: Read `05_API_CONTROLLERS.md` for REST API endpoints.*
