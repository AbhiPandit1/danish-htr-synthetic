"""Load and clean the 18th-century Danish text lines that the synthetic
images are rendered from.

The text is NOT invented. Each line is a real transcription string drawn
from the DiEm HTR dataset (Digitalisering af Enesteministerialboger), the
volunteer-verified transcriptions of Danish parish registers released by the
Danish National Archives (Rigsarkivet) under CC BY 4.0. See README.md >
"Source corpora" for the attribution and the provenance overlap check.

The corpus file may be either:
  * a JSONL manifest with a "text" field per row (e.g. the released
    manifest of the existing dataset), or
  * a plain-text file with one transcription per line.
"""
from __future__ import annotations

import json
from pathlib import Path


def load_lines(
    path: str | Path,
    min_len: int = 3,
    max_len: int = 102,
    dedup: bool = False,
    normalize: dict | None = None,
) -> list[str]:
    """Return a length-filtered list of transcription strings, in file order.

    min_len / max_len match the released dataset (3-102 characters).

    `dedup=False` (default) keeps every row, so feeding the released 160k
    manifest reproduces the full 160k set — the same text rendered with a
    different font and degradation is a legitimately distinct training line.
    Set `dedup=True` to keep only the ~36k unique transcription strings.

    `normalize` is an optional character-replacement map applied to each
    string (for example {"å": "aa"} for strictly period-faithful spelling).
    It is a no-op by default, and on the released corpus `å` does not occur.
    """
    path = Path(path)
    raw: list[str] = []

    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                raw.append(json.loads(line)["text"])
    else:  # plain text, one transcription per line
        with path.open(encoding="utf-8") as fh:
            raw = [ln.rstrip("\n") for ln in fh]

    table = str.maketrans(normalize) if normalize and all(
        len(k) == 1 for k in normalize
    ) else None

    seen: set[str] = set()
    out: list[str] = []
    for text in raw:
        text = " ".join(text.split())  # normalise whitespace only
        if normalize:
            text = text.translate(table) if table else _multi_replace(text, normalize)
        if not (min_len <= len(text) <= max_len):
            continue
        if dedup:
            if text in seen:
                continue
            seen.add(text)
        out.append(text)
    return out


def _multi_replace(text: str, mapping: dict) -> str:
    """Apply multi-character replacements (e.g. {"aa": "å"}) in a stable order."""
    for src, dst in mapping.items():
        text = text.replace(src, dst)
    return text
