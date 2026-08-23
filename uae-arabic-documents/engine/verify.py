#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/verify.py — Automated reading-order verification for generated
Arabic PDFs. The build gate: FAIL means do not ship the file.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

WHY
---
"Render a preview and look at it" is manual, non-reproducible, and it
failed twice in production before catching the line-reversal bug. This
module makes the check programmatic and CI-able. Human-gated release
still applies (QOPS) — this gate runs BEFORE the human, not instead.

EXTRACTOR CHOICE (hard-won)
---------------------------
pypdf silently DROPS the tail of lines containing mixed RTL/LTR runs —
the page renders correctly but the extraction is incomplete, producing
false FAILs. pdfium (pypdfium2) has a real text engine: it decomposes
Presentation Forms back to base letters AND returns lines in logical
reading order. This module therefore uses pypdfium2 exclusively.

HOW IT WORKS
------------
1. Extract the text layer with pdfium (logical order, base letters).
2. NFKC-normalize + strip controls/tatweel/punctuation on both sides.
3. Score:
   COVERAGE — fraction of source words present in the extraction
     (either orientation, for producer robustness). Catches tofu,
     missing glyphs, dropped runs — including the U+2066-in-font bug
     that silently drops everything after an unstripped control.
   ORDER    — fraction of consecutive source word pairs appearing in
     order in the extraction. Also computed on a line-reversed
     variant: if that scores clearly higher, lines were emitted
     bottom-to-top — the classic multi-line bug — and the verdict
     names it.

Heuristic gate calibrated for ReportLab output from this repo's engine.
FAIL is always real; borderline PASS still gets the visual check.
"""

import re
import sys
import unicodedata
import pypdfium2 as pdfium

_STRIP = re.compile(r"[\u200e\u200f\u2066-\u2069\u202a-\u202e\u0640"
                    r"\.,;:!\?\(\)\[\]«»\"'،؛؟\-–—/\\|_]+")

COVERAGE_MIN = 0.95
ORDER_MIN = 0.75
MONOTONICITY_MIN = 0.60   # fraction of adjacent line pairs in forward order


def _norm_words(text: str) -> list:
    t = unicodedata.normalize("NFKC", text)
    t = _STRIP.sub(" ", t)
    return [w for w in t.split() if w]


def _extract_lines(pdf_path: str) -> list:
    doc = pdfium.PdfDocument(pdf_path)
    lines = []
    for page in doc:
        txt = page.get_textpage().get_text_bounded()
        lines.extend(ln for ln in txt.replace("\r", "\n").split("\n")
                     if ln.strip())
    return lines


def _line_monotonicity(ext_lines: list, src_words: list) -> float:
    """Line-granularity reading-order check — the reversal detector.

    Word-level bigram scores are dominated by WITHIN-line pairs, so a
    paragraph whose lines stack bottom-to-top can still score >0.9.
    This detector anchors each extracted line to a position in the
    source stream (median source-index of its recognized words) and
    measures how often consecutive lines move FORWARD through the
    source. Correct documents score near 1.0; a reversed paragraph
    scores near 0.0 for its span."""
    first_pos = {}
    for i, w in enumerate(src_words):
        first_pos.setdefault(w, i)
    anchors = []
    for ln in ext_lines:
        idxs = sorted(first_pos[w] for w in _norm_words(ln) if w in first_pos)
        if len(idxs) >= 2:
            anchors.append(idxs[len(idxs) // 2])
    if len(anchors) < 2:
        return 1.0
    fwd_pairs = sum(1 for a, b in zip(anchors, anchors[1:]) if b >= a)
    return fwd_pairs / (len(anchors) - 1)


def _bigram_order_score(src_words: list, seq: list) -> float:
    if len(src_words) < 2:
        return 1.0
    pos = {}
    for i, w in enumerate(seq):
        pos.setdefault(w, []).append(i)
    hits = total = 0
    for a, b in zip(src_words, src_words[1:]):
        total += 1
        if a in pos and b in pos and any(pb > pa for pa in pos[a] for pb in pos[b]):
            hits += 1
    return hits / total if total else 1.0


def verify_pdf(pdf_path: str, source_texts: list) -> dict:
    """Verify a generated PDF against its logical-order source strings.

    Args:
        pdf_path:     path to the generated PDF
        source_texts: every logical-order string that was rendered
                      (the same strings passed to the engine, BEFORE
                      reshaping — iso() wrappers are fine)
    Returns dict: coverage, order_score, reversed_order_score,
                  line_reversal_detected, passed, verdict.
    """
    ext_lines = _extract_lines(pdf_path)

    src_words = []
    for t in source_texts:
        src_words.extend(_norm_words(t))

    seq_fwd = []
    for ln in ext_lines:
        seq_fwd.extend(_norm_words(ln))

    ext_set = set(seq_fwd) | {w[::-1] for w in seq_fwd}
    covered = sum(1 for w in src_words if w in ext_set)
    coverage = covered / len(src_words) if src_words else 1.0

    fwd = _bigram_order_score(src_words, seq_fwd)
    mono = _line_monotonicity(ext_lines, src_words)
    reversal = mono < MONOTONICITY_MIN

    passed = coverage >= COVERAGE_MIN and fwd >= ORDER_MIN and not reversal

    if reversal:
        verdict = ("FAIL — LINE-ORDER REVERSAL detected: lines read "
                   "bottom-to-top. A visual-order string was wrapped by an "
                   "LTR renderer. Use engine/rtl_paragraph.py.")
    elif coverage < COVERAGE_MIN:
        verdict = (f"FAIL — coverage {coverage:.0%} < {COVERAGE_MIN:.0%}: "
                   "missing glyphs/tofu or dropped text. Check font "
                   "Presentation Forms B coverage (engine/fonts.py) and "
                   "that directional controls were stripped post-BiDi.")
    elif fwd < ORDER_MIN:
        verdict = (f"WARN/FAIL — order score {fwd:.0%} < {ORDER_MIN:.0%}: "
                   "word order disturbed. Inspect visually before release.")
    else:
        verdict = (f"PASS — coverage {coverage:.0%}, order {fwd:.0%}. "
                   "Proceed to human review (QOPS gate).")

    return {"coverage": round(coverage, 3), "order_score": round(fwd, 3),
            "line_monotonicity": round(mono, 3),
            "line_reversal_detected": reversal, "passed": passed,
            "verdict": verdict}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: verify.py <pdf> <source_text_file>")
        sys.exit(2)
    src = open(sys.argv[2], encoding="utf-8").read().split("\n")
    r = verify_pdf(sys.argv[1], src)
    print(r["verdict"])
    sys.exit(0 if r["passed"] else 1)
