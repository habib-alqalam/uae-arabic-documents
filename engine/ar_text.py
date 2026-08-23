#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/ar_text.py — Core Arabic text preparation for PDF rendering.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

RULES ENCODED HERE (see references/rendering-rules.md):
  1. reshape FIRST, then BiDi reorder — never the reverse.
  2. ar() output is VISUAL order. It is safe for SINGLE LINES ONLY.
     For multi-line paragraphs use engine/rtl_paragraph.py — never
     hand ar() output to a wrapping Paragraph flowable.
  3. Every LTR token (numbers, references, English words) embedded in
     Arabic must be wrapped with iso() BEFORE reshaping.
  4. Normalize all Arabic to NFC before any processing or storage.
"""

import unicodedata
import arabic_reshaper
# CRITICAL: use the top-level entrypoint (python-bidi ≥0.5, Rust-backed,
# full Unicode BiDi Algorithm incl. isolates U+2066-2069).
# The legacy `bidi.algorithm.get_display` predates Unicode 6.3 and
# raises "LRI not allowed here" on isolate characters. Never import it.
from bidi import get_display

# ── Unicode directional controls ─────────────────────────────────────
RLM = "\u200F"   # Right-to-Left Mark — glue a neutral char to the RTL run
LRM = "\u200E"   # Left-to-Right Mark — glue a neutral char to the LTR run
LRI = "\u2066"   # Left-to-Right Isolate  (open)
RLI = "\u2067"   # Right-to-Left Isolate  (open)
FSI = "\u2068"   # First-Strong Isolate   (open)
PDI = "\u2069"   # Pop Directional Isolate (close)

# Reshaper configured for legal/official documents:
# keep harakat (some legal texts carry them), support ligatures.
_reshaper = arabic_reshaper.ArabicReshaper(configuration={
    "delete_harakat": False,
    "support_ligatures": True,
    "use_unshaped_instead_of_isolated": False,
})


def nfc(text: str) -> str:
    """Normalize to NFC. Run on ALL input before processing or storage.
    macOS produces NFD; mixing forms creates invisible duplicates and
    failed comparisons (references/bug-catalog.md #10)."""
    return unicodedata.normalize("NFC", text)


def iso(token: str) -> str:
    """Wrap an embedded LTR token (number, reference, English word,
    phone, date) in directional isolates so it cannot leak direction
    into surrounding Arabic and its internal order cannot be reversed.

    Use for: INV-41752, CN-6316697, 784-1990-1234567-1, +971 58 561 1292,
    'Article 18' style refs, ISO dates, URLs, email addresses.

        ar(f"رقم الفاتورة {iso('INV-41752')} غير مدفوعة")
    """
    return LRI + token + PDI


def rtl_iso(token: str) -> str:
    """Wrap an Arabic token embedded inside LTR text (the mirror case)."""
    return RLI + token + PDI


import re
_CONTROLS = re.compile("[\u200e\u200f\u2066-\u2069\u202a-\u202e]")


def strip_controls(visual: str) -> str:
    """Remove directional formatting characters AFTER BiDi processing.

    The controls (LRI/RLI/FSI/PDI, RLM/LRM, embeddings) exist to steer
    get_display(); once the visual order is computed they are spent.
    Fonts have no glyphs for them — left in the string, ReportLab's TTF
    subsetter breaks the text run and everything after the control is
    silently DROPPED from the page (bug-catalog #16). Always strip
    post-BiDi, never pre-BiDi."""
    return _CONTROLS.sub("", visual)


def ar(text: str) -> str:
    """Prepare ONE LINE of Arabic (or mixed) text for a renderer that
    does no shaping/BiDi of its own (ReportLab canvas, Acrobat form
    fields, FPDF2, image drawing with PIL).

    Pipeline: NFC → reshape → BiDi visual order → strip spent controls.

    WARNING — single line only. If this string will WRAP inside a
    Paragraph flowable, the line ORDER will reverse (the classic
    multi-line bug). Use rtl_paragraph.wrap_rtl / rtl_paragraphs
    for anything longer than one line.
    """
    return strip_controls(get_display(_reshaper.reshape(nfc(text))))


def reshape_only(text: str) -> str:
    """Shaping without BiDi. Rarely needed directly; used internally by
    the paragraph engine which applies BiDi per wrapped line."""
    return _reshaper.reshape(nfc(text))


def bidi_only(shaped: str) -> str:
    """BiDi visual reorder of already-reshaped text (per-line stage of
    the paragraph engine). Spent controls stripped for the renderer."""
    return strip_controls(get_display(shaped))


# ── Mirrored characters ──────────────────────────────────────────────
# Parentheses/brackets are mirrored glyphs in RTL context: (x) renders
# as )x( when the runs split. Two safe strategies:
#   A) isolate the bracketed content:  iso("(INV-41752)")
#   B) keep brackets INSIDE one Arabic run and let BiDi mirror them
#      correctly — works when content is Arabic-only.
# Never mix strategy A and B in one bracket pair.

def paren_ltr(content: str) -> str:
    """Safely parenthesize an LTR token inside Arabic text."""
    return iso("(" + content + ")")


__all__ = [
    "RLM", "LRM", "LRI", "RLI", "FSI", "PDI",
    "nfc", "iso", "rtl_iso", "ar", "reshape_only", "bidi_only", "strip_controls",
    "paren_ltr",
]
