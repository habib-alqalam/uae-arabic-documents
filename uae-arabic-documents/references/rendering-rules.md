# Arabic Rendering Rules — Engineering Standard

Part of **uae-arabic-documents** · MIT · Al Qalam AI Solutions

Every Arabic rendering bug reduces to one of these rules being violated.
Work top-down when diagnosing.

## Rule 1 — Order of operations
`NFC normalize → reshape → BiDi` — always, never reordered.
BiDi-before-reshape destroys positional context (wrong letter forms).

## Rule 2 — `ar()` is single-line only
`ar()` output is **visual order**. Handing it to a wrapping renderer
(ReportLab `Paragraph`) makes the renderer wrap it LTR: each line looks
right, but **lines stack in reverse order**. This is the most damaging
Arabic PDF bug in existence because it survives casual inspection.
Multi-line text goes through `engine/rtl_paragraph.py`:
reshape → wrap in **logical** order (measuring reshaped glyph widths) →
BiDi **per line** → emit top-down → draw right-anchored.

## Rule 3 — Isolate every embedded LTR token
Digits, hyphens, slashes, `+` are weak/neutral BiDi classes. Unisolated,
`2570/2026` becomes `2026/2570` and phone numbers scramble. Wrap every
number, reference, English word, URL and email in `iso()` (U+2066…U+2069)
**before** reshaping. Requires python-bidi ≥ 0.5 top-level
`from bidi import get_display` — the legacy `bidi.algorithm` module
predates isolates and raises `LRI not allowed here`.

## Rule 4 — Dates: written month names, Latin digits
Slashed dates inside Arabic reverse their segments. Use
`24 أغسطس 2026` (Gulf month set). Latin digits 0-9 everywhere in
programmatic output. If a form forces `DD/MM/YYYY`, isolate it.

## Rule 5 — Fonts
- Must cover Arabic Presentation Forms B (U+FE70–FEFF): ≥100 glyphs.
  Verify with `engine/fonts.py` before building.
- FreeSerif ✓ (141) · Amiri ✓ · Noto Naskh/Sans Arabic ✓ · Arial ✓
- FreeSans ✗ (0 — renders boxes) · Helvetica/Times ✗ · FreeSerifItalic ✗
- **Never italicise Arabic. Never synthetic-bold (`<b>`). Never rely on
  font fallback.** TTF only (Type1 loses the ToUnicode map → broken
  copy-paste).

## Rule 6 — Alignment and wrapping
- `TA_RIGHT` on every Arabic style. **Never `TA_JUSTIFY`** — ReportLab
  pads the wrong side and has no kashida.
- Table label columns ≥ 4.5 cm; never `word-break: break-all` on the
  web; Arabic has no hyphenation.

## Rule 7 — Lists
Markers are separate BiDi runs and flip to the wrong end of the line.
Use `engine/rtl_lists.py` (marker in its own **right-most** table
column). Never `bulletText=`, `<bullet>`, or `ListFlowable`.

## Rule 8 — Mirrored characters
`( ) [ ] { } « »` are mirrored glyphs: an LTR token in brackets renders
`)x(`. Use `paren_ltr()` / isolate the whole bracketed token.

## Rule 9 — Canvas discipline
- `drawRightString(x_right, y, …)` for Arabic — never `drawString`.
- `setFont()` **inside** the per-line loop — canvas font state resets
  after `showPage()` (page-2-tofu bug).
- Line height ≥ 1.7 × font size.

## Rule 10 — Normalize, then verify, then human-gate
- NFC before storage/compare (macOS emits NFD → invisible duplicates).
- Run `engine/verify.py` on every generated PDF. FAIL = do not ship.
- PASS = proceed to human review. The machine gate runs **before** the
  human, never instead (QOPS).
