#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uae/identifiers.py — Render every UAE official identifier correctly
inside Arabic text. One canonical function per identifier type.

Part of uae-arabic-documents.
License: MIT | Al Qalam AI Solutions | Habib Mohammed Babul

THE PROBLEM
-----------
UAE identifiers are LTR tokens full of weak/neutral characters (digits,
hyphens, slashes, plus signs). Embedded raw in Arabic, the BiDi
algorithm reverses their segments: 784-1990-1234567-1 can render with
its groups in the wrong order, and case number 2570/2026 flips to
2026/2570 — which in a legal filing is a DIFFERENT CASE.

THE FIX
-------
Wrap every identifier in directional isolates (U+2066…U+2069) so its
internal order is sealed and it cannot leak direction. Always render
identifiers in Latin digits (0-9) — never Arabic-Indic — so segment
order is immune to BiDi in every downstream viewer.

Every function returns a LOGICAL-order string ready to embed in text
that will then pass through ar() / the paragraph engine.
"""

import re
from engine.ar_text import iso

# ── Emirates ID ──────────────────────────────────────────────────────
_EID = re.compile(r"^784-?\d{4}-?\d{7}-?\d$")


def emirates_id(eid: str, validate: bool = True) -> str:
    """رقم الهوية — 784-YYYY-NNNNNNN-C.
    Validation is FORMAT-level only. The public Luhn check-digit
    algorithm is unreliable against real ICP-issued IDs (documented
    mismatches exist), so no checksum is enforced."""
    clean = eid.strip()
    if validate and not _EID.match(clean.replace(" ", "")):
        raise ValueError(f"Not a valid Emirates ID format: {eid}")
    digits = re.sub(r"\D", "", clean)
    return iso(f"{digits[0:3]}-{digits[3:7]}-{digits[7:14]}-{digits[14]}")


def unified_number(num: str) -> str:
    """الرقم الموحد — ICP unified number (variable length, digits only)."""
    return iso(re.sub(r"\D", "", num))


def trade_license(lic: str) -> str:
    """رقم الرخصة التجارية — e.g. CN-6316697 (AUH), 1338114 (DXB),
    or emirate-prefixed formats. Rendered exactly as issued."""
    return iso(lic.strip())


def trn(number: str) -> str:
    """الرقم الضريبي (TRN) — 15 digits, FTA. Grouped for readability."""
    d = re.sub(r"\D", "", number)
    if len(d) != 15:
        raise ValueError(f"TRN must be 15 digits, got {len(d)}: {number}")
    return iso(f"{d[0:3]} {d[3:7]} {d[7:11]} {d[11:15]}")


def case_number(case: str) -> str:
    """رقم القضية / رقم التنفيذ — NNNN/YYYY. The slash makes this the
    single most dangerous identifier in Arabic legal text: unisolated,
    2570/2026 renders as 2026/2570. Always isolate."""
    return iso(case.strip())


def phone(number: str) -> str:
    """رقم الهاتف — +971 5X XXX XXXX. The leading '+' is a neutral that
    jumps to the wrong end without isolation."""
    return iso(number.strip())


def iban(value: str) -> str:
    """AE-prefixed IBAN, spaced in groups of 4."""
    clean = re.sub(r"\s", "", value.upper())
    if not clean.startswith("AE") or len(clean) != 23:
        raise ValueError(f"UAE IBAN must be AE + 21 chars: {value}")
    return iso(" ".join(clean[i:i + 4] for i in range(0, len(clean), 4)))


def plate(emirate_code: str, number: str) -> str:
    """رقم اللوحة — e.g. plate('M', '12345') → M 12345 (Sharjah)."""
    return iso(f"{emirate_code.strip()} {number.strip()}")


def chassis(vin: str) -> str:
    """رقم القاعدة / الشاصي — 17-char VIN."""
    return iso(vin.strip().upper())


def invoice_ref(ref: str) -> str:
    """رقم الفاتورة / المرجع — INV-41752, QOT-2026-018, PO numbers."""
    return iso(ref.strip())


def mohre_number(num: str) -> str:
    """رقم بطاقة العمل / تصريح العمل — MOHRE labour card / work permit."""
    return iso(re.sub(r"\s", "", num))


__all__ = ["emirates_id", "unified_number", "trade_license", "trn",
           "case_number", "phone", "iban", "plate", "chassis",
           "invoice_ref", "mohre_number"]
