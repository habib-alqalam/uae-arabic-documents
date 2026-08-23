#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/rtl_paragraph.py — Multi-line Arabic paragraphs that read in the
correct order. The permanent fix for the #1 Arabic PDF bug.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

THE BUG THIS FIXES
------------------
ar() (reshape + get_display) returns text in VISUAL order. If you hand
that string to a wrapping renderer (ReportLab Paragraph), the renderer
wraps it with an LTR line-breaking algorithm. Each individual line looks
correct, but the LINES STACK IN REVERSE ORDER — sentence 1 appears at
the bottom. Single-line strings never expose it; every real paragraph
does. This shipped-to-court-almost bug is documented in
references/bug-catalog.md #1.

THE FIX
-------
    1. reshape the LOGICAL text (shaping first, always)
    2. wrap into lines IN LOGICAL ORDER, measuring real glyph widths
    3. apply BiDi per line (visual order within the line only)
    4. emit lines top→bottom in logical sequence
    5. draw each line right-anchored (drawRightString)

Never let a Paragraph flowable wrap visual-order Arabic. Ever.
"""

from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

from .ar_text import nfc, reshape_only, bidi_only


def wrap_rtl(text: str, font_name: str, font_size: float,
             max_width: float) -> list:
    """Wrap Arabic/mixed text into visual lines in CORRECT reading order.

    Returns a list of visual-order strings, first line first.
    Width is measured on the reshaped glyphs (post-shaping widths differ
    from raw codepoints — lam-alef ligature is one glyph, not two).

    Args:
        text:       logical-order source text (apply iso() to embedded
                    LTR tokens BEFORE calling)
        font_name:  a registered TTF font name (FreeSerif / Amiri / Noto)
        font_size:  points
        max_width:  available line width in points
    """
    shaped = reshape_only(nfc(text))
    words = shaped.split(" ")
    space_w = pdfmetrics.stringWidth(" ", font_name, font_size)

    lines, current, current_w = [], [], 0.0
    for w in words:
        ww = pdfmetrics.stringWidth(w, font_name, font_size)
        add = ww if not current else ww + space_w
        if current and current_w + add > max_width:
            lines.append(" ".join(current))
            current, current_w = [w], ww
        else:
            current.append(w)
            current_w += add
    if current:
        lines.append(" ".join(current))

    # BiDi per line — logical line sequence is preserved.
    return [bidi_only(ln) for ln in lines]


def draw_rtl_paragraph(canvas, text: str, x_right: float, y_top: float,
                       max_width: float, font_name: str,
                       font_size: float, leading: float = None) -> float:
    """Draw a correctly-ordered RTL paragraph on a raw canvas.

    Right-anchored at x_right, first line at y_top, growing downward.
    setFont is called PER LINE — canvas font state resets after
    showPage() and this guards against the page-2-tofu bug
    (references/bug-catalog.md #6).

    Returns the y position after the last line (for stacking content).
    """
    leading = leading or font_size * 1.7   # Arabic needs generous leading
    y = y_top
    for line in wrap_rtl(text, font_name, font_size, max_width):
        canvas.setFont(font_name, font_size)
        canvas.drawRightString(x_right, y, line)
        y -= leading
    return y


def rtl_paragraphs(text: str, style: ParagraphStyle,
                   max_width: float) -> list:
    """Platypus-compatible: return a list of single-line Paragraph
    flowables in correct order. Each flowable holds exactly one visual
    line, so ReportLab has nothing to wrap and nothing to reverse.

    The style MUST use an Arabic-capable font and alignment=TA_RIGHT.
    max_width should be the frame width minus indents. Keep it slightly
    (2-3%) under the true frame width so rounding never forces a wrap.
    """
    if style.alignment != TA_RIGHT:
        raise ValueError("Arabic paragraph styles must use TA_RIGHT "
                         "(never TA_JUSTIFY — ReportLab pads the wrong "
                         "side and has no kashida support).")
    safe = max_width * 0.97
    return [Paragraph(line, style)
            for line in wrap_rtl(text, style.fontName, style.fontSize, safe)]


__all__ = ["wrap_rtl", "draw_rtl_paragraph", "rtl_paragraphs"]
