"""Danish HTR synthetic line generator.

A small, deterministic pipeline that renders 18th-century Danish transcription
strings as degraded handwriting line images with perfect ground truth, for
bootstrapping historical Handwritten Text Recognition.

Modules:
    corpus   - load/clean the source transcription lines
    render   - render one line as clean ink-on-paper
    degrade  - apply + record realistic capture degradation
    splits   - deterministic train/val/test assignment
"""
__version__ = "1.0.0"
