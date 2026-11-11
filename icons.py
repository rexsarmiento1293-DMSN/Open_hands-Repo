# -*- coding: utf-8 -*-
"""Per-app themed icon generator.

Each app gets a unique icon: a vibrant gradient tile matching the app's own
emoji (movie -> film reel, ulam -> frying pan, ...). Emoji artwork comes from
Twemoji (CC-BY 4.0) and is rasterised with cairosvg, then cached locally.
"""
import os, math, hashlib, urllib.request
from PIL import Image, ImageDraw

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".iconcache")
os.makedirs(CACHE, exist_ok=True)

PALETTES = [
    ("#6a11cb", "#2575fc"), ("#ee0979", "#ff6a00"), ("#00c9a7", "#0072ff"),
    ("#f7971e", "#ffd200"), ("#c31432", "#ff4e50"), ("#396afc", "#2948ff"),
    ("#11998e", "#38ef7d"), ("#7f00ff", "#e100ff"), ("#f953c6", "#b91d73"),
    ("#43cea2", "#185a9d"), ("#ff512f", "#dd2476"), ("#1fa2ff", "#12d8fa"),
    ("#00b09b", "#96c93d"), ("#fc466b", "#3f5efb"), ("#2b5876", "#4e4376"),
    ("#f12711", "#f5af19"), ("#8e2de2", "#4a00e0"), ("#0f9b0f", "#a8e063"),
    ("#e52d27", "#b31217"), ("#134e5e", "#71b280"),
]


def _hex(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def palette_for(name):
    h = int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16)
    return PALETTES[h % len(PALETTES)]


def _codepoint(emoji):
    return "-".join("%x" % ord(ch) for ch in emoji if ch != "\ufe0f")


def emoji_png(emoji, size):
    """Return a PIL RGBA image of the emoji, fetched from Twemoji (cached)."""
    cp = _codepoint(emoji)
    svg_path = os.path.join(CACHE, cp + ".svg")
    if not os.path.exists(svg_path):
        url = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/svg/%s.svg" % cp
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read()
            with open(svg_path, "wb") as f:
                f.write(data)
        except Exception:
            return None
    try:
        import cairosvg, io
        png = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
        return Image.open(io.BytesIO(png)).convert("RGBA")
    except Exception:
        return None


def _rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def themed_icon(path, size, emoji, name):
    """Build a unique gradient icon tile featuring the app's emoji."""
    c1, c2 = palette_for(name)
    base = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(base)
    a, b = _hex(c1), _hex(c2)
    for y in range(size):                       # diagonal-ish vertical gradient
        d.line([(0, y), (size, y)], fill=_lerp(a, b, y / max(1, size - 1)))
    # glass sheen (soft highlight in the upper-left)
    sheen = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.ellipse([-size * 0.35, -size * 0.55, size * 0.85, size * 0.5],
               fill=(255, 255, 255, 46))
    base = Image.alpha_composite(base.convert("RGBA"), sheen)

    em = emoji_png(emoji, int(size * 0.66)) if emoji else None
    if em is not None:
        off = (size - em.width) // 2
        base.alpha_composite(em, (off, int(size * 0.17)))
    else:                                       # fallback: initial letter
        try:
            from PIL import ImageFont
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                   int(size * 0.5))
            t = (name[:1] or "?").upper()
            bb = d.textbbox((0, 0), t, font=f)
            d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]),
                   t, font=f, fill="#ffffff")
        except Exception:
            pass

    base.putalpha(_rounded_mask(size, int(size * 0.22)))
    base.save(path)
