# Danish HTR Synthetic — generation pipeline

Reproducible code that renders 18th-century Danish transcription strings as
degraded handwriting **line images with perfect ground truth**, for
bootstrapping / pre-training historical Handwritten Text Recognition (HTR).

This is the generator for the dataset
[`abhishekjha1008/danish-htr-synthetic`](https://huggingface.co/datasets/abhishekjha1008/danish-htr-synthetic)
(160,000 lines, also on Zenodo, DOI
[10.5281/zenodo.22093255](https://doi.org/10.5281/zenodo.22093255)).

```bash
pip install -r requirements.txt
# 1. put the fonts in place  (see fonts/README.md)
# 2. put the source transcriptions at data/texts.jsonl  (see below)
python generate.py --config config.yaml --out out/
```

Output: `out/images/{train,val,test}/*.jpg` and
`out/synthetic_1700s_manifest.jsonl`.

---

## How a line is made

For every transcription string, line `i` is driven by `random.Random(seed + i)`
so the whole run is deterministic and re-runnable.

1. **Render** (`synthgen/render.py`) — draw the text in black ink on white with
   a randomly-chosen historical font, per-line font size, letter-spacing,
   slant and baseline jitter.
2. **Degrade** (`synthgen/degrade.py`) — apply a randomised capture-degradation
   chain and **record every sampled value**: ink greyness, stroke weight
   (thin/normal/heavy), bleed-through ghost, paper tone, paper texture, blur,
   scan noise, rotation.
3. **Split** (`synthgen/splits.py`) — assign `train`/`val`/`test` by hashing
   the text (stable, no leakage), per the ratios in `config.yaml`.
4. **Write** — the image plus a manifest row that fully describes the line.

Manifest row:

```json
{
  "image_path": "images/train/synthetic_1700s_0000000.jpg",
  "text": "11. Domin. 20 post. Trin: blef Anders Kockis",
  "corpus": "synthetic_1700s", "era_bucket": "1700s", "split": "train",
  "seed": 1700,
  "render": {"font": "Kurrent", "font_style": "kurrent", "font_px": 54,
             "tracking_px": 1.8, "slant": -0.06, "baseline_jitter_px": 3},
  "degradation": {"ink_gray": 21, "stroke_weight": "normal",
                  "bleed_through": {"strength": 6, "dx": -3},
                  "paper_tone": 232, "paper_texture_amp": 5.1,
                  "blur_sigma": 0.7, "noise_std": 4.2, "rotation_deg": -0.8,
                  "height_px": 192}
}
```

Because each line carries its font and degradation parameters, the dataset can
be used as a **controlled diagnostic benchmark** — e.g. measure accuracy vs.
`blur_sigma`, or vs. `stroke_weight`, in isolation.

---

## Source corpora (text)

The text is **not synthetic**. Each string is a real transcription drawn from
openly available eighteenth-century Danish sources — principally **parish
registers (kirkebøger)** and **administrative petition records (supplikker)**.
The transcriptions are the work of the archives and volunteers who produced
them; this dataset re-uses only the text strings, under their open terms, and
credits that upstream transcription effort. Provide them to the generator as
`data/texts.jsonl` (one JSON object per line with a `"text"` field) or a plain
`.txt` file (one transcription per line). The released 160k manifest's `text`
column is exactly this corpus and can be used directly.

### Orthography note (æ / ø / å)

18th-century Danish did **not** use the letter **å** (introduced officially in
1948); the sound was written **aa**, and **ø** was frequently written **ö**.
The pipeline renders the transcription strings **as given in the source** — it
does not normalise or modernise spelling. Any `å`/`ø` present therefore comes
from the source transcription's own editorial conventions, not from the
generator; if a fully period-faithful corpus is required, normalise the text
file before generation (`å→aa`) and the images will follow.

---

## Splits

The original release placed all lines in `train` because the synthetic set was
only ever used as a pre-training / augmentation mix, with final accuracy always
reported on **held-out real documents** (synthetic test accuracy is not a
meaningful target). This pipeline instead writes explicit `train`/`val`/`test`
(default 90/5/5, by text hash) so the manifest and the paper agree. Treat the
synthetic `val`/`test` only as sanity checks, never as the headline metric.

---

## Reproducibility checklist (addresses the JOHD reviews)

- [x] Generation **code** published (this repo) — not just the output.
- [x] **Fonts named** with sources and licences (`fonts/README.md`), and the
      font used is recorded per line.
- [x] **Degradation parameters recorded per line**, so factors can be isolated.
- [x] **Source corpora identified** and the upstream transcription work credited.
- [x] **Splits** made explicit and reproducible (was all-`train`).
- [x] **Deterministic** given the seed; `æ/ø/å` orthography clarified.
- [x] Labels are exact **by construction** — the rendered string is the label;
      note that glyph/diacritic fidelity depends on the chosen font's coverage.

## Licence

Code: MIT. Dataset images: CC-BY 4.0. Fonts: under their respective licences
(see `fonts/README.md`). Source transcriptions: under their original open terms.
