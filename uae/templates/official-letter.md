# Template — Official Letter to a UAE Authority (خطاب رسمي)

Placeholders use `{{variable-name}}`. Render every identifier through
`uae/identifiers.py`, dates through `uae/dates.py`, body text through
`engine/rtl_paragraph.py`, lists through `engine/rtl_lists.py`.

---

التاريخ: {{dual-date}}
الرقم المرجعي: {{reference-number}}

إلى / {{authority-full-title}} الموقرة
{{emirate}} — دولة الإمارات العربية المتحدة

تحية طيبة وبعد،

**الموضوع: {{subject-line}}**

## بيانات مقدم الطلب
| البيان | التفاصيل |
|---|---|
| الاسم | {{applicant-name}} |
| رقم الهوية الإماراتية | {{emirates-id}} |
| الرقم الموحد | {{unified-number}} |
| رقم الهاتف | {{phone}} |
| الصفة | {{capacity}} |

## التفاصيل
{{body-paragraph-1}}

{{body-paragraph-2}}

## الطلبات
١. {{request-1}}
٢. {{request-2}}
٣. {{request-3}}

وتفضلوا بقبول فائق الاحترام والتقدير،

الاسم: {{applicant-name}}
التوقيع: ______________________
التاريخ: {{gregorian-date}}

**المرفقات:**
١. {{attachment-1}}
٢. {{attachment-2}}
