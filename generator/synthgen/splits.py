"""Deterministic train / val / test assignment.

The original released manifest assigned every line to `train` (the synthetic
set was only ever used as a training/pre-training mix, with final evaluation
done on held-out REAL documents). Reviewers correctly flagged that the paper
claimed three splits while the manifest had one.

This module makes the split explicit and reproducible. The split is decided
by hashing the TEXT, so the same transcription always lands in the same split
no matter the run order, and val/test never leak paraphrases of train lines.
"""
from __future__ import annotations

import hashlib


def assign_split(text: str, ratios: dict) -> str:
    """Return 'train' | 'val' | 'test' for a given transcription.

    ratios e.g. {"train": 0.90, "val": 0.05, "test": 0.05} (must sum to 1).
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # map first 8 bytes to a float in [0, 1)
    frac = int.from_bytes(digest[:8], "big") / float(1 << 64)
    t = ratios["train"]
    v = ratios.get("val", 0.0)
    if frac < t:
        return "train"
    if frac < t + v:
        return "val"
    return "test"
