#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo/generate_demo_letter.py — End-to-end demonstration: generate a
complete Arabic UAE official letter PDF exercising every module, then
run the reading-order verifier on the result.

    python3 demo/generate_demo_letter.py

Output: demo/uae_official_letter_demo.pdf + PASS/FAIL verdict.
All data below is fictional.
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from engine.ar_text import ar, iso
from engine.rtl_paragraph import rtl_paragraphs
from engine.rtl_lists import rtl_list
from engine.fonts import check_font
from engine.verify import verify_pdf
from uae.identifiers import emirates_id, unified_number, phone, case_number, trade_license
from uae.dates import dual_date_ar, gregorian_ar
from uae.amounts import aed, tafqit_aed

FONT = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
FONT_B = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
OUT = os.path.join(os.path.dirname(__file__), "uae_official_letter_demo.pdf")

# ── Gate 1: font coverage ────────────────────────────────────────────
report = check_font(FONT)
assert report["ok"], report["verdict"]
pdfmetrics.registerFont(TTFont("Ar", FONT))
pdfmetrics.registerFont(TTFont("ArB", FONT_B))

# ── Styles (TA_RIGHT, generous leading, real bold face) ──────────────
body = ParagraphStyle("body", fontName="Ar", fontSize=11.5, leading=21,
                      alignment=TA_RIGHT)
head = ParagraphStyle("head", fontName="ArB", fontSize=13, leading=22,
                      alignment=TA_RIGHT, textColor=colors.HexColor("#0D3D2A"))
title = ParagraphStyle("title", fontName="ArB", fontSize=15, leading=26,
                       alignment=TA_CENTER, textColor=colors.HexColor("#0D3D2A"))

W, H = A4
MARGIN = 2.2 * cm
FRAME_W = W - 2 * MARGIN

# ── Content (logical order; identifiers pre-isolated) ────────────────
today = date(2026, 8, 24)
AMOUNT = 12500.00

t_title = "خطاب رسمي — طلب تسوية مستحقات"
t_date = f"التاريخ: {dual_date_ar(today)}"
t_ref = f"الرقم المرجعي: {iso('AQD-2026-0147')}"
t_to = "إلى / دائرة التنمية الاقتصادية الموقرة — إمارة الشارقة"
t_greet = "تحية طيبة وبعد،"
t_subject = f"الموضوع: طلب تسوية المستحقات المالية المرتبطة بالرخصة التجارية رقم {trade_license('786514')}"

applicant_rows = [
    ("الاسم", "أحمد عبدالله المنصوري"),
    ("رقم الهوية الإماراتية", emirates_id("784-1990-1234567-1")),
    ("الرقم الموحد", unified_number("12345678")),
    ("رقم الهاتف", phone("+971 50 123 4567")),
]

t_para1 = ("يتقدم مقدم هذا الخطاب إلى دائرتكم الموقرة بطلب تسوية "
           "المستحقات المالية المرتبطة بالرخصة التجارية المشار إليها "
           "أعلاه، وذلك بعد مراجعة كشف الحساب الصادر بتاريخ "
           f"{gregorian_ar(date(2026, 8, 10))} والذي أظهر مبلغاً "
           f"إجمالياً وقدره {aed(AMOUNT)} درهم إماراتي.")

t_para2 = ("ويؤكد مقدم الطلب التزامه التام بجميع القوانين والأنظمة "
           "المعمول بها في الدولة، وحرصه على تسوية كافة الالتزامات "
           "المالية ضمن المهلة النظامية المقررة، مع الإشارة إلى أن "
           f"الطلب السابق المقيد برقم {case_number('2570/2026')} "
           "لا يزال قيد الدراسة لدى الجهة المختصة.")

requests = [
    "اعتماد جدول سداد على أربعة أقساط شهرية متساوية اعتباراً من الشهر القادم.",
    f"إصدار براءة ذمة فور سداد كامل المبلغ البالغ {aed(AMOUNT)} درهم إماراتي.",
    "تحديث حالة الرخصة التجارية في السجل الاقتصادي بعد إتمام التسوية.",
]

t_tafqit = f"المبلغ كتابةً: {tafqit_aed(AMOUNT)}"
t_close = "وتفضلوا بقبول فائق الاحترام والتقدير،"
t_sign = "الاسم: أحمد عبدالله المنصوري          التوقيع: ______________"

# ── Build ────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(OUT, pagesize=A4, topMargin=MARGIN,
                        bottomMargin=MARGIN, leftMargin=MARGIN,
                        rightMargin=MARGIN,
                        title="UAE Official Letter — uae-arabic-documents demo")
story = [
    Paragraph(ar(t_title), title),
    HRFlowable(width="100%", thickness=1.2,
               color=colors.HexColor("#B7952A"), spaceAfter=10),
    Paragraph(ar(t_date), body), Paragraph(ar(t_ref), body),
    Spacer(1, 6),
    Paragraph(ar(t_to), head), Paragraph(ar(t_greet), body),
    Spacer(1, 4),
]
story.extend(rtl_paragraphs(t_subject, head, FRAME_W))
story.append(Spacer(1, 8))

# Applicant table — value column left, label column RIGHT; every cell a Paragraph
rows = [[Paragraph(ar(v), body), Paragraph(ar(k), head)]
        for k, v in applicant_rows]
tbl = Table(rows, colWidths=[FRAME_W - 5.5 * cm, 5.5 * cm])
tbl.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F5F0E8")),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(tbl)
story.append(Spacer(1, 10))

for para in (t_para1, t_para2):
    story.extend(rtl_paragraphs(para, body, FRAME_W))
    story.append(Spacer(1, 6))

story.append(Paragraph(ar("الطلبات:"), head))
story.append(rtl_list(requests, body, FRAME_W, system="arabic_indic"))
story.append(Spacer(1, 8))
story.extend(rtl_paragraphs(t_tafqit, body, FRAME_W))
story.append(Spacer(1, 14))
story.append(Paragraph(ar(t_close), body))
story.append(Spacer(1, 10))
story.append(Paragraph(ar(t_sign), body))

doc.build(story)
print(f"Built: {OUT}")

# ── Gate 2: reading-order verification ───────────────────────────────
sources = ([t_title, t_date, t_ref, t_to, t_greet, t_subject,
            t_para1, t_para2, t_tafqit, t_close, t_sign]
           + requests + [f"{k} {v}" for k, v in applicant_rows])
result = verify_pdf(OUT, sources)
print(result["verdict"])
sys.exit(0 if result["passed"] else 1)
