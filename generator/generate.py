#!/usr/bin/env python3
"""Generate the Danish HTR synthetic line dataset.

    python generate.py --config config.yaml --out out/ [--n 160000]

For each transcription in the corpus it:
  1. renders a clean handwriting line with a randomly-chosen historical font,
  2. applies and RECORDS realistic capture degradation,
  3. assigns a deterministic train/val/test split by text hash,
  4. writes the image and a rich manifest row.

The run is fully deterministic given the seed: line i is driven by
`Random(seed + i)`, so re-running reproduces the dataset bit-for-bit, and the
manifest fully describes how every line was made (font, degradation values,
split). This is the reproducible generation pipeline that the released
160,000-line dataset documents.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import yaml
from PIL import ImageFont

from synthgen.corpus import load_lines
from synthgen.degrade import degrade
from synthgen.render import render_line
from synthgen.splits import assign_split


def resolve_fonts(cfg: dict, root: Path) -> list[dict]:
    fonts = []
    for f in cfg["fonts"]:
        path = (root / f["path"]).resolve()
        if not path.exists():
            raise SystemExit(
                f"Missing font file: {path}\n"
                f"Download the fonts listed in fonts/README.md and place them "
                f"under {root / 'fonts'}/ before generating."
            )
        # fail fast if the font cannot be opened
        ImageFont.truetype(str(path), 32)
        fonts.append({"name": f["name"], "style": f["style"], "path": str(path)})
    return fonts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--out", default="out")
    ap.add_argument("--n", type=int, default=0, help="limit (0 = all corpus lines)")
    ap.add_argument("--seed", type=int, default=None, help="override config seed")
    args = ap.parse_args()

    root = Path(args.config).resolve().parent
    cfg = yaml.safe_load(Path(args.config).read_text())
    seed = args.seed if args.seed is not None else cfg["seed"]

    fonts = resolve_fonts(cfg, root)
    texts = load_lines(root / cfg["corpus"])
    if args.n:
        texts = texts[: args.n]
    print(f"corpus: {len(texts)} lines | fonts: {[f['name'] for f in fonts]}")

    out = Path(args.out)
    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)

    manifest = (out / f"{cfg['corpus_tag']}_manifest.jsonl").open("w", encoding="utf-8")
    counts = {"train": 0, "val": 0, "test": 0}

    for i, text in enumerate(texts):
        rng = random.Random(seed + i)          # deterministic per line
        split = assign_split(text, cfg["splits"])

        clean, render_meta = render_line(text, fonts, rng)
        img, degrade_meta = degrade(clean, rng, cfg["degradation"], cfg["target_height"])

        name = f"{cfg['corpus_tag']}_{i:07d}.jpg"
        rel = f"images/{split}/{name}"
        img.save(out / rel, "JPEG", quality=88)

        manifest.write(json.dumps({
            "image_path": rel,
            "text": text,
            "corpus": cfg["corpus_tag"],
            "era_bucket": cfg["era_bucket"],
            "split": split,
            "seed": seed + i,
            "render": render_meta,
            "degradation": degrade_meta,
        }, ensure_ascii=False) + "\n")

        counts[split] += 1
        if (i + 1) % 2000 == 0:
            manifest.flush()
            print(f"{i + 1}/{len(texts)}  {counts}")

    manifest.close()
    print(f"DONE  {sum(counts.values())} lines  splits={counts}")


if __name__ == "__main__":
    main()
