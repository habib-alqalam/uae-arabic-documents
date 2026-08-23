---
name: uae-arabic-documents
description: Generate UAE government and official Arabic documents (letters, memoranda to authorities, court filings, quotations, invoices) as correctly rendered PDFs — and fix any broken Arabic PDF output. ALWAYS use this skill when the task involves Arabic text in a PDF, RTL rendering, arabic_reshaper/python-bidi, reversed or disconnected Arabic letters, reversed line order in Arabic paragraphs, Arabic bullet points or numbered lists, tofu boxes, Emirates ID / TRN / trade licence / case numbers inside Arabic text, Hijri or dual dates, AED amounts in words (tafqit), bilingual AR/EN documents, or any letter/memo/quotation addressed to a UAE ministry, court, prosecution, free zone or government department. Also use it to DIAGNOSE broken Arabic output — the bug catalog maps every known failure mode to its fix.
---

# uae-arabic-documents

Engineering standard + working code for generating UAE official Arabic
documents that render correctly, plus an automated verification gate.

## Workflow

1. **Read `references/rendering-rules.md` first** — the 10 rules. Every
   Arabic rendering decision in this skill follows them.
2. For UAE structure/register/numbering/dates/identifiers, read
   `references/uae-conventions.md`.
3. Diagnosing broken output? Go straight to
   `references/bug-catalog.md` — failure mode → root cause → fix.
4. Build with the engine (never raw reshape+bidi into a Paragraph):

```python
from engine.ar_text import ar, iso                # single lines / tokens
from engine.rtl_paragraph import rtl_paragraphs   # multi-line paragraphs
from engine.rtl_lists import rtl_list             # bullets & numbering
from engine.fonts import check_font               # gate 1: font coverage
from engine.verify import verify_pdf              # gate 2: reading order
from uae.identifiers import emirates_id, trn, case_number, phone
from uae.dates import dual_date_ar, gregorian_ar
from uae.amounts import aed, tafqit_aed
```

5. Document skeletons: `uae/templates/` (official letter, prosecution
   memorandum, VAT quotation) — `{{variable-name}}` placeholders.
6. End-to-end reference implementation: `demo/generate_demo_letter.py`.

## Non-negotiable rules (full detail in references/)

- `ar()` output is visual order → **single lines only**. Multi-line
  text goes through `rtl_paragraphs()` or lines will stack reversed.
- Every embedded LTR token (numbers, refs, English) through `iso()` —
  or use the typed wrappers in `uae/identifiers.py`.
- Directional controls are stripped **after** BiDi (`ar()` does this);
  left in, ReportLab silently drops everything after them.
- `from bidi import get_display` (≥0.5) — never `bidi.algorithm`.
- Fonts: verify Presentation Forms B coverage with `check_font()`
  before building. FreeSerif/Amiri/Noto yes; FreeSans/Helvetica no.
  Never italic, never synthetic bold, never fallback, TTF only.
- Lists via `rtl_list()` — never `bulletText=`/`ListFlowable`.
- Dates: written Gulf month names + Latin digits; dual-date line for
  official correspondence via `dual_date_ar()`.
- Amounts: isolated figure via `aed()` + mandatory tafqit line via
  `tafqit_aed()` on quotations/receipts/contracts.
- **Every generated PDF runs `verify_pdf()` before delivery.** FAIL =
  fix and rebuild, never ship. PASS = proceed to human review.
- Also render a page preview image and visually inspect it — the
  verifier is a gate before human review, not a replacement for it.
