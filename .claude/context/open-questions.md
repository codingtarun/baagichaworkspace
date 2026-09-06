# Open questions — for Tarun

Things the code cannot tell me. Grouped by how much they change what I'd do next.
Answers get folded back into the other context files.

---

## A. Blocking — I would work differently depending on the answer

**A1. What is live right now?**
`.env` points at `baagvaani.com` on Hostinger and there is a real cron config, but the local
database is entirely seeded on one day and `notifications` is empty. Is the site publicly live?
Is the Android app in anyone's hands, or on the Play Store? Are there real users whose data I
could break?

**A2. What is the next milestone?**
`DOCS/milestone/project-milestone.md` describes a "v1 by 1 May" that has passed. Given everything
built since, what is the actual next thing — public web launch, Play Store release, marketplace
go-live, or continued knowledge-base build-out?

**A3. `master` vs `feature/fruit-module`.**
98 commits of work — the Fruit refactor, VarietyStrain, Intelligence, IMD weather, the Disease
rework — exist only on `feature/fruit-module`. `master` is a June snapshot and `origin/HEAD`
still points at it. Do you want me to merge the branch into `master` and make it the default, or
is `master` being kept as a deployed-production line on purpose?

**A4. What do you want me to actually do first?**
"Take over" could mean: stabilise (fix the failures, merge the branch, clean the docs), ship a
specific feature, or audit-and-advise. I have a recommendation in [next-steps](#recommended-first-moves)
below, but this is your call.

---

## B. Product decisions with code consequences

**B1. Hindi UI — is it in scope?**
Content is properly bilingual (`_en`/`_hi` everywhere), but the interface is not: no `lang/`
directory, 7 Blade files use `__()`, `mcamara/laravel-localization` is installed and unused. For
a Hindi-first farmer audience this is a large gap. Is UI translation a real goal, a later phase,
or deliberately dropped because the app is the primary surface?

**B2. Web vs mobile — which is the product?**
The web app has 638 routes and a full public site; the mobile app has 44 screens and is the only
surface for Community (77 backend files, 44 API routes, just 5 Blade views). Where does a new
feature go by default?

**B3. Is the Shop real, or built ahead of demand?**
25 models, Razorpay, GST, invoices, warehouses, vendor onboarding — a serious amount of machinery
for a platform whose revenue plan puts the marketplace in Year 2. Is there a vendor lined up, or
is this parked?

**B4. Prediction engine validation.**
Mills / Maryblyt / DMC / degree-day models are implemented and their own docs say "awaiting
shadow-mode validation". They are producing spray advice with no measured accuracy against
Himalayan conditions. Do you have a validation plan or ground-truth data? This is the highest
product risk in the codebase — wrong spray timing is exactly the harm the product exists to
prevent.

**B5. The 14 BaagvaaniBrain blogs vs 12 `blog_posts` rows.**
Is there a manual copy-paste step from the content repo into the CMS? Should there be an
importer? Are the two sets the same articles?

**B6. Baagicha → Baagvaani rebrand.**
User-facing copy says Baagvaani; the database, repos, RN bundle id, deep-link scheme
(`baagicha://`) and `MAIL_FROM_NAME` still say Baagicha. Do you want that finished, or is the
internal name staying?

---

## C. Technical decisions I want your preference on

**C1. Tailwind or semantic CSS?** (See [known-issues](known-issues.md) #3.)
Right now module Blades carry Tailwind classes that get purged, and 28 hand-written CSS files do
the actual work. Options: (a) add `Modules/**` to `@source` and go Tailwind-first, (b) strip the
Tailwind classes from module views and commit to semantic CSS, (c) leave it and just correct the
guidance. I lean (a) then migrate gradually — but it will change how pages render, so I won't
touch it without you.

**C2. `area_unit` — add `acre`?**
Density is stored per-acre; area cannot be expressed in acres. Add it to the enum plus six
validation sites, or delete the stale test?

**C3. Test strategy.**
404 tests, but Shop, Auth, KnowledgeBase, Core, Community and Blog have none inside the module.
Do you want coverage grown deliberately, or tests only where bugs appear?

**C4. Documentation consolidation.**
There are instruction files for four different AI tools (`.ai/`, `.kimi/` → `.opencode/`,
`.claude/`), and several are actively wrong — `baagichaApp/.opencode/AGENTS.md` most of all.
Should I consolidate onto `CLAUDE.md` + `.claude/` and delete or archive the rest? Do you still
use OpenCode?

**C5. Deployment.**
No CI, no deploy script, manual upload to shared hosting. Want me to set up something minimal
(a deploy script, or GitHub Actions running Pint + tests on push)?

**C6. `.playwright-mcp/` artifacts.**
~200 committed, ~100 untracked, all machine-generated logs and page snapshots. Gitignore and
purge them?

---

## Recommended first moves

If you want a default rather than a decision, this is what I'd do, in order:

1. **Fix the 17 test failures** — 3 root causes, and two of them (#1 Chemical publish crash, #2
   duplicate newsletters) are real user-facing bugs, not test noise. Small, high value.
2. **Merge `feature/fruit-module` → `master`**, repoint `origin/HEAD`, delete the stale backup
   branch. Removes the biggest structural risk.
3. **Fix or delete the misleading docs** — rewrite `baagichaApp/.opencode/AGENTS.md` to match
   Zustand/MMKV/actual tabs, and correct the hero-styling guidance.
4. **Fix the `BaagvaaniBrain` submodule** so the workspace is clonable.
5. *Then* pick a feature, once the ground is stable.

I have done none of this — everything above is analysis only.
