# Template — Bilingual Quotation (عرض سعر)

VAT-compliant quotation frame. Amounts through `uae/amounts.py`
(figure isolated + mandatory tafqit line), TRN through
`uae/identifiers.trn()`.

---

**{{company-name-ar}}** | **{{company-name-en}}**
الرقم الضريبي / TRN: {{trn}}
رخصة تجارية / Trade Licence: {{trade-license}}

**عرض سعر / QUOTATION**
الرقم / No.: {{quotation-number}} · التاريخ / Date: {{date}}
الصلاحية / Validity: {{validity-days}} يوماً / days

إلى السادة / To: {{client-name}}

| # | البيان / Description | الكمية / Qty | السعر / Unit (AED) | الإجمالي / Total (AED) |
|---|---|---|---|---|
| 1 | {{item-1-description}} | {{item-1-qty}} | {{item-1-price}} | {{item-1-total}} |

| | |
|---|---|
| المجموع / Subtotal | {{subtotal}} |
| ضريبة القيمة المضافة 5% / VAT 5% | {{vat-amount}} |
| **الإجمالي شامل الضريبة / Grand Total** | **{{grand-total}}** |

المبلغ كتابةً: {{tafqit-line}}
Amount in words: {{amount-in-words-en}}

**الشروط / Terms:** {{payment-terms}}

التوقيع والختم / Signature & Stamp: ______________________
