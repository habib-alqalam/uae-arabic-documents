# UAE Document Conventions

Part of **uae-arabic-documents** · MIT · Al Qalam AI Solutions

The layer no general Arabic resource covers: how UAE official documents
are actually structured, numbered, dated and phrased.

## 1. Register
Official written output is **Modern Standard Arabic (فصحى)** — Diwan
memos, court filings, ministry letters. Emirati dialect is spoken-only;
dialect in formal writing signals limited register awareness. Tone is
respectful, neutral, factual: no emotional appeals, no admissions, no
hyperbole. Address authorities with full formal titles on first use.

## 2. Document skeleton (letters/memoranda to authorities)
1. **الديباجة** — addressee block with full title
   (e.g. «إلى نيابة الشارقة الكلية الموقرة»), greeting
   («تحية طيبة وبعد،»)
2. **بيانات مقدم الطلب** — applicant data table (name, Emirates ID,
   unified number, phone) — all identifiers isolated
3. **الموضوع** — one-line subject
4. **الوقائع / التفاصيل** — facts, numbered
5. **الطلبات** — requests, numbered with Arabic-Indic ordinals
6. **الخاتمة** — closing formula
   («وتفضلوا بقبول فائق الاحترام والتقدير،»)
7. **التوقيع** — name, capacity, date, signature line
8. **المرفقات** — attachments list

Templates: `uae/templates/`.

## 3. Numbering systems — the locked decision rule
| Context | System | Example |
|---|---|---|
| Main sections of legal/gov documents | Ordinal words | أولاً: ثانياً: ثالثاً: |
| Requests/items inside Arabic legal text | Arabic-Indic | ١. ٢. ٣. |
| Data, amounts, identifiers, dates | Latin digits | 1,500 · 2026 · 784-… |
| Bilingual/technical documents | Latin | 1. 2. 3. |

Never mix systems within one list. Identifiers and amounts are **always**
Latin digits regardless of the surrounding list system.

## 4. Dates
- Dual-date line on official correspondence:
  `24 أغسطس 2026م الموافق 11 ربيع الأول 1448هـ`
- Gulf month set (يناير…ديسمبر) — never Levantine (كانون…آذار).
- English half of bilingual documents: `DD/MM/YYYY`.
- Hijri caveat: tabular (Umm al-Qura) conversion can differ ±1 day from
  the UAE moon-sighting announcement. Confirm announced dates for legal
  deadlines.

## 5. Identifiers (render via `uae/identifiers.py`, always isolated)
Emirates ID `784-YYYY-NNNNNNN-C` · Unified Number · Trade licence
(emirate formats differ: `CN-…` Abu Dhabi, numeric Dubai/Sharjah) ·
TRN (15 digits, FTA) · Case/execution numbers `NNNN/YYYY` — the slash
makes these the highest-risk tokens in legal text · MOHRE labour card ·
plate · chassis/VIN · IBAN (`AE` + 21) · phone (`+971 5X XXX XXXX`).
Emirates ID validation is format-level only — the public Luhn
check-digit algorithm mismatches real ICP-issued IDs.

## 6. Amounts
- Prose: `مبلغ وقدره ⟨1,500.00⟩ درهم إماراتي` — figure isolated.
- **Tafqit is mandatory** on quotations, receipts, contracts, cheques:
  `فقط ألف وخمسمائة درهم إماراتي لا غير` — the فقط…لا غير frame.
  Generate with `uae/amounts.tafqit_aed()`.
- VAT: 5% standard; TRN shown on tax invoices; totals as
  الإجمالي شامل ضريبة القيمة المضافة.

## 7. Bilingual AR/EN layout
- Split-column: Arabic column RIGHT, English LEFT — per-cell direction,
  every cell a styled Paragraph.
- Stacked: Arabic block first (above), English below, each block
  homogeneous in direction.
- One canonical value per identifier across both languages (same
  isolated token — do not re-type numbers per language).

## 8. Output acceptance (courts/ministries/portals)
- Embed all fonts; keep a real text layer (TTF + ToUnicode). Scanned
  image-only PDFs are second-class evidence and defeat portal search.
- A4 portrait; conservative margins (≥ 2 cm); no decorative elements on
  legal filings.
- File size limits vary by portal (commonly 2–10 MB per attachment) —
  compress embedded images, never rasterize text.
- Signature: wet-ink line for court filings; UAE Pass digital signature
  where the portal supports it.

## 9. Verification before release
`engine/verify.py` on every build, then human review. Machine gate
first, human gate final — never the reverse, never skipped.
