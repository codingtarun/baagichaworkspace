# Product — what Baagvaani is and who it serves

## Identity

**Baagvaani** (formerly / internally **Baagicha**, बागीचा — Hindi for "orchard"). Domain
`baagvaani.com`. Solo side project, one developer.

The rebrand is **incomplete**: `APP_NAME=Baagvaani` and the site chrome say Baagvaani, but the
database is `baagicha`, the repos are `web_baagicha` / `baagichaApp`, the RN app bundle is
`baagichaApp`, and the mail `MAIL_FROM_NAME` still says "Baagicha". Deep links are
`baagicha://`. Treat "Baagicha" in code and "Baagvaani" in user-facing copy as the same thing.

## The user

Apple-growing families in the Indian Himalaya — Himachal Pradesh, Uttarakhand, Jammu & Kashmir.
Roughly 800,000 households. Low digital literacy, Hindi-first, Android-first, patchy connectivity.

## The wedge — altitude

This is the one idea the whole product hangs on, and the reason it is not another Plantix clone.

A grower at 8,700 ft (Narkanda) and one at 1,800 ft (Parwanoo) both grow apples but need spray
timings **14 days apart**, different disease priorities, different varieties, different
rootstocks. Every competitor — Plantix, AgroStar, AgriCentral, Krishify — gives both the same
generic advice.

| Band | Metres | Feet | Belt | Spray offset |
|---|---|---|---|---|
| `below_6000` | < 1,829 | < 6,000 | Solan, Bilaspur, lower Sirmaur | −7 days |
| `6000_8000` | 1,829–2,438 | 6,000–8,000 | Shimla belt, lower Kullu | 0 (standard) |
| `above_8000` | > 2,438 | > 8,000 | Narkanda, Kinnaur, upper Kullu | +14 days |

Band is derived from `altitude_meters` inside the model's `booted()` hook
(`syncAltitudeData()`). **Never assign `altitude_band` by hand.**

Altitude is captured, best source first: GPS pin → Google Elevation API; browser geolocation →
Elevation API; village search → Places → Elevation; IP geolocation (district-level); manual entry.

## Problems it claims to solve

1. Wrong spray timing wastes ₹30,000+/year in chemicals
2. Disease ID is a WhatsApp photo and a neighbour's guess
3. Chemical efficacy is a black box with no peer data
4. Variety and rootstock choice driven by trader advice, not data
5. Input over-application against a ₹55–60/kg production cost
6. No community memory — an outbreak in Kotkhai is unknown in Narkanda until it arrives

## Business model (planned, not built)

Phase 1 free → acquisition. Phase 2 input marketplace commission + premium. Phase 3 B2B and
data services. The Shop and Vendor modules exist and are substantial, so the marketplace is
being built ahead of the audience.

Research lives in `BaagvaaniBrain/research/{market,competitors,revenue-model,prediction-engine}/`.

## Bilingual reality

Content is genuinely bilingual at the **data** layer — every content table carries `_en` / `_hi`
column pairs and models expose `getDisplayName(string $locale)`.

The **interface** is not. There is no `lang/` directory, only 7 Blade files call `__()`, and
`mcamara/laravel-localization` is installed but effectively unused. Navigation, buttons, form
labels, admin — all hardcoded English. A Hindi-first farmer today sees English chrome around
Hindi content. See [open-questions.md](open-questions.md).

## Content operation

`BaagvaaniBrain/` is a separate content business: agronomist-authored `.docx` articles are
transcribed verbatim to HTML, translated to spoken Hindi, given image prompts, and compressed.
**14 blog packages** have been produced there. The local database has **12 published
blog_posts** — whether those are the same 14 and how they get from the repo into the CMS is an
open question; there is no automated import.
