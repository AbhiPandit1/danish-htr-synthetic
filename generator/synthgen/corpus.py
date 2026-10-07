"""Load and clean the 18th-century Danish text lines that the synthetic
images are rendered from.

The text is NOT invented. Each line is a real transcription string drawn
from openly available eighteenth-century Danish transcription corpora
(parish registers / kirkeboger and administrative "supplikker" petitions).
See README.md > "Source corpora" for the exact sources and attribution.

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
) -> list[str]:
    """Return a length-filtered list of transcription strings, in file order.

    min_len / max_len match the released dataset (3-102 characters).

    `dedup=False` (default) keeps every row, so feeding the released 160k
    manifest reproduces the full 160k set — the same text rendered with a
    different font and degradation is a legitimately distinct training line.
    Set `dedup=True` to keep only the ~36k unique transcription strings.
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

    seen: set[str] = set()
    out: list[str] = []
    for text in raw:
        text = " ".join(text.split())  # normalise whitespace only
        if not (min_len <= len(text) <= max_len):
            continue
        if dedup:
            if text in seen:
                continue
            seen.add(text)
        out.append(text)
    return out
