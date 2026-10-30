#!/usr/bin/env python3
"""Prepare real external before/after restoration examples for the site.

Sources:
  Jacket photos: https://www.releather.com/leather-restoration-jackets-coats
  Bag photos: https://doriabagspa.com/pages/gallery

Both pairs are actual photographs published by third-party ateliers, not
GH-Leather commissions. The site visibly attributes them to the sources.

This build script downloads the real pairs, resizes without stretching, and
stores them locally so visiting the site doesn't contact third parties.
It must never simulate damage, manufacture an 'after' result or invert labels.
"""
from io import BytesIO
from pathlib import Path
import time
import urllib.request

from PIL import Image, ImageOps, ImageStat, ImageChops

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "images"
DEST.mkdir(exist_ok=True)

# ReLeather originals. Cloudinary supplies a larger version of the same assets.
RELEATHER = "https://res.cloudinary.com/releather-com/image/upload/"
RELEATHER_THUMB = ("c_fill,w_300,y_60/ar_1:1,b_rgb:23262f,"
                   "bo_5px_solid_rgb:f8991d,c_fill,g_auto/")
RELEATHER_LARGE = "c_fit,w_1100,q_88/"
JACKET_BASE = "before-after/leather-restoration/jackets/black/"
SOURCES = {
    "jacket": {
        "before": [
            RELEATHER + RELEATHER_LARGE
            + "v1745923661/" + JACKET_BASE + "color-restoration-black-jacket-before.jpg",
            RELEATHER + RELEATHER_THUMB
            + "v1745923661/" + JACKET_BASE + "color-restoration-black-jacket-before.jpg",
        ],
        "after": [
            RELEATHER + RELEATHER_LARGE
            + "v1745923660/" + JACKET_BASE + "color-restoration-black-jacket-after.jpg",
            RELEATHER + RELEATHER_THUMB
            + "v1745923660/" + JACKET_BASE + "color-restoration-black-jacket-after.jpg",
        ],
    },
    "bag": {
        "before": [
            "https://doriabagspa.com/cdn/shop/files/trello4193253841636557036.jpg?v=1772420411&width=1200",
            "https://doriabagspa.com/cdn/shop/files/trello4193253841636557036.jpg?v=1772420411&width=900"
        ],
        "after": [
            "https://doriabagspa.com/cdn/shop/files/trello8582225378991030218.jpg?v=1772420435&width=1200",
            "https://doriabagspa.com/cdn/shop/files/trello8582225378991030218.jpg?v=1772420435&width=900"
        ],
    },
}

ICON_SOURCES = [
    "https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js",
    "https://cdn.jsdelivr.net/npm/lucide@0.468.0/dist/umd/lucide.min.js",
]


def download(url, limit=9000000):
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            })
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError("HTTP " + str(response.status))
                raw = response.read(limit + 1)
            if not 1000 <= len(raw) <= limit:
                raise RuntimeError("Unexpected file size: " + str(len(raw)))
            return raw
        except Exception as e:
            last = e
            if attempt < 2:
                time.sleep(1.2 + attempt)
    raise RuntimeError(f"Failed to retrieve {url.split('?')[0]}: {last}")


def load_image(urls):
    errors = []
    for source in urls:
        try:
            raw = download(source)
            picture = ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert("RGB")
            if min(picture.size) < 250:
                raise RuntimeError("Photo too small: " + repr(picture.size))
            return picture
        except Exception as e:
            errors.append(str(e))
    raise RuntimeError("Photo source failed: " + " | ".join(errors))


def fit_photo(image, canvas=(900, 900)):
    # Separate before/after real photos may differ slightly in framing. They
    # must remain recognizable photos, not warped or AI-manipulated results.
    fitted = ImageOps.contain(image, canvas, method=Image.Resampling.LANCZOS)
    output = Image.new("RGB", canvas, (234, 231, 225))
    output.paste(fitted, ((canvas[0]-fitted.width)//2,
                          (canvas[1]-fitted.height)//2))
    return output


def create_pairs():
    for kind, examples in SOURCES.items():
        previous = None
        for state in ("before", "after"):
            real_photo = load_image(examples[state])
            photo = fit_photo(real_photo)
            target = DEST / f"studio_{kind}_{state}.jpg"
            photo.save(target, "JPEG", quality=89, optimize=True, subsampling=0)
            print(f"Real {kind} {state}: {real_photo.size} -> {photo.size}, {target.stat().st_size} bytes")
            if previous is not None:
                difference = ImageStat.Stat(ImageChops.difference(previous, photo)).mean
                if max(difference) < 2.5:
                    raise RuntimeError(f"{kind} before and after images are identical")
            previous = photo


def build_icons():
    # Site uses local icons; never require clients to fetch third-party scripts.
    local = DEST / "lucide.min.js"
    if local.is_file() and b"createIcons" in local.read_bytes():
        return
    for url in ICON_SOURCES:
        try:
            content = download(url, 1600000)
            if b"createIcons" not in content:
                raise RuntimeError("Unexpected JS bundle")
            local.write_bytes(content)
            print("Local icons: " + str(len(content)) + " bytes")
            return
        except Exception as exc:
            print("Icon source failed: " + str(exc))
    raise RuntimeError("Icon library unavailable; refusing partial build")


if __name__ == "__main__":
    create_pairs()
    build_icons()
