#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/rtl_lists.py — Numbered and bulleted Arabic lists that keep the
marker on the correct side, at the correct end, on every line.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

THE BUG THIS FIXES
------------------
List markers ("1.", "•", "١.") are separate BiDi runs of weak/neutral
characters. They inherit direction from context and flip to the wrong
END of the line ("...قبول الاعتذار الرسمي ١." instead of
"١. قبول الاعتذار الرسمي..."). references/bug-catalog.md #2.

THE FIX (most → least robust)
-----------------------------
  A) TABLE-BASED (this module's default): marker in its own narrow
     column on the RIGHT, text column to its left. No BiDi involvement
     at all — the marker physically cannot move.
  B) RLM wrapping: "\u200F" + marker + "\u200F" forces the marker into
     the RTL run. Works for simple inline cases, fragile on wrap.
Never use ReportLab bulletText=, <bullet> tags, or ListFlowable with
Arabic.

MARKER SYSTEMS (see references/uae-conventions.md):
  ordinal_words — أولاً/ثانياً…  : main sections of legal/gov documents
  arabic_indic  — ١. ٢. ٣.       : requests/items inside Arabic legal text
  latin         — 1. 2. 3.       : data, bilingual and technical documents
  bullet        — •              : informal lists only
"""

from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_RIGHT

from .ar_text import RLM, ar
from .rtl_paragraph import rtl_paragraphs

ORDINAL_WORDS = ["أولاً", "ثانياً", "ثالثاً", "رابعاً", "خامساً",
                 "سادساً", "سابعاً", "ثامناً", "تاسعاً", "عاشراً",
                 "حادي عشر", "ثاني عشر"]

_ARABIC_INDIC = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def marker(i: int, system: str = "arabic_indic") -> str:
    """Return the logical-order marker string for item i (1-based)."""
    if system == "ordinal_words":
        return ORDINAL_WORDS[i - 1] + ":"
    if system == "arabic_indic":
        return str(i).translate(_ARABIC_INDIC) + "."
    if system == "latin":
        return str(i) + "."
    if system == "bullet":
        return "•"
    raise ValueError(f"unknown marker system: {system}")


def rtl_list(items: list, style, frame_width: float,
             system: str = "arabic_indic",
             marker_width: float = 1.4 * cm,
             row_gap: float = 3) -> Table:
    """Build a correctly-ordered Arabic list as a Table flowable.

    Layout per row (RTL): [ text column | marker column ] — the marker
    column is the RIGHTMOST, where an Arabic reader expects it.
    Multi-line items wrap correctly because each item's text goes
    through the rtl_paragraph engine (one Paragraph per visual line).

    Args:
        items:        list of logical-order Arabic strings
                      (apply iso() to embedded LTR tokens first)
        style:        ParagraphStyle — Arabic font, TA_RIGHT
        frame_width:  total available width in points
        system:       marker system (see module docstring)
        marker_width: width of the marker column (widen for ordinal_words)
    """
    if style.alignment != TA_RIGHT:
        raise ValueError("Arabic list style must be TA_RIGHT.")
    if system == "ordinal_words" and marker_width < 2.2 * cm:
        marker_width = 2.2 * cm

    text_width = frame_width - marker_width
    rows = []
    for i, item in enumerate(items, 1):
        m = ar(RLM + marker(i, system) + RLM)          # single line — ar() is safe
        para_stack = rtl_paragraphs(item, style, text_width - 0.3 * cm)
        rows.append([para_stack, Paragraph(m, style)])  # text left, marker RIGHT

    t = Table(rows, colWidths=[text_width, marker_width])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), row_gap),
        ("BOTTOMPADDING", (0, 0), (-1, -1), row_gap),
        ("LINEBELOW", (0, 0), (-1, -1), 0, colors.white),  # no visible grid
    ]))
    return t


__all__ = ["rtl_list", "marker", "ORDINAL_WORDS"]
