"""Notebook-compatible wrappers around the main MedViet PII implementation."""

from __future__ import annotations

import sys
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parent
REPO_ROOT = LAB_ROOT.parent
MEDVIET_ROOT = REPO_ROOT / "medviet-governance"
MEDVIET_SRC = MEDVIET_ROOT / "src"

for candidate in (MEDVIET_ROOT, MEDVIET_SRC):
    candidate_str = str(candidate)
    if candidate.exists() and candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from src.pii.detector import build_vietnamese_analyzer, detect_pii, print_model_setup_hint


__all__ = [
    "build_vietnamese_analyzer",
    "detect_pii",
    "print_model_setup_hint",
]
