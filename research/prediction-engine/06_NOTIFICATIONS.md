# 06 — Push Notifications

> **Copy notification class to `app/Notifications/`**

---

## `DiseaseRiskAlert.php`

**File:** `app/Notifications/DiseaseRiskAlert.php`

```php
<?php

namespace App\Notifications;

use App\Models\DiseasePressureLog;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;
use NotificationChannels\Fcm\FcmChannel;
use NotificationChannels\Fcm\FcmMessage;
use NotificationChannels\Fcm\Resources\AndroidConfig;
use NotificationChannels\Fcm\Resources\AndroidFcmOptions;
use NotificationChannels\Fcm\Resources\AndroidNotification;
use NotificationChannels\Fcm\Resources\ApnsConfig;
use NotificationChannels\Fcm\Resources\ApnsFcmOptions;

class DiseaseRiskAlert extends Notification
{
    use Queueable;

    public function __construct(private DiseasePressureLog $log) {}

    public function via($notifiable): array
    {
        return [FcmChannel::class, 'database'];
    }

    public function toFcm($notifiable): FcmMessage
    {
        $title = $this->getTitle();
        $body = $this->getBody();
        $bodyHi = $this->getBodyHi();

        return (new FcmMessage(notification: new \NotificationChannels\Fcm\Resources\Notification(
            title: $title,
            body: $body,
        )))
            ->data([
                'type' => 'disease_alert',
                'log_id' => (string) $this->log->id,
                'disease_id' => (string) $this->log->disease_id,
                'disease_name' => $this->log->disease->name,
                'disease_name_hi' => $this->log->disease->name_hi,
                'risk_level' => $this->log->risk_level,
                'risk_score' => (string) $this->log->risk_score,
                'prediction_date' => $this->log->prediction_date->toDateString(),
                'action_needed' => $this->log->risk_level === 'high' || $this->log->risk_level === 'critical' ? 'true' : 'false',
                'screen' => 'AlertDetailScreen',
                'screen_params' => json_encode([
                    'logId' => $this->log->id,
                    'diseaseId' => $this->log->disease_id,
                ]),
            ])
            ->android(
                AndroidConfig::create()
                    ->fcmOptions(AndroidFcmOptions::create()->analyticsLabel('disease_alert'))
                    ->notification(
                        AndroidNotification::create()
                            ->channelId('disease_alerts')
                            ->priority('high')
                            ->sound('default')
                    )
            )
            ->apns(
                ApnsConfig::create()
                    ->fcmOptions(ApnsFcmOptions::create()->analyticsLabel('disease_alert'))
                    ->payload(['aps' => ['sound' => 'default', 'badge' => 1]])
            );
    }

    public function toDatabase($notifiable): array
    {
        return [
            'type' => 'disease_alert',
            'log_id' => $this->log->id,
            'disease_id' => $this->log->disease_id,
            'disease_name' => $this->log->disease->name,
            'disease_name_hi' => $this->log->disease->name_hi,
            'risk_level' => $this->log->risk_level,
            'risk_score' => $this->log->risk_score,
            'prediction_date' => $this->log->prediction_date->toDateString(),
            'message' => $this->getBody(),
            'message_hi' => $this->getBodyHi(),
            'action_needed' => $this->log->risk_level === 'high' || $this->log->risk_level === 'critical',
        ];
    }

    private function getTitle(): string
    {
        $disease = $this->log->disease->name;
        return match ($this->log->risk_level) {
            'critical' => "🚨 {$disease} — CRITICAL",
            'high' => "⚠️ {$disease} — HIGH RISK",
            'medium' => "👁️ {$disease} — Watch",
            default => "ℹ️ {$disease}",
        };
    }

    private function getBody(): string
    {
        $disease = $this->log->disease->name;
        return match ($this->log->risk_level) {
            'critical' => "{$disease} infection is almost certain. Spray immediately!",
            'high' => "{$disease} risk is high. Spray within 24 hours.",
            'medium' => "{$disease} risk building. Prepare spray materials.",
            default => "{$disease} conditions are favorable. Monitor closely.",
        };
    }

    private function getBodyHi(): string
    {
        $disease = $this->log->disease->name_hi ?? $this->log->disease->name;
        return match ($this->log->risk_level) {
            'critical' => "{$disease} का संक्रमण लगभग तय है। तुरंत स्प्रे करें!",
            'high' => "{$disease} का जोखिम उच्च है। 24 घंटे के भीतर स्प्रे करें।",
            'medium' => "{$disease} का जोखिम बढ़ रहा है। स्प्रे सामग्री तैयार रखें।",
            default => "{$disease} के लिए परिस्थितियाँ अनुकूल हैं। नज़दीकी निगरानी करें।",
        };
    }
}
```

---

## `PestAlertNotification.php`

**File:** `app/Notifications/PestAlertNotification.php`

```php
<?php

namespace App\Notifications;

use App\Models\PestTracker;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Notification;
use NotificationChannels\Fcm\FcmChannel;
use NotificationChannels\Fcm\FcmMessage;
use NotificationChannels\Fcm\Resources\AndroidConfig;
use NotificationChannels\Fcm\Resources\AndroidFcmOptions;
use NotificationChannels\Fcm\Resources\AndroidNotification;
use NotificationChannels\Fcm\Resources\ApnsConfig;
use NotificationChannels\Fcm\Resources\ApnsFcmOptions;

class PestAlertNotification extends Notification
{
    use Queueable;

    public function __construct(private PestTracker $tracker) {}

    public function via($notifiable): array
    {
        return [FcmChannel::class, 'database'];
    }

    public function toFcm($notifiable): FcmMessage
    {
        $pest = $this->tracker->pestModel;
        $nextEvent = (new \App\Services\Prediction\Models\Pests\DegreeDayModel())
            ->getNextEvent($pest, $this->tracker->cumulative_dd);

        $title = "🐛 {$pest->name_en} — {$this->tracker->risk_level} risk";
        $body = $nextEvent
            ? "{$nextEvent['name']} expected in ~{$nextEvent['dd_remaining']} DD. Prepare to spray."
            : "Pest development tracked. Check app for details.";

        return (new FcmMessage(notification: new \NotificationChannels\Fcm\Resources\Notification(
            title: $title,
            body: $body,
        )))
            ->data([
                'type' => 'pest_alert',
                'tracker_id' => (string) $this->tracker->id,
                'pest_id' => (string) $pest->id,
                'pest_name' => $pest->name_en,
                'pest_name_hi' => $pest->name_hi,
                'risk_level' => $this->tracker->risk_level,
                'cumulative_dd' => (string) $this->tracker->cumulative_dd,
                'screen' => 'PestTrackerScreen',
                'screen_params' => json_encode([
                    'trackerId' => $this->tracker->id,
                    'pestId' => $pest->id,
                ]),
            ])
            ->android(
                AndroidConfig::create()
                    ->fcmOptions(AndroidFcmOptions::create()->analyticsLabel('pest_alert'))
                    ->notification(AndroidNotification::create()->channelId('pest_alerts')->sound('default'))
            )
            ->apns(
                ApnsConfig::create()
                    ->fcmOptions(ApnsFcmOptions::create()->analyticsLabel('pest_alert'))
                    ->payload(['aps' => ['sound' => 'default']])
            );
    }

    public function toDatabase($notifiable): array
    {
        $pest = $this->tracker->pestModel;

        return [
            'type' => 'pest_alert',
            'tracker_id' => $this->tracker->id,
            'pest_id' => $pest->id,
            'pest_name' => $pest->name_en,
            'pest_name_hi' => $pest->name_hi,
            'risk_level' => $this->tracker->risk_level,
            'cumulative_dd' => $this->tracker->cumulative_dd,
            'last_event' => $this->tracker->last_event_triggered,
        ];
    }
}
```

---

## Notification Channel Setup

**File:** Add to existing push notification config

```php
// config/fcm.php or wherever your FCM config lives

// Notification channels for disease alerts
'disease_alerts' => [
    'channel_id' => 'disease_alerts',
    'channel_name' => 'Disease Risk Alerts',
    'channel_description' => 'Critical disease risk predictions for your orchard',
    'importance' => 'high',
    'sound' => 'default',
    'vibration' => true,
],

'pest_alerts' => [
    'channel_id' => 'pest_alerts',
    'channel_name' => 'Pest Development Alerts',
    'channel_description' => 'Pest lifecycle tracking and spray timing alerts',
    'importance' => 'default',
    'sound' => 'default',
],
```

---

## Deduplication Rules

| Alert Type | Cooldown | Logic |
|------------|----------|-------|
| Disease HIGH/CRITICAL | 24 hours | Same disease + same orchard |
| Disease MEDIUM | 72 hours | Same disease + same orchard |
| Pest event | 48 hours | Same pest + same orchard |
| Spray window | Daily at 7 AM | One per orchard per day |

Implement in `SendPredictionAlert` job and `PestAlertNotification`.

---

## Notification Deep Linking (Mobile)

When user taps notification:

| Type | Screen | Params |
|------|--------|--------|
| `disease_alert` | `AlertDetailScreen` | `{ logId, diseaseId }` |
| `pest_alert` | `PestTrackerScreen` | `{ trackerId, pestId }` |
| `spray_reminder` | `SprayScheduleScreen` | `{ stageId }` |

---

*Next: Read `07_MOBILE_INTEGRATION.md` for React Native types and screens.*
