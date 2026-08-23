# Arabic Rendering Bug Catalog

Part of **uae-arabic-documents** · MIT · Al Qalam AI Solutions

Every entry below was hit in real production while generating UAE legal
and government documents. Failure mode → root cause → fix.

| # | Failure | Root cause | Fix |
|---|---------|-----------|-----|
| 1 | **Multi-line paragraphs read bottom-to-top.** Each line correct, sentence order reversed. Survives casual review; caught in a court filing pre-submission. | `ar()` returns visual order; `Paragraph` wraps it with an LTR algorithm | `engine/rtl_paragraph.py` — wrap in logical order, BiDi per line |
| 2 | **List markers (`١.`, `1.`, `•`) at the wrong end of the line** | Marker is a separate weak/neutral BiDi run | `engine/rtl_lists.py` — marker in its own right-most table column |
| 3 | **Case number `2570/2026` renders `2026/2570`; phone/ID segments scramble** | Slashes/hyphens are neutral; number groups are independent LTR runs | Isolate every identifier — `uae/identifiers.py` |
| 4 | **Arabic renders as boxes (tofu)** | Font lacks Presentation Forms B — FreeSans has **0** such glyphs | FreeSerif/Amiri/Noto; gate with `engine/fonts.py` |
| 5 | **Boxes only in *some* runs (e.g. page 2, or emphasized text)** | FreeSerifItalic incomplete Arabic coverage; italic style applied | Never italicise Arabic; real bold face only |
| 6 | **Page 1 fine, page 2 tofu** | Canvas font state resets after `showPage()` | `setFont()` inside the per-line draw loop |
| 7 | **Table cells render as solid black blocks** | Raw strings passed as cell content with a non-Arabic default font | Every cell is a `Paragraph` with an Arabic style |
| 8 | **Copy-paste from PDF produces reversed/disconnected text** | Type1 font or missing ToUnicode map — text layer stores bare glyph IDs | Register TTF fonts only |
| 9 | **`(INV-41752)` renders `)INV-41752(`** | Parentheses are mirrored glyphs at a direction boundary | `paren_ltr()` — isolate the whole bracketed token |
| 10 | **Identical-looking strings compare unequal; duplicate DB rows; search misses** | NFC vs NFD mixed (macOS emits NFD) | `nfc()` before storage/compare; `utf8mb4_unicode_ci` / ICU collation |
| 11 | **Dates `01/03/2026` appear with day/month/year segments reordered** | BiDi treats each digit group as its own LTR run around neutral slashes | Written Gulf month names; isolate unavoidable slashed dates |
| 12 | **`AssertionError: LRI not allowed here`** | Legacy `bidi.algorithm.get_display` predates Unicode 6.3 isolates | `from bidi import get_display` (python-bidi ≥ 0.5, Rust UBA) |
| 13 | **Words split mid-word in narrow table cells, changing meaning** | Arbitrary break points; connected script has no safe mid-word break | Columns ≥ 4.5 cm for labels; shorter synonyms; never shrink below 8 pt |
| 14 | **Justified Arabic has huge gaps on the wrong side** | `TA_JUSTIFY` pads LTR-style; no kashida support | `TA_RIGHT` only |
| 15 | **Web: Safari/Chrome/Firefox break lines differently** | Different shaping engines (CoreText vs HarfBuzz) | `word-break: normal`, `hyphens: none`, test all targets |
| 16 | **Everything after an isolated token silently vanishes from the page** | Directional controls (U+2066…U+2069) left in the post-BiDi string; the font has no glyphs for them and ReportLab's TTF subsetter breaks the text run at the control | `strip_controls()` AFTER `get_display()`, never before — controls steer BiDi, then they are spent |
| 17 | **Verifier false-FAILs: page renders correctly but extraction is missing line tails** | pypdf drops the tail of lines containing mixed RTL/LTR runs | Extract with pdfium (`pypdfium2`) — real text engine, logical-order output, decomposes Presentation Forms |
| 18 | **`AssertionError: LRI not allowed here` (also listed as #12)** | Legacy `bidi.algorithm` module predates Unicode 6.3 isolates | `from bidi import get_display` — python-bidi ≥ 0.5 top-level Rust UBA |

## Diagnostic order
Boxes? → #4/#5/#6/#7. Disconnected letters? → shaping skipped (Rule 1)
or fallback font. Wrong *word* order in a line? → missing isolates (#3).
Wrong *line* order in a paragraph? → #1. Wrong marker position? → #2.
