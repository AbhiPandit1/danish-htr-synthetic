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
the **DiEm HTR dataset** (*Digitalisering af Enesteministerialbøger*) — the
volunteer-verified transcriptions of Danish **parish registers (kirkebøger)**
released by the Danish National Archives (Rigsarkivet) under CC BY 4.0
(https://huggingface.co/datasets/RA-Data-Science/DiEm_HTR). This dataset re-uses
only the text strings, under that licence, and credits that upstream
transcription effort. Provenance is verifiable: of the 36,056 unique strings in
this repo's `manifest.jsonl`, 39% are verbatim DiEm transcription lines and 71%
appear verbatim within a DiEm page, with 99% of word tokens in the DiEm
vocabulary. The generator reads this repo's `manifest.jsonl` (field `"text"`)
directly, or any `.txt` file with one transcription per line.

### Orthography note (æ / ø / å)

Eighteenth-century Danish wrote the sound later spelled **å** as **aa** (22% of
lines here); the modern letter **å** (official only from 1948) occurs in just
8 of 160,000 lines (0.005%), where the source transcription itself uses a
modernised spelling. The pipeline renders strings **as given in the source** and
does not modernise spelling. For a specific convention, set `normalize` in
`config.yaml` (for example `normalize: {"å": "aa"}`); it is off by default.

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
