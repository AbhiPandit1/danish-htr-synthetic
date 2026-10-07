"""Apply realistic capture degradation to a clean line image.

Each factor is applied with a probability and a parameter sampled per line,
and EVERY sampled value is returned in the metadata. This is the key fix for
the reviewer point that the released manifest did not let users isolate
individual degradation factors (stroke weight, blur, bleed-through, ...):
here each line records exactly which factors were applied and with what
strength, so the dataset can be used as a controlled diagnostic benchmark.

Factors, in order:
  1. ink_gray       - ink is rarely pure black; darkest ink level
  2. stroke_weight  - thin/heavy pen (morphological erode/dilate of ink)
  3. bleed_through  - faint mirrored ghost of the text (show-through)
  4. paper_tone     - background paper colour (aged, off-white)
  5. paper_texture  - low-frequency mottling of the paper
  6. blur_sigma     - soft focus / ink spread
  7. noise_std      - sensor / scan grain
  8. rotation_deg   - small skew from imperfect scanning
"""
from __future__ import annotations

import random

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def degrade(
    clean: Image.Image,
    rng: random.Random,
    cfg: dict,
    target_h: int,
) -> tuple[Image.Image, dict]:
    """Return (degraded "L" image resized to target_h, metadata)."""
    meta: dict = {}
    img = clean  # clean = dark ink (0) on white (255)

    # 1. ink is not pure black
    ink_gray = rng.randint(*cfg["ink_gray"])
    img = img.point(lambda v: min(255, v + ink_gray))
    meta["ink_gray"] = ink_gray

    # 2. stroke weight: erode (thin) or dilate (heavy) the ink
    sw = rng.choice([-1, 0, 0, 1])  # bias towards unchanged
    if sw == 1:
        img = img.filter(ImageFilter.MinFilter(3))   # darker/thicker ink
    elif sw == -1:
        img = img.filter(ImageFilter.MaxFilter(3))   # thinner ink
    meta["stroke_weight"] = {-1: "thin", 0: "normal", 1: "heavy"}[sw]

    # 3. bleed-through: faint mirrored ghost behind the writing
    bleed = rng.random() < cfg["bleed_through_prob"]
    if bleed:
        ghost_strength = rng.randint(4, 8)  # higher = fainter
        ghost = ImageOps.mirror(img).point(lambda v: 255 - (255 - v) // ghost_strength)
        dx = rng.randint(-6, 6)
        shifted = Image_offset(ghost, dx)
        img = Image.fromarray(np.minimum(np.asarray(img), np.asarray(shifted)))
        meta["bleed_through"] = {"strength": ghost_strength, "dx": dx}
    else:
        meta["bleed_through"] = None

    # 4. + 5. paper tone and low-frequency texture
    tone = rng.randint(*cfg["paper_tone"])
    arr = np.asarray(img).astype(np.float32)
    # put ink onto a toned paper: paper where there is no ink
    paper = np.full_like(arr, tone)
    texture_amp = rng.uniform(*cfg["paper_texture_amp"])
    paper = _mottle(paper, rng, texture_amp)
    # composite: min keeps the darker of ink vs paper
    arr = np.minimum(arr * (tone / 255.0), paper)
    meta["paper_tone"] = tone
    meta["paper_texture_amp"] = round(texture_amp, 2)

    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    # 6. blur
    blur_sigma = round(rng.uniform(*cfg["blur_sigma"]), 2)
    if blur_sigma > 0.05:
        img = img.filter(ImageFilter.GaussianBlur(blur_sigma))
    meta["blur_sigma"] = blur_sigma

    # 7. gaussian scan noise
    noise_std = round(rng.uniform(*cfg["noise_std"]), 2)
    if noise_std > 0.1:
        a = np.asarray(img).astype(np.float32)
        a += np.asarray(_rng_normal(rng, a.shape, noise_std))
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    meta["noise_std"] = noise_std

    # 8. small rotation
    rot = round(rng.uniform(*cfg["rotation_deg"]), 2)
    if abs(rot) > 0.05:
        img = img.rotate(rot, resample=Image.BILINEAR, expand=True, fillcolor=tone)
    meta["rotation_deg"] = rot

    # normalise line height
    if img.height != target_h:
        w = max(1, round(img.width * target_h / img.height))
        img = img.resize((w, target_h), Image.LANCZOS)
    meta["height_px"] = target_h

    return img, meta


def Image_offset(img: Image.Image, dx: int) -> Image.Image:
    """Horizontal pixel shift, filling the gap with white (255)."""
    out = Image.new("L", img.size, 255)
    out.paste(img, (dx, 0))
    return out


def _mottle(paper: np.ndarray, rng: random.Random, amp: float) -> np.ndarray:
    """Add smooth low-frequency variation to the paper background."""
    h, w = paper.shape
    small = np.asarray(_rng_normal(rng, (max(1, h // 24), max(1, w // 24)), amp))
    field = np.asarray(
        Image.fromarray(small).resize((w, h), Image.BILINEAR)
    )
    return paper + field


def _rng_normal(rng: random.Random, shape, std: float):
    """Deterministic gaussian noise from a python Random (no global numpy seed)."""
    n = int(np.prod(shape))
    flat = [rng.gauss(0.0, std) for _ in range(n)]
    return np.array(flat, dtype=np.float32).reshape(shape)
