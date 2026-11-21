# Ink sketches: which image is which

The 20 images ChatGPT made from `baagicha_php/docs/illustrations/chatgpt-prompts.md` (made 2026-11-21), matched by
looking at each picture, not only at its file name. `download.webp` is the **original reference** (the two growers
picking apples), not a new image.

The **web name** is the name each image should get when it goes into the site (`public/images/ink/`, as WebP).

## Page headers (breadcrumb hero)

| # | File | Prompt | Page | Web name | What is in it | Notes |
|---|---|---|---|---|---|---|
| 1 | `Himalayan Orchard Harvest Conversation.png` | 4.1 Fruits | `/fruits` | `hero-fruits.webp` | A woman with a basket of mixed fruit talks to an older man holding a pear; plum, apple, kiwi pergola and other fruit trees on the terraces, stone-step path | Good |
| 2 | `Apple Harvest in the Himalayan Orchard.png` | 4.2 Varieties | `/variety-strain` | `hero-varieties.webp` | Two growers at a wooden table comparing rows of apples of different shapes (conical, round, flat), cartons and crates | Good |
| 3 | `Himalayan Orchard Planting in Winter.png` | 4.3 Rootstocks | `/rootstock` | `hero-rootstocks.webp` | Winter: a grower plants a bare-root plant in a pit beside staked high-density rows on posts and wire; old bare seedling tree behind; second grower carries stakes | Good |
| 4 | `Himalayan Orchard Leaf Inspection.png` | 4.4 Diseases & pests | `/disease` | `hero-diseases.webp` | A man looks at an apple leaf through a hand lens, a woman checks the leaves beside him; a sticky trap card hangs from a branch | Good (the lens is with the man, not the woman: fine) |
| 5 | `Himalayan Orchard Mixing Scene.png` | 4.5 Chemicals | `/chemical` | `hero-chemicals.webp` | A grower in mask and gloves reads a bottle; another pours a measured amount into a drum; plain bottles, sachets, measuring jug on the wall | Good, no writing on any bottle or sachet (checked zoomed in) |
| 6 | `Terraced Orchard Blossom Spraying.png` | 4.6 Spray schedule | `/spray-schedule` | `hero-spray.webp` | A grower in a mask sprays blossoming trees with a spray gun; hose to a power sprayer and drum, where a second grower stands | Good. The second grower stands about 25–35 % from the left, a little into the text area |
| 7 | `Himalayan Orchard Companions.png` | 4.7 Blog | `/blog` | `hero-blog.webp` | An older grower reads a book and a young grower reads his phone, sitting on a stone wall under an apple tree, tea glass between them, valley with houses behind | Good |
| 8 | `Himalayan Orchard Family Gathering.png` | 4.8 About | `/about` | `hero-about.webp` | A kath-kuni house with a carved balcony and slate roof; a family (grandfather, mother, child) looks at a tablet a young man is showing; apple crates by the wall | Good, tablet screen has no writing |
| 9 | `Himalayan Orchard Weather Watch.png` | 4.9 Weather | `/weather` | `hero-weather.webp` | Clouds and rain lines over the peaks, anti-hail net on poles over the trees, a grower looks at the sky holding his phone, rain gauge and wind vane beside him | Good. The grower stands at about 23–30 % from the left, inside the text area |
| 10 | `Himachal Orchard Blossom Harvest.png` | 4.10 Plus | `/plus` | `hero-plus.webp` | A grower in a blossoming high-density block looks at his phone, smiling; power sprayer and drum ready, house on the terrace above | Good (file name says "harvest", but it is the Plus scene in bloom) |
| 11 | `Family Harvest Under the Apple Tree.png` | 4.11 App / beta | `/app` | `hero-app.webp` | A young grower shows his phone to his grandfather; grandmother looks over their shoulders; basket and carton of apples | Good, phone screen dark, no writing |
| 12a | `Welcoming Orchard Gate in the Mountains-2.png` | 4.12 Login / register | `/login`, `/register` | `hero-login.webp` | The open wooden gate in a stone wall, steps up into the orchard, the grower **faces the visitor** and waves | **Recommended** of the two: he greets the person arriving |
| 12b | `Welcoming Gate to the Mountain Orchard-1.png` | 4.12 Login / register | (spare) | — | The same gate; the grower walks away up the steps and **looks back** over his shoulder, waving | Spare. Use it if you prefer, or delete it |

## Footer

| # | File | Prompt | Place | Web name | What is in it | Notes |
|---|---|---|---|---|---|---|
| 13 | `Apple Terraces Beneath Mountain Peaks.png` | 5 Footer | Bottom of every page | `footer.webp` | A long, light panorama: terraced orchard rows, deodar trees, two slate-roofed houses, crates, one small grower with a basket, faint peaks | Already wide (2172×724, 3 : 1). The drawing is only in the lower part, so it can be cropped to a low strip. Replaces `footer-orchard-silhouette.webp` |

## Home page sections

| # | File | Prompt | Place | Web name | What is in it | Notes |
|---|---|---|---|---|---|---|
| 14 | `Terraced Orchard with Sapling and Tools.png` | 6.1 Grow & protect | Home, behind the "Grow & protect" cards | `home-grow.webp` | A young apple tree on a stake, a watering can and a spade on the right; a faint line of terraces along the bottom | Good: very light, the left and top are empty for the cards |
| 15 | `Apple Orchard Dashboard Sketch.png` | 6.2 App section | Home, "Take Baagvaani Everywhere" | `home-app.webp` | A hand holding a phone showing a simple chart (bars, pie, lines), an apple branch with blossoms and fruit around it, a valley behind | Square (1254×1254). Screen has shapes only, no writing |

## Empty states and error pages

| # | File | Prompt | Place | Web name | What is in it | Notes |
|---|---|---|---|---|---|---|
| 16 | `Orchard Crate and Fallen Apple.png` | 7.1 Nothing found | Empty search results and empty lists | `empty-nothing.webp` | An empty wooden crate with two leaves inside, an apple beside it, a branch above | Good |
| 17 | `Forked Paths Through the Himalayan Orchard.png` | 7.2 Page not found | `errors/page.twig` (404) | `empty-404.webp` | A grower scratching his head at a blank two-arm signpost where the stone path forks | Good, signpost is blank |
| 18 | `Seedling Pot with Orchard Hills.png` | 7.3 Coming soon | Coming-soon pages | `empty-soon.webp` | A seedling with two leaves in a clay pot, a trowel leaning on it, orchard hills behind | Good |
| 19 | `Rustic Orchard Gate Among Apple Trees.png` | 7.4 No access / log in | 403 page, "log in to see this" | `empty-locked.webp` | A closed wooden gate in a stone wall, apple trees behind | Good |

All 19 prompts have an image; the login scene has two versions (12a, 12b).

## What I checked on every image

| Check | Result |
|---|---|
| One ink colour, no colour fills | Yes, all navy line work on cream |
| Background | Flat cream from `#F6EEE3` to `#FAF2E7` (the site's page colour is `#F5F0E8`): close, slightly lighter. Will be matched exactly when converting to WebP |
| No writing | None found, including zoomed checks of the bottles, sachets, measuring jug, cartons, tablet and phones |
| Faces and clothes | Kullu topi caps, pattu shawls, salwar kameez with headscarves; the same young curly-haired grower appears in many scenes, which ties the set together |
| Edges | No frames; scenes fade into the cream |

## Website copies (`web/` folder)

The originals above are kept untouched. `web/convert.py` makes the website copies in `web/`: WebP, quality 70
(the same to the eye as 80 on this line art, checked zoomed in), the cream shifted to the site's exact `#F5F0E8`,
never enlarged. Run it again after replacing an original: `python ink-sktech/web/convert.py`.

Each image comes in a few widths, named `<web name>-<width>.webp`; the page lists them in `srcset` so each screen
downloads only the one it needs.

| Kind | Widths | Size of one image | Used for |
|---|---|---|---|
| Headers `hero-*` (13 incl. `hero-login-alt`) | 1200 · 800 · 480 (3 : 2) | about 180 / 90 / 33 KB | 1200 sharp desktop screens, 800 phones and normal desktops, 480 small phones |
| Footer `footer` | 1920 · 1280 · 768 (3 : 1) | 59 / 29 / 11 KB | Full page width |
| Home `home-grow` | 1200 · 800 · 480 (3 : 2) | 53 / 25 / 9 KB | Behind the "Grow & protect" cards |
| Home `home-app` | 800 · 480 (square) | 117 / 47 KB | The app section, shown about 320–400 px |
| Empty states `empty-*` (4) | 640 · 320 (square) | about 50 / 12 KB | Small pictures about 280 px wide |

56 files, 4.0 MB in all (a visitor only ever downloads one size per picture).

## Two things to know before they go on the site

1. **The empty space on the left is about 25 %, not 40 %.** In every header the drawing starts about a quarter of the
   way in. A short title fits, but a long heading would run into the drawing (Spray schedule and Weather have a
   person at about 25–30 %). Plan: the header keeps its text in the left column and the picture is anchored to the
   right, so the drawing never sits under the text.
2. **The trees reach the top edge.** The prompts asked for the scene in the lower two-thirds, but ChatGPT filled
   the full height. Cropping the headers to a 2.5 : 1 strip would cut the tree tops. Plan: show each header image
   **whole** (3 : 2) on the right side of a taller header instead of cropping it. If you want very short headers
   instead, ask ChatGPT for each: *"Extend this image upward and to the left with more empty cream sky, keep
   everything else identical."*
