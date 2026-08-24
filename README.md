# uae-arabic-documents

**Generate UAE government and official Arabic documents that render
correctly — with an automated gate that refuses to ship broken output.**

مجموعة أدوات مفتوحة المصدر لإنتاج المستندات الرسمية الإماراتية باللغة
العربية بشكل صحيح — هوية، تاريخ هجري وميلادي، مبالغ كتابةً، وقوائم
مرقمة سليمة الاتجاه.

Arabic PDF generation is quietly broken almost everywhere: paragraphs
whose lines stack bottom-to-top, list markers at the wrong end, case
number `2570/2026` rendering as `2026/2570` in a legal filing, tofu
boxes on page 2 only. Every bug in this repo's catalog was hit — and
fixed — in real production generating documents for UAE courts,
ministries and government portals.

This is the engineering standard, the working code, and the
verification gate, released so every typing centre, PRO office, law
firm and developer in the UAE can produce official Arabic documents
that are simply *correct*.

## What's inside

| Layer | Contents |
|---|---|
| **`engine/`** — general Arabic PDF engineering | `ar_text.py` (reshape→BiDi→strip-controls pipeline, directional isolates, mirrored chars, NFC) · `rtl_paragraph.py` (**the fix for reversed line order** — logical-order wrapping, per-line BiDi) · `rtl_lists.py` (bullets/numbering that stay on the right end) · `fonts.py` (Presentation Forms B coverage gate) · `verify.py` (**automated reading-order verifier** — CI-able build gate) |
| **`uae/`** — the UAE layer | `identifiers.py` (Emirates ID, TRN, trade licence, case numbers, MOHRE, IBAN, plates — all isolate-safe) · `dates.py` (dual Gregorian+Hijri official date line, Gulf month set) · `amounts.py` (AED figures + **tafqit** — المبلغ كتابةً) · `templates/` (official letter, prosecution memorandum, VAT quotation) |
| **`references/`** | `rendering-rules.md` (the 10 rules) · `bug-catalog.md` (18 production failure modes → root cause → fix) · `uae-conventions.md` (register, document skeletons, numbering systems, portal acceptance) |
| **`SKILL.md`** | Installable as a Claude / agent skill |
| **`demo/`** | One command → complete bilingual UAE official letter, verified |

## Quick start

```bash
git clone https://github.com/habib-alqalam/uae-arabic-documents
cd uae-arabic-documents
pip install -r requirements.txt
python3 demo/generate_demo_letter.py
# → Built: demo/uae_official_letter_demo.pdf
# → PASS — coverage 98%, order 95%. Proceed to human review.
```

```python
from engine.rtl_paragraph import rtl_paragraphs
from engine.rtl_lists import rtl_list
from engine.verify import verify_pdf
from uae.identifiers import emirates_id, case_number
from uae.dates import dual_date_ar
from uae.amounts import tafqit_aed
```

## The five fixes that matter most

1. **Reversed line order** — `ar()` (reshape+BiDi) returns *visual*
   order; a wrapping renderer then wraps it LTR and r paragraph
   reads bottom-to-top. `rtl_paragraph.py` wraps in logical order and
   applies BiDi per line. (bug-catalog #1)
2. **List markers on the wrong end** — markers are separate BiDi runs.
   `rtl_lists.py` pins them in a right-most table column. (#2)
3. **Scrambled identifiers** — `2570/2026` → `2026/2570` unisolated.
   Every UAE identifier type gets a typed, isolate-wrapped renderer. (#3)
4. **Silently dropped text** — directional controls left in the drawn
   string break ReportLab's text run; everything after them vanishes.
   Controls are stripped *after* BiDi, automatically. (#16)
5. **No more "looks fine to me"** — `verify.py` extracts the built
   PDF's text layer (pdfium), checks word coverage and line-order
   monotonicity, and **fails the build** on the classic reversal bug.
   Verified against a deliberately broken control PDF.

## Scope and honesty

- Calibrated for Python + ReportLab output (the dominant programmatic
  Arabic-PDF stack). The rules generalize; the code targets ReportLab.
- The verifier is a heuristic gate, tuned to be strict: a FAIL is
  always real; a PASS still goes to human review. It runs *before*
  the human gate, never instead of it.
- Emirates ID validation is format-level by design — the public Luhn
  check-digit algorithm mismatches real ICP-issued IDs.
- Hijri dates are tabular (Umm al-Qura); UAE-announced dates can
  differ ±1 day. Confirm announced dates for legal deadlines.

## Contributing

Issues and PRs welcome — especially new bug-catalog entries with a
reproducible failure, additional UAE document skeletons, and
emirate-specific portal acceptance notes. Every catalog entry must
state failure mode, root cause, and fix.

## License & credit

MIT. Built and maintained by **Habib Mohammed Babul** —
[Al Qalam AI Solutions](https://alqalamai.ae), Abu Dhabi/Sharjah, UAE.
Born from production work automating UAE government document
workflows; released so the whole UAE ecosystem benefits.

صُنع في الإمارات 🇦🇪
