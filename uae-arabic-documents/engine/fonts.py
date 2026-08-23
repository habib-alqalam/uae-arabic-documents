#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/fonts.py — Verify a font can actually render reshaped Arabic
BEFORE you build a document with it.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

THE RULES (references/bug-catalog.md #4, #7, #8):
  - After reshaping, glyphs live in Arabic Presentation Forms B
    (U+FE70–U+FEFF). The font MUST cover this block. FreeSans has ZERO
    coverage — it renders reshaped Arabic as boxes. FreeSerif has 141.
  - NEVER italicise Arabic. FreeSerifItalic has incomplete coverage and
    Arabic typography has no italic tradition — it reads as broken.
  - NEVER synthetic-bold Arabic (<b> tags). Use a real bold face.
  - NEVER rely on font fallback: fallback fonts may lack shaping,
    producing mixed connected/disconnected text in one word.
  - Register TTF fonts only (not Type1) so the PDF text layer keeps its
    ToUnicode map and copy-paste survives.
"""

import sys
from fontTools.ttLib import TTFont

PRES_FORMS_B = (0xFE70, 0xFEFF)
BASIC_ARABIC = (0x0600, 0x06FF)
MIN_PFB_GLYPHS = 100

KNOWN_GOOD = ["FreeSerif", "Amiri", "Noto Naskh Arabic", "Noto Sans Arabic",
              "Arial", "Sakkal Majalla", "Tahoma", "Cairo"]
KNOWN_BAD = ["FreeSans (0 Presentation Forms)", "Helvetica (no Arabic)",
             "Times-Roman (no Arabic)", "FreeSerifItalic (incomplete)"]


def check_font(path: str) -> dict:
    """Return coverage report for a TTF/OTF file. Gate on ok=True."""
    font = TTFont(path)
    cmap = font.getBestCmap()
    pfb = sum(1 for c in cmap if PRES_FORMS_B[0] <= c <= PRES_FORMS_B[1])
    basic = sum(1 for c in cmap if BASIC_ARABIC[0] <= c <= BASIC_ARABIC[1])
    return {
        "path": path,
        "presentation_forms_b": pfb,
        "basic_arabic": basic,
        "ok": pfb >= MIN_PFB_GLYPHS,
        "verdict": ("OK for reshaped Arabic" if pfb >= MIN_PFB_GLYPHS else
                    f"REJECT — only {pfb} Presentation Forms B glyphs "
                    f"(need ≥{MIN_PFB_GLYPHS}). Text will render as boxes."),
    }


if __name__ == "__main__":
    for p in sys.argv[1:] or ["/usr/share/fonts/truetype/freefont/FreeSerif.ttf"]:
        r = check_font(p)
        print(f"{r['path']}\n  Pres. Forms B: {r['presentation_forms_b']}"
              f" | Basic Arabic: {r['basic_arabic']}\n  → {r['verdict']}")
