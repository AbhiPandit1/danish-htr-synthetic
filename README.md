# Danish HTR Synthetic Lines (18th-century style)

**160,000 synthetic text-line images with exact ground truth**, generated to support handwritten text recognition (HTR) of 18th-century Danish administrative and parish records.

- **Author:** Abhishek Jha (224abhishekjha@gmail.com)
- **License:** CC-BY 4.0
- **Volume:** 160,000 lines / approximately 2.5 GB of JPEG line images
- **Language:** Danish (18th-century orthography)
- **Script:** Gothic cursive (kurrent) and copperplate-style hands, rendered from historical-style fonts
- **Period emulated:** ~1700-1800
- **Full data (DOI):** https://doi.org/10.5281/zenodo.22093255 ; this repository holds the manifest, samples, and documentation

## What this is

Real ground truth for 18th-century Danish handwriting is scarce and expensive to produce. This set provides unlimited perfectly-labelled training lines by rendering genuine 18th-century Danish text (names, dates, parish-record phrasing) through historical-style handwriting fonts with realistic degradation:

- paper texture and tone variation
- contrast and stroke-weight variation
- blur and noise
- simulated bleed-through from the reverse page

Each line image comes with its exact source text, so the label error rate is zero by construction.

In our own experiments the set was used **alongside real data** (never alone) when training CTC recognisers for 18th-century Danish, as an augmentation source for low-resource eras.

## Format

```
synthetic_1700s.tar     # 160,000 JPEG line images (Zenodo)
manifest.jsonl          # one JSON object per line (this repo)
samples/                # 60 random example images
```

Each manifest row:

```json
{"image_path": "synthetic_1700s/0_synth_000000.jpg",
 "text": "11. Domin. 20 post. Trin: blef Anders Kockis",
 "corpus": "synthetic_1700s",
 "era_bucket": "1700s",
 "split": "train"}
```

Splits are provided (train/val/test) for reproducibility, though for augmentation use the whole set is typically folded into training.

## Source text

The rendered strings are drawn from public 18th-century Danish transcription corpora (parish registers and administrative records), preserving authentic orthography, abbreviations (Dom:, Trin:, u: c:), personal and place names, and record phrasing. The text is reshuffled at line level; no source document can be reconstructed from this set.

## Known characteristics (read before use)

1. **Diacritic fidelity varies by font.** 42% of lines contain the Danish letters æ, ø or å. Some of the rendering fonts draw ø and æ with subtle or absent distinguishing strokes, as many historical hands also did. If your use case requires strict diacritic visual fidelity, inspect the font styles in `samples/` first.
2. **Editorial marks from source conventions.** A small share of lines contains editorial characters inherited from the source transcription conventions, including `#` (~9% of lines) and `¬` (~7%, line-break hyphenation mark), plus authentic period notation such as `†` (death) and `☿` (weekday symbol). These characters appear in both image and label, so image-text consistency is preserved. Strip or keep them according to your target alphabet.
3. **Line-level only.** No page layout, no ALTO/PAGE hierarchy: this is a line-image + text dataset intended for recogniser training, not segmentation.

## Intended use

- Augmentation for low-resource historical Danish HTR (our use case)
- Pre-training before fine-tuning on small real ground-truth sets
- Alphabet and tokenizer stress-testing for Nordic historical text

## Citation

If you use this dataset, please cite:

```
Jha, A. (2026). Danish HTR Synthetic Lines (18th-century style) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22093255
```

A benchmark paper describing the surrounding evaluation work is in preparation; the citation will be updated once available.

## Acknowledgements

Generated as part of a production HTR effort for historical Danish property and parish records. Thanks to the maintainers of the public Danish transcription corpora that provided the source text distributions.
