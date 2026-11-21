"""
Make the website copies of the ink sketches.

Reads the original PNGs in ink-sktech/ (never changes them) and writes resized WebP files
into ink-sktech/web/, one file per width, named <web name>-<width>.webp. While resizing it
shifts each picture's cream background to the site's page colour (#F5F0E8), so the drawings
sit on the page without a visible box.

    python ink-sktech/web/convert.py
"""

from pathlib import Path

from PIL import Image, ImageStat

HERE = Path(__file__).resolve().parent
ORIGINALS = HERE.parent
PAGE_CREAM = (0xF5, 0xF0, 0xE8)
QUALITY = 70  # the same to the eye as 80 on this line art (checked zoomed in), about 18 % smaller

# Original file -> (web name, widths to make). See ../image-map.md for which page uses which.
HERO = (1200, 800, 480)  # headers sit at about 600 px on desktop: 1200 for sharp screens, 800 for phones
SQUARE_SMALL = (640, 320)
IMAGES = {
    'Himalayan Orchard Harvest Conversation.png': ('hero-fruits', HERO),
    'Apple Harvest in the Himalayan Orchard.png': ('hero-varieties', HERO),
    'Himalayan Orchard Planting in Winter.png': ('hero-rootstocks', HERO),
    'Himalayan Orchard Leaf Inspection.png': ('hero-diseases', HERO),
    'Himalayan Orchard Mixing Scene.png': ('hero-chemicals', HERO),
    'Terraced Orchard Blossom Spraying.png': ('hero-spray', HERO),
    'Himalayan Orchard Companions.png': ('hero-blog', HERO),
    'Himalayan Orchard Family Gathering.png': ('hero-about', HERO),
    'Himalayan Orchard Weather Watch.png': ('hero-weather', HERO),
    'Himachal Orchard Blossom Harvest.png': ('hero-plus', HERO),
    'Family Harvest Under the Apple Tree.png': ('hero-app', HERO),
    'Welcoming Orchard Gate in the Mountains-2.png': ('hero-login', HERO),
    'Welcoming Gate to the Mountain Orchard-1.png': ('hero-login-alt', HERO),
    'Apple Terraces Beneath Mountain Peaks.png': ('footer', (1920, 1280, 768)),
    'Terraced Orchard with Sapling and Tools.png': ('home-grow', HERO),
    'Apple Orchard Dashboard Sketch.png': ('home-app', (800, 480)),
    'Orchard Crate and Fallen Apple.png': ('empty-nothing', SQUARE_SMALL),
    'Forked Paths Through the Himalayan Orchard.png': ('empty-404', SQUARE_SMALL),
    'Seedling Pot with Orchard Hills.png': ('empty-soon', SQUARE_SMALL),
    'Rustic Orchard Gate Among Apple Trees.png': ('empty-locked', SQUARE_SMALL),
}


def background(image):
    """The cream: the median colour of the four corners (always empty paper)."""
    w, h = image.size
    boxes = [(0, 0, 40, 40), (w - 40, 0, w, 40), (0, h - 40, 40, h), (w - 40, h - 40, w, h)]
    medians = [ImageStat.Stat(image.crop(box)).median for box in boxes]
    return tuple(sum(m[c] for m in medians) / 4 for c in range(3))


def match_cream(image):
    """Scale each colour channel so the background becomes exactly PAGE_CREAM.

    A multiplication: the cream moves fully, the dark ink lines hardly change.
    """
    bg = background(image)
    channels = [
        band.point(lambda v, f=PAGE_CREAM[c] / bg[c]: min(255, round(v * f)))
        for c, band in enumerate(image.split())
    ]
    return Image.merge('RGB', channels)


def main():
    total = 0
    for name, (web_name, widths) in IMAGES.items():
        original = Image.open(ORIGINALS / name).convert('RGB')
        fixed = match_cream(original)
        for width in widths:
            width = min(width, original.width)  # never enlarge
            height = round(original.height * width / original.width)
            out = HERE / f'{web_name}-{width}.webp'
            fixed.resize((width, height), Image.LANCZOS).save(out, 'WEBP', quality=QUALITY, method=6)
            size = out.stat().st_size
            total += size
            print(f'{out.name:28} {width}x{height:<5} {size / 1024:6.0f} KB')
    print(f'\n{total / 1024 / 1024:.1f} MB in all')


if __name__ == '__main__':
    main()
