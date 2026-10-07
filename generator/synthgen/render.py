"""Render one transcription string as a clean handwriting line.

Clean = black ink on a white canvas, no degradation yet. Degradation is a
separate, independently-recorded step (see degrade.py) so a user can reason
about each factor on its own.

Every random choice here is driven by a per-line `random.Random` instance so
the whole pipeline is deterministic given a seed, and every choice is
returned in the metadata dict so the line is fully described.
"""
from __future__ import annotations

import random

from PIL import Image, ImageFont

# Vertical padding above/below the glyph band, as a fraction of font size.
_PAD_FRAC = 0.35


def render_line(
    text: str,
    fonts: list[dict],
    rng: random.Random,
) -> tuple[Image.Image, dict]:
    """Render `text` with a randomly chosen font.

    `fonts` is the resolved font table from config: a list of dicts with
    keys {name, style, path, font (loaded ImageFont at a base size)}.

    Returns (grayscale "L" image, metadata). Metadata records the exact
    font, style, pixel size, letter-spacing and slant used.
    """
    choice = rng.choice(fonts)
    size = rng.randint(38, 72)
    font = ImageFont.truetype(choice["path"], size)

    # Per-line calligraphic variation.
    tracking = rng.uniform(-0.04, 0.10) * size  # extra px between glyphs
    slant = rng.uniform(-0.18, 0.12)            # horizontal shear (radians-ish)
    baseline_jitter = max(1, int(size * 0.06))  # vertical wobble per glyph

    # --- measure total width with tracking ---
    ascent, descent = font.getmetrics()
    glyph_h = ascent + descent
    pad = int(glyph_h * _PAD_FRAC)
    widths = [font.getbbox(ch)[2] + tracking for ch in text]
    total_w = int(sum(widths)) + 2 * pad
    height = glyph_h + 2 * pad

    canvas = Image.new("L", (max(total_w, 10), height), 255)

    # --- draw glyph by glyph so tracking + baseline jitter apply ---
    x = float(pad)
    for ch, w in zip(text, widths):
        glyph = Image.new("L", (max(1, int(w) + size), height), 255)
        from PIL import ImageDraw

        ImageDraw.Draw(glyph).text((0, pad), ch, font=font, fill=0)
        dy = rng.randint(-baseline_jitter, baseline_jitter)
        canvas.paste(_shear(glyph, slant), (int(x), dy), _ink_mask(glyph, slant))
        x += w

    # Trim to the actual ink bounding box, then re-pad uniformly.
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    canvas = _pad(canvas, pad)

    meta = {
        "font": choice["name"],
        "font_style": choice["style"],
        "font_px": size,
        "tracking_px": round(tracking, 2),
        "slant": round(slant, 3),
        "baseline_jitter_px": baseline_jitter,
    }
    return canvas, meta


def _shear(img: Image.Image, slant: float) -> Image.Image:
    if abs(slant) < 1e-3:
        return img
    w, h = img.size
    return img.transform(
        (w + int(abs(slant) * h), h),
        Image.AFFINE,
        (1, slant, 0 if slant > 0 else slant * h, 0, 1, 0),
        resample=Image.BILINEAR,
        fillcolor=255,
    )


def _ink_mask(img: Image.Image, slant: float) -> Image.Image:
    # Paste mask = where there is ink (dark). Invert so dark -> opaque.
    from PIL import ImageOps

    sheared = _shear(img, slant)
    return ImageOps.invert(sheared)


def _pad(img: Image.Image, pad: int) -> Image.Image:
    w, h = img.size
    out = Image.new("L", (w + 2 * pad, h + 2 * pad), 255)
    out.paste(img, (pad, pad))
    return out
