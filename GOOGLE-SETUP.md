# Move Baagvaani's Google (and Expo) setup to the official account

For Tarun, written 22 Nov 2026. You do these steps yourself: they need your logins, and some ask for a card.
Tick each box as you go. Where a step gives you something to **send Claude**, it is never a secret;
**secrets** (keys, passwords, the client secret) stay in files on your PC and the servers, never in git or chat.

In this guide **"the official Gmail"** = Baagvaani's own Gmail (you said *bagwani@gmail.com*; check the exact spelling
before you start). **"Old account"** = coding.tarun@gmail.com.

## What uses Google today, and where it moves

| Piece | Used for | Today | After |
|---|---|---|---|
| Firebase project | Push notifications on Android (FCM) | `baagichaapp` (the old app's project), old account | New project **Baagvaani**, official Gmail |
| FCM V1 key (service account) | Lets Expo send through Firebase | Old project, uploaded to Expo | New key from the new project |
| Expo account + project | Push service the server talks to; builds | Owner `coding.tarun` (app.json `owner`) | Official account (organisation `baagvaani`) |
| Google Maps key | The orchard map in the app | Old account's Cloud project | New key in the new project |
| Google login (OAuth) | "Continue with Google", app + website | Not made yet | New project (plan: `baagicha_php/plans/google-login-plan.md`) |
| Google Analytics 4 | Website visits (`G-LFDEBYBMZS`) | Old account | Official Gmail made Administrator |
| Search Console | Google search for baagvaani.com | Unknown | Official Gmail, domain verified |
| Play Console | Publishing the app | Not made yet | Official Gmail |

## Free or paid? (checked 22 Nov 2026; prices change, so look again before paying)

| Service | Cost for us | Notes |
|---|---|---|
| **Firebase** (project, Cloud Messaging = push) | **Free** | The free "Spark" plan; push messages have no charge and no monthly limit. |
| **Expo** (account, push service) | **Free** | Push through Expo costs nothing. We build the app on this PC, so Expo's paid cloud builds aren't needed. |
| **Google login** (OAuth, "Continue with Google") | **Free** | No charge per sign-in, any number of users. |
| **Google Cloud billing account** | **Free to have** | Only needed so Maps can be turned on; you pay only for paid use. The budget alert (step 1) warns you early. |
| **Google Maps SDK for Android** (the orchard map) | **Free** for app maps | Google's billing page says mobile use of the Maps SDK for Android is unlimited (Street View, which we don't use, is paid). Keep the key restricted to the app (step 6) so nobody else can use it on our bill. |
| **Google Analytics 4** | **Free** | |
| **Search Console** | **Free** | |
| **Google Business Profile** | **Free** | Optional. |
| **Google Play Console** | **US$25 once** (about ₹2,100) | A one-time fee, no yearly fee. If Plus is ever sold inside the app through Play Billing, Google keeps a share of each sale (15% on the first US$1 million a year). |
| **D-U-N-S number** (for a Play *organisation* account) | **Free** | From Dun & Bradstreet; can take days to a few weeks. |
| **Open-Meteo** (weather, not Google) | **Paid for commercial use** | The free API is for non-commercial use, under 10,000 calls a day. Open-Meteo's own announcement lists **Standard US$29 / month** (1 million calls) and Professional US$99 / month (5 million). Standard is plenty for us. |
| **Hostinger** (website + API) | Already paid | |
| **Razorpay** (later, with the shop) | No fixed fee | About 2% of each payment. |
| **SMS codes** (later) | Paid | A few paise per SMS, plus the one-time DLT registration. |

**Total to start:** US$25 once for Play, plus about US$29 a month for Open-Meteo. Everything Google besides Play
stays free at our size.

**Test and live use the same Google project.** One app (`com.baagvaani.baagicha`) and one Firebase project serve
both servers: a phone gets its push from whichever server it is logged in to. Google login lists both web addresses.
(A separate test project would need a second app name; not worth it now.)

**What will break for a moment:** after the switch, phones need the new build and must turn alerts on again (old push
tokens belong to the old Firebase project). Fine during the beta. Keep the old setup running until step 8 is done.

---

## Step 0. Prepare the official Gmail (10 minutes)

- [ ] Log in to the official Gmail in Chrome, ideally in **its own Chrome profile** (Chrome → profile icon → Add),
      so the old and the official accounts never mix.
- [ ] Google Account → Security: turn on **2-Step Verification**; add a recovery phone and recovery email (your
      personal one is fine). Losing this account would lose the app's push, login and Play listing.
- [ ] Make a folder for secrets **outside every project**, e.g. `D:\GoogleDrive\Baagicha\keys\`. Back it up (USB + private
      cloud drive) together with `baagicha_mobile/credentials/` (the app's signing key).

## Step 1. Google Cloud billing (5 minutes, needs a card)

Google Maps needs a billing account, even inside the free amount.

- [ ] <https://console.cloud.google.com> (official Gmail) → Billing → **Create account** → country India, your card.
- [ ] Billing → Budgets & alerts → **Create budget**, e.g. ₹500 a month, alerts at 50 / 90 / 100 %.

## Step 2. Firebase project for push (15 minutes)

- [ ] <https://console.firebase.google.com> → **Create a project** → name **Baagvaani** →
      Google Analytics: **off** (we can turn it on later) → Create.
      This also makes the Google Cloud project that steps 5–6 use.
- [ ] Project page → **Add app → Android**:
      package **`com.baagvaani.baagicha`** · nickname Baagvaani · SHA-1: leave empty → Register app.
- [ ] **Download `google-services.json`**. Skip Firebase's "Add SDK" steps (Expo does that).
- [ ] Save it as `D:\Apps\UnnatDigital\BaagichaWorkspace\baagicha_mobile\google-services.json`, **replacing** the
      old one (rename the old one to `google-services.old.json` first, in case you need to go back).
      It is git-ignored. `.env.local` already points to it (`GOOGLE_SERVICES_JSON=./google-services.json`).
- [ ] ⚙️ Project settings → **Cloud Messaging**: check that "Firebase Cloud Messaging API (V1)" says **Enabled**.
- [ ] ⚙️ Project settings → **Service accounts** → **Generate new private key** → save the JSON as
      `D:\GoogleDrive\Baagicha\keys\fcm-service-account.json`. **Secret.**

## Step 3. Expo on the official account (15 minutes)

- [ ] <https://expo.dev/signup> with the official Gmail (a new Expo account, e.g. user `baagvaani`).
- [ ] In it: **Create organization** `baagvaani` (lets you add your personal account later as a member).
- [ ] Move the project there. Log in to expo.dev with the **old** account → project **baagicha** → Settings →
      look for **Transfer project** → transfer to the `baagvaani` organisation.
  - If transfer works: the project id (`0664debe-…`) stays the same. **Send Claude:** "transferred".
  - If there is no transfer: in a terminal, `cd baagicha_mobile`, `npx eas-cli logout`, `npx eas-cli login`
    (official account), then **send Claude** that, so Claude changes `app.json` (`owner`, project id) and you run
    `npx eas-cli init`; put the new id in `.env.local` `EAS_PROJECT_ID=`.
- [ ] expo.dev → project → **Credentials → Android** → application identifier `com.baagvaani.baagicha` →
      **FCM V1 service account key** → upload `D:\GoogleDrive\Baagicha\keys\fcm-service-account.json`
      (remove the old key there if one is listed).
- [ ] (Recommended) expo.dev → account settings → **Access tokens** → Create, name "push from servers" →
      save it in `D:\GoogleDrive\Baagicha\keys\expo-token.txt`. **Secret.** Claude will add a git-ignored server setting for it;
      then turn on "Enhanced security for push notifications" in the project's settings, so only our servers can push.

## Step 4. Rebuild and test push (test server first, then live)

Phone on USB (Claude asks before touching it).

- [ ] Uninstall the old app from the phone (new push setup).
- [ ] ```powershell
      cd D:\Apps\UnnatDigital\BaagichaWorkspace\baagicha_mobile
      ```
      ```powershell
      npx expo prebuild --platform android --clean
      ```
      ```powershell
      npx expo run:android
      ```
- [ ] In the app: Account → Server → **test server** → log in (a test phone) → My Orchard → an orchard →
      Turn on alerts → Allow.
- [ ] test.bhatko.com/admin → Alerts → Phones: your phone is listed → **Send me a test alert** → it arrives.
- [ ] Account → Server → **live** → log in → turn on alerts → baagvaani.com/admin → Alerts → **Send me a test alert**.
- [ ] Realme: phone Settings → Apps → Baagvaani → Autostart on, Battery → No restrictions.
- [ ] If something fails, the table at the end of `baagicha_mobile/PUSH-SETUP.md` explains each error
      (`MismatchSenderId` = the build still has the old `google-services.json`).

## Step 5. Google login (OAuth) — 30 minutes

Same project as step 2. **Needs the real privacy and terms pages first** (Google asks for their addresses);
until they exist, do 5a–5b and leave the rest.

- [ ] 5a. <https://console.cloud.google.com> → top bar: choose project **Baagvaani** → menu **Google Auth Platform**
      → **Get started**: app name **Baagvaani**, support email **hello@baagvaani.com** (or the official Gmail),
      audience **External**, contact email → Create.
- [ ] 5b. **Data access → Add or remove scopes**: only `openid`, `.../auth/userinfo.email`,
      `.../auth/userinfo.profile`. (No Google review needed for these.)
- [ ] 5c. **Branding**: logo (square 120×120 PNG), home page `https://baagvaani.com`,
      privacy `https://baagvaani.com/privacy`, terms `https://baagvaani.com/terms`,
      authorised domains `baagvaani.com` and `bhatko.com`.
- [ ] 5d. **Clients → Create client → Web application**, name "Baagvaani website":
  - Authorised JavaScript origins: `https://baagvaani.com` · `https://test.bhatko.com` · `http://localhost:8000`
  - Authorised redirect URIs: `https://baagvaani.com/auth/google/callback` ·
    `https://test.bhatko.com/auth/google/callback` · `http://localhost:8000/auth/google/callback`
  - Create → **Download JSON** → `D:\GoogleDrive\Baagicha\keys\oauth-web-client.json`. **Secret** (it holds the client secret).
  - **Send Claude:** the **Client ID** (ends in `.apps.googleusercontent.com`).
- [ ] 5e. **Create client → Android**, "Baagvaani app (debug)": package `com.baagvaani.baagicha`,
      SHA-1 `5E:8F:16:06:2E:A3:CD:2C:4A:0D:54:78:76:BA:A6:F3:8C:AB:F6:25`.
- [ ] 5f. **Create client → Android**, "Baagvaani app (release)": same package,
      SHA-1 `85:EC:6F:0E:A2:CB:FD:A1:85:F7:0E:66:E8:43:95:98:8B:82:AB:EE`.
- [ ] 5g. **Audience → Publish app** (status "In production"). If Google asks to verify the branding, submit it the
      same day: it can take a few days.
- [ ] 5h. When Claude has made `config/google.example.php`: copy it to `config/google.php` (this PC),
      `config/servers/staging/google.php` and the live server's `config/servers/production/google.php`, and paste
      the client secret into each yourself.

## Step 6. Google Maps key (10 minutes)

- [ ] Cloud console (project Baagvaani) → APIs & Services → Library → **Maps SDK for Android** → Enable.
- [ ] Credentials → **Create credentials → API key** → edit it, name "Android maps":
  - Application restrictions: **Android apps** → add `com.baagvaani.baagicha` with the debug SHA-1 (5e) and the
    release SHA-1 (5f).
  - API restrictions: **Maps SDK for Android** only → Save.
- [ ] Put the key in `baagicha_mobile/.env.local` after `GOOGLE_MAPS_ANDROID_API_KEY=` (replace the old one), rebuild
      (step 4 commands), open My Orchard → Add orchard: the map must show.
- [ ] Firebase made an "Android key (auto created by Firebase)" too: restrict it the same way
      (Android apps → package + both SHA-1s). Leave its API list as Firebase set it.

## Step 7. Accounts around the app (when you are ready to publish)

- [ ] **Play Console** <https://play.google.com/console> with the official Gmail: developer account, US$25 once,
      identity check. **Choose carefully:** *Organisation* (needs a D-U-N-S number for Unnat Digital, free but takes
      days) skips the "12 testers for 14 days" rule; *Personal* needs that test before you can publish.
- [ ] After the first upload: Play Console → app → Test and release → **App integrity** → copy the **App signing key
      SHA-1** → add it (a) as a third Android OAuth client "Baagvaani app (Play)" (like 5e) and (b) to the Maps key
      (step 6). Without it, Google login and the map fail only in the app installed from Play.
- [ ] **Google Analytics:** <https://analytics.google.com> with the **old** account → Admin → Account access
      management → add the official Gmail as **Administrator**. Then log in as the official Gmail and check you see
      the property. (The `G-LFDEBYBMZS` id doesn't change; nothing to do on the website.)
- [ ] **Search Console:** <https://search.google.com/search-console> (official Gmail) → Add property → **Domain**
      `baagvaani.com` → copy the TXT record → Hostinger hPanel → DNS → add the TXT record → Verify.
      Then Sitemaps → add `https://baagvaani.com/sitemap.xml`.
- [ ] (Optional, for growers who search on Maps) **Google Business Profile** for Baagvaani.

## Step 8. Switch off the old setup (2 weeks after everything works)

- [ ] Old Firebase project `baagichaapp`: it also holds the **old app** (`com.baagichaapp`). If the old app is no
      longer used, delete the project; otherwise only remove `com.baagvaani.baagicha` from it.
- [ ] Old Maps key in the old account's Cloud project: delete it.
- [ ] Old FCM key: Firebase (old project) → Service accounts → delete the key; delete the old JSON from your PC.
- [ ] Expo: if a new project was made in step 3, delete the old one under `coding.tarun`.
- [ ] Analytics: remove the old account from the property only if you want to (Administrator access can stay).

---

## What to send Claude, and when

| After step | Send | Claude then |
|---|---|---|
| 2 | "Firebase done" (nothing else; the file is on your PC) | — |
| 3 | "transferred" or "new Expo project, id …" | Updates `app.json` if needed; adds the git-ignored server setting for the Expo token |
| 4 | Did the test alert arrive on test and live? | Fixes anything that failed |
| 5d | The Web **Client ID** | Makes `config/google.example.php`; starts the Google login work once you have said who writes what |
| 6 | "map works" | Updates `RUN-ON-ANDROID.md` and `PUSH-SETUP.md` (new project names, official account) |
| 7 | Play account type; the Play signing SHA-1 | Updates the launch plan dates |

## Not Google, but on the same list for a smooth launch

- **Open-Meteo** (weather): a paid API key for commercial use, then `config/engine.php` `api_key` on both servers.
- **Hostinger cron jobs** (hPanel): check `/admin/cron` on live shows every job on time (alerts depend on it).
- **Email:** hello@baagvaani.com already sends over SMTP; use it as the support address everywhere above.
- **Razorpay:** later, with the shop (live keys + webhook), on the official business details.
