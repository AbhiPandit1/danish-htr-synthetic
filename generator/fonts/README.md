# Fonts

The generator renders each line with one of several historical-style
handwriting fonts. The TTF/OTF files are **not committed** here (to respect
each font's licence); download them and drop them in this folder with the
exact filenames referenced in `../config.yaml`.

| config name | file | script family | source & licence |
|---|---|---|---|
| Kurrent | `Kurrent.ttf` | German/Danish gothic cursive (Kurrent) | Peter Wiegel, *Kurrent* — freeware (peter-wiegel.de) |
| AlteSchwabacher | `AlteSchwabacher.ttf` | broken-letter / fraktur administrative hand | GNU FreeFont / Dieter Steffmann — freeware |
| HerrVonMuellerhoff | `HerrVonMuellerhoff-Regular.ttf` | English roundhand / copperplate | Google Fonts — SIL Open Font License 1.1 |
| PetitFormalScript | `PetitFormalScript-Regular.ttf` | copperplate formal script | Google Fonts — SIL Open Font License 1.1 |

Notes
- The two Google Fonts (OFL) can be redistributed; if you prefer a fully-OFL
  build, drop the two freeware faces and keep only the OFL ones, then trim the
  `fonts:` list in `config.yaml` to match.
- Danish 18th-century clerks wrote a **gothic cursive (Kurrent)** everyday hand
  with **copperplate** used for formal headings; the font mix reflects that.
- To add a font: place the file here and add an entry to `config.yaml`
  (`name`, `style`, `path`). The `style` string is written into every
  manifest row so the script family used per line is always recoverable.
