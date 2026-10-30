#!/usr/bin/env python3
"""Generate studio before/after demo pairs. No visitor data is ever used.

Photographs: Pexels free-to-use photography; these simulations are NOT
photographs of actual GH-Leather orders. Both sides of each pair are derived
from one and the same photograph, so zipper, grain and perspective align.
Also vendors the icon library locally to avoid browser requests to unpkg.
"""
from io import BytesIO
from pathlib import Path
import random
import time
import urllib.request

from PIL import Image, ImageEnhance, ImageDraw, ImageFilter, ImageOps, ImageChops

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "images"
DEST.mkdir(exist_ok=True)
SOURCES = {
    "jacket": (
        "https://images.pexels.com/photos/16341730/pexels-photo-16341730.jpeg?auto=compress&cs=tinysrgb&w=1200",
        167103, (162, 135, 106),
    ),
    "bag": (
        "https://images.pexels.com/photos/26903899/pexels-photo-26903899.jpeg?auto=compress&cs=tinysrgb&w=1200",
        167104, (159, 149, 138),
    ),
}
ICON_SOURCES = [
    "https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js",
    "https://cdn.jsdelivr.net/npm/lucide@0.468.0/dist/umd/lucide.min.js",
]


def download(url, max_bytes=8000000):
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; GHLeatherSiteBuilder/1.0)",
                "Accept": "image/jpeg,image/*;q=0.9,*/*;q=0.5",
            })
            with urllib.request.urlopen(req, timeout=35) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                data = resp.read(max_bytes + 1)
            if len(data) < 1000 or len(data) > max_bytes:
                raise RuntimeError("Unexpected asset size")
            return data
        except Exception as error:
            last_error = error
            if attempt != 2:
                time.sleep(1 + attempt)
    raise RuntimeError(f"Asset download failed ({url.split('?')[0]}): {last_error}")


def build_icons():
    for url in ICON_SOURCES:
        try:
            content = download(url, 1600000)
            if b"createIcons" not in content:
                raise RuntimeError("Unexpected icon library")
            path = DEST / "lucide.min.js"
            path.write_bytes(content)
            print(f"Local icon library: {len(content)} bytes")
            return
        except Exception as exc:
            print("Icon CDN attempt failed:", str(exc))
    raise RuntimeError("Unable to install local icons; refusing incomplete deployment.")


def make_wear_mask(img, kind):
    w, h = img.size
    # Isolate dark foreground product from light backdrop; keep metal and
    # studio background unchanged. Blur edges so ageing is not cut sharply.
    grey = img.convert("L").filter(ImageFilter.GaussianBlur(2))
    threshold = (144 if kind == "jacket" else 151)
    mask = grey.point(lambda v: 250 if v < threshold else (60 if v < threshold + 24 else 0))
    bounds = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(bounds)
    if kind == "jacket":
        d.ellipse((int(w*.05), int(h*.12), int(w*.95), int(h*.98)),fill=255)
    else:
        d.ellipse((int(w*.09), int(h*.16), int(w*.92), int(h*.94)),fill=255)
    return ImageChops.multiply(mask,bounds).filter(ImageFilter.GaussianBlur(max(2,w//220)))


def make_worn(after, kind, seed, shade):
    rnd = random.Random(seed)
    w,h = after.size
    mask = make_wear_mask(after,kind)
    # Subtle overall fading, rather than painting the whole image gray.
    faded = ImageEnhance.Brightness(after).enhance(.87 if kind=="jacket" else .9)
    faded = ImageEnhance.Color(faded).enhance(.49 if kind=="jacket" else .57)
    faded = ImageEnhance.Contrast(faded).enhance(.78)
    result = Image.composite(faded,after,mask)
    damage=Image.new("RGBA",(w,h),(0,0,0,0))
    painter=ImageDraw.Draw(damage)
    # Irregular worn patches: narrow translucent streaks grouped over areas
    # of frequent handling; no sharp procedural spirals or giant fake cracks.
    zones = ([(.32,.34,.16,.10),(.72,.47,.13,.16),(.29,.78,.16,.11),(.76,.81,.12,.13)]
             if kind=="jacket" else
             [(.23,.73,.13,.13),(.77,.73,.14,.13),(.37,.45,.17,.12),(.71,.38,.14,.10)])
    for cx,cy,sx,sy in zones:
        for _ in range(150):
            x = int((cx + rnd.gauss(0,sx/2))*w)
            y = int((cy + rnd.gauss(0,sy/2))*h)
            if not(0<=x<w and 0<=y<h) or mask.getpixel((x,y))<70:
                continue
            rw=rnd.randint(max(1,w//350),max(3,w//60))
            rh=rnd.randint(1,max(2,h//250))
            painter.ellipse((x-rw,y-rh,x+rw,y+rh),
                            fill=(*shade,rnd.randint(16,64)))
    for _ in range(int(w*h/700)):
        x,y=rnd.randrange(w),rnd.randrange(h)
        if mask.getpixel((x,y))<125:continue
        ln=rnd.randint(4,max(8,w//25))
        alpha=rnd.randint(35,135)
        dx=rnd.choice([-1,1])*ln
        painter.line([(x,y),(x+dx//2,y+rnd.randint(-2,2)),(x+dx,y+rnd.randint(-4,4))],
                    fill=(*shade,alpha),width=rnd.randint(1,2))
    alpha=ImageChops.multiply(damage.getchannel("A"),mask)
    damage.putalpha(alpha)
    return Image.alpha_composite(result.convert("RGBA"),damage).convert("RGB")


def build_pair(kind,url,seed,shade):
    raw=download(url)
    image=ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert("RGB")
    if min(image.size)<400:
        raise RuntimeError(f"Source photo too small for {kind}: {image.size}")
    image.thumbnail((1080,1200),Image.Resampling.LANCZOS)
    photo=DEST/f"studio_{kind}_after.jpg"
    worn=DEST/f"studio_{kind}_before.jpg"
    image.save(photo,"JPEG",quality=88,subsampling=0,optimize=True)
    make_worn(image,kind,seed,shade).save(worn,"JPEG",quality=88,subsampling=0,optimize=True)
    if image.size != Image.open(worn).size:
        raise RuntimeError(f"Unaligned photo pair: {kind}")
    print(f"Generated {kind}: {image.size}, two images of the SAME item.")
    print(f"  After: {photo.stat().st_size} bytes; Before: {worn.stat().st_size} bytes")


if __name__=="__main__":
    for kind,(url,seed,shade) in SOURCES.items():
        build_pair(kind,url,seed,shade)
    build_icons()
