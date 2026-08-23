#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uae/amounts.py — AED amounts in Arabic text, plus tafqit
(المبلغ كتابةً — amount in words), required on quotations, receipts,
contracts and cheques.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

RULES:
  - Numerals: Latin 0-9, thousands separator, isolated so the figure
    cannot split across BiDi runs: درهم ⟨1,500.00⟩ …
  - In Arabic prose the currency word follows Arabic grammar:
    "مبلغ وقدره ⟨1,500⟩ درهم إماراتي".
  - Tafqit follows standard Arabic number grammar (dual forms,
    3-10 plural, 11+ singular) — covers up to billions + fils.
"""

from engine.ar_text import iso

_ONES = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة",
         "ثمانية", "تسعة", "عشرة", "أحد عشر", "اثنا عشر", "ثلاثة عشر",
         "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر",
         "تسعة عشر"]
_TENS = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون",
         "ثمانون", "تسعون"]
_HUNDREDS = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة",
             "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]

# (singular, dual, plural, 11+ form)
_SCALES = [
    ("ألف", "ألفان", "آلاف", "ألفاً"),
    ("مليون", "مليونان", "ملايين", "مليوناً"),
    ("مليار", "ملياران", "مليارات", "ملياراً"),
]


def _under_1000(n: int) -> str:
    parts = []
    h, r = divmod(n, 100)
    if h:
        parts.append(_HUNDREDS[h])
    if r:
        if r < 20:
            parts.append(_ONES[r])
        else:
            t, o = divmod(r, 10)
            parts.append(f"{_ONES[o]} و{_TENS[t]}" if o else _TENS[t])
    return " و".join(parts)


def _scale_words(n: int, scale_idx: int) -> str:
    sing, dual, plural, acc = _SCALES[scale_idx]
    if n == 1:
        return sing
    if n == 2:
        return dual
    if 3 <= n <= 10:
        return f"{_under_1000(n)} {plural}"
    return f"{_under_1000(n)} {acc}"


def _int_words(n: int) -> str:
    if n == 0:
        return "صفر"
    groups = []          # [(scale_idx or -1 for units, value)]
    scale = -1
    while n:
        n, g = divmod(n, 1000)
        if g:
            groups.append((scale, g))
        scale += 1
    parts = []
    for scale_idx, g in reversed(groups):
        parts.append(_under_1000(g) if scale_idx < 0
                     else _scale_words(g, scale_idx))
    return " و".join(parts)


def aed(amount: float, decimals: int = 2) -> str:
    """Isolated numeric AED figure for Arabic prose:
    'مبلغ وقدره ' + aed(1500) + ' درهم إماراتي'"""
    return iso(f"{amount:,.{decimals}f}")


def aed_en(amount: float) -> str:
    """English side: AED 1,500.00"""
    return f"AED {amount:,.2f}"


def tafqit_aed(amount: float) -> str:
    """المبلغ كتابةً — 'فقط ألف وخمسمائة درهم إماراتي وخمسون فلساً لا غير'.
    The canonical فقط … لا غير frame used on UAE financial documents."""
    dirhams = int(amount)
    fils = round((amount - dirhams) * 100)
    if fils == 100:
        dirhams, fils = dirhams + 1, 0

    d_words = _int_words(dirhams)
    if dirhams == 1:
        d_part = "درهم إماراتي واحد"
    elif dirhams == 2:
        d_part = "درهمان إماراتيان"
    elif 3 <= dirhams % 100 <= 10 and dirhams < 100:
        d_part = f"{d_words} دراهم إماراتية"
    else:
        d_part = f"{d_words} درهم إماراتي"

    if fils:
        f_words = _int_words(fils)
        f_part = ("فلس واحد" if fils == 1 else "فلسان" if fils == 2 else
                  f"{f_words} فلوس" if 3 <= fils <= 10 else f"{f_words} فلساً")
        return f"فقط {d_part} و{f_part} لا غير"
    return f"فقط {d_part} لا غير"


__all__ = ["aed", "aed_en", "tafqit_aed"]
