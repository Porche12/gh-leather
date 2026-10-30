#!/usr/bin/env python3
"""Build visually worn sample photos FROM the exact same post-restoration photo.

These are illustrative simulations, not evidence of completed atelier work.
Generated images are deployed as static assets on PythonAnywhere.
"""
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = ROOT / "images"

ITEMS = {
    "jacket": {
        "source": "jacket_after.jpg",
        "target": "demo_jacket_before.jpg",
        "seed": 41731,
        "areas": [
            [(0.00, 0.11), (0.27, 0.12), (0.43, 0.41), (0.32, 0.65), (0.32, 1.0), (0.0, 1.0)],
            [(0.72, 0.10), (1.0, 0.10), (1.0, 1.0), (0.75, 1.0), (0.61, 0.55)],
            [(0.40, 0.19), (0.67, 0.19), (0.74, 0.56), (0.68, 1.0), (0.37, 1.0), (0.30, 0.56)]
        ],
        "exclude": [(0.15, 0.54, 0.68, 0.82), (0.55, 0.54, 0.94, 0.82),
                    (0.27, 0.00, 0.78, 0.17)],
        "scuff_color": (182, 161, 142),
    },
    "bag": {
        "source": "bag_after.jpg",
        "target": "demo_bag_before.jpg",
        "seed": 41732,
        "areas": [
            [(0.04, 0.43), (0.92, 0.43), (0.94, 0.95), (0.03, 0.95)],
            [(0.16, 0.26), (0.34, 0.26), (0.40, 0.58), (0.22, 0.58)],
            [(0.52, 0.27), (0.74, 0.26), (0.80, 0.57), (0.59, 0.57)]
        ],
        "exclude": [],
        "scuff_color": (116, 104, 88),
    },
}


def make_mask(size, item):
    width, height = size
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    for polygon in item["areas"]:
        d.polygon([(round(x * width), round(y * height)) for x, y in polygon], fill=255)
    for x0, y0, x1, y1 in item["exclude"]:
        d.ellipse((int(x0 * width), int(y0 * height),
                   int(x1 * width), int(y1 * height)), fill=0)
    return mask.filter(ImageFilter.GaussianBlur(radius=max(2, width // 145)))


def generate(kind, item):
    path = IMAGE_DIR / item["source"]
    if not path.is_file():
        raise FileNotFoundError(path)
    original = Image.open(path).convert("RGB")
    width, height = original.size
    rnd = random.Random(item["seed"])
    mask = make_mask(original.size, item)

    faded = ImageEnhance.Color(original).enhance(0.59 if kind == "jacket" else 0.75)
    faded = ImageEnhance.Contrast(faded).enhance(0.85)
    faded = ImageEnhance.Brightness(faded).enhance(0.84 if kind == "jacket" else 0.90)
    worn = Image.composite(faded, original, mask)

    # Patchy abrasion on actual leather, not on hands, backdrop or hardware.
    patches = Image.new("RGBA", original.size, (0, 0, 0, 0))
    patches_draw = ImageDraw.Draw(patches)
    for _ in range(max(95, width * height // 900)):
        x = rnd.randrange(width)
        y = rnd.randrange(height)
        if mask.getpixel((x, y)) < 100:
            continue
        r = rnd.randint(3, max(5, width // 14))
        color = item["scuff_color"]
        opacity = rnd.randint(11, 38)
        patches_draw.ellipse((x-r, y-r//2, x+r, y+r//2),
                             fill=(*color, opacity))
    patches = patches.filter(ImageFilter.GaussianBlur(radius=max(2, width // 90)))
    patches_alpha = ImageChops.multiply(patches.getchannel("A"), mask)
    patches.putalpha(patches_alpha)
    worn = Image.alpha_composite(worn.convert("RGBA"), patches)

    # Fine irregular scuffs, sparse short lines and wear at stress points.
    abrasions = Image.new("RGBA", original.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(abrasions)
    for _ in range(max(180, width * height // 410)):
        x, y = rnd.randrange(width), rnd.randrange(height)
        if mask.getpixel((x, y)) < 140:
            continue
        length = rnd.randint(max(3,width//95), max(9,width//24))
        dx = rnd.choice([-1, 1]) * length
        dy = rnd.randint(-length//3, length//3)
        base_color = item["scuff_color"]
        alpha = rnd.randint(24, 100) if kind == "jacket" else rnd.randint(18, 67)
        points = [(x,y), (x+dx//2, y+dy//3), (x+dx,y+dy)]
        d.line(points, fill=(*base_color, alpha), width=rnd.choice([1,1,1,2]))
    a = ImageChops.multiply(abrasions.getchannel("A"), mask)
    abrasions.putalpha(a)
    worn = Image.alpha_composite(worn, abrasions).convert("RGB")
    target = IMAGE_DIR / item["target"]
    worn.save(target, format="JPEG", quality=91, subsampling=0, optimize=True)
    print(f"Built {target.relative_to(ROOT)} from {path.name} ({width}x{height})")


if __name__ == "__main__":
    for kind, item in ITEMS.items():
        generate(kind, item)
