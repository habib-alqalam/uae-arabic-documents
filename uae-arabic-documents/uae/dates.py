#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uae/dates.py — UAE official date rendering: Gregorian, Hijri, and the
dual-date line used on government correspondence.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

LOCKED RULES (references/uae-conventions.md):
  - Month names: GULF transliterated set (يناير، فبراير، مارس…) —
    never the Levantine set (كانون الثاني، شباط، آذار…).
  - Digits: Latin 0-9 in all programmatic output. Immune to BiDi
    segment reversal; matches UAE gov portal rendering.
  - NEVER slashed dates (01/03/2026) inside Arabic prose — BiDi
    reverses the segments. Written month names only. Where a slashed
    date is unavoidable (form fields), isolate it: iso("24/08/2026").
  - Dual-date line format: "<Gregorian>م الموافق <Hijri>هـ".
  - Hijri conversion is tabular (Umm al-Qura). The UAE announces months
    by moon sighting; official Hijri dates can differ by ±1 day from
    the computed value. For legal filings, confirm the announced date.
"""

from datetime import date
from hijridate import Gregorian

from engine.ar_text import iso

GULF_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
               "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

HIJRI_MONTHS = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر",
                "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
                "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

EN_MONTHS = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November",
             "December"]


def gregorian_ar(d: date) -> str:
    """24 أغسطس 2026 — the only Arabic date format safe in every renderer."""
    return f"{d.day} {GULF_MONTHS[d.month - 1]} {d.year}"


def hijri_ar(d: date) -> str:
    """Computed Hijri date in Arabic: 11 ربيع الأول 1448."""
    h = Gregorian(d.year, d.month, d.day).to_hijri()
    return f"{h.day} {HIJRI_MONTHS[h.month - 1]} {h.year}"


def dual_date_ar(d: date) -> str:
    """The UAE official-letter date line:
    24 أغسطس 2026م الموافق 11 ربيع الأول 1448هـ"""
    return f"{gregorian_ar(d)}م الموافق {hijri_ar(d)}هـ"


def date_en(d: date) -> str:
    """DD/MM/YYYY for the English half of bilingual documents (safe in
    LTR context; isolate if ever embedded in Arabic)."""
    return d.strftime("%d/%m/%Y")


def date_en_long(d: date) -> str:
    """24 August 2026."""
    return f"{d.day} {EN_MONTHS[d.month - 1]} {d.year}"


def slashed_date_in_arabic(d: date) -> str:
    """Escape hatch for form-field contexts that force DD/MM/YYYY inside
    Arabic. Isolated so segments cannot reverse. Prefer gregorian_ar."""
    return iso(d.strftime("%d/%m/%Y"))


__all__ = ["gregorian_ar", "hijri_ar", "dual_date_ar", "date_en",
           "date_en_long", "slashed_date_in_arabic",
           "GULF_MONTHS", "HIJRI_MONTHS"]
