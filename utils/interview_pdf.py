"""Interview-question PDF generator.

Renders an `InterviewQuestionSet` (per-skill Basic/Intermediate/Expert + common
categories) into a styled, printable PDF. Each question shows a difficulty pill
and a full model answer beneath it.
"""
from __future__ import annotations
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    KeepTogether, PageBreak,
)

# ── colors ─────────────────────────────────────────────────────────────────────
BLACK   = colors.HexColor("#111111")
DGRAY   = colors.HexColor("#333333")
MGRAY   = colors.HexColor("#6B7280")
LGRAY   = colors.HexColor("#9CA3AF")
HDR_BG  = colors.HexColor("#1A1A1A")
ACCENT  = colors.HexColor("#6C63FF")
SKILL_BG = colors.HexColor("#EEF2FF")
BOX_BG  = colors.HexColor("#F9FAFB")
BORDER  = colors.HexColor("#D1D5DB")

BASIC_BG = colors.HexColor("#DCFCE7"); BASIC_FG = colors.HexColor("#166534")
INT_BG   = colors.HexColor("#FEF3C7"); INT_FG   = colors.HexColor("#92400E")
EXP_BG   = colors.HexColor("#FEE2E2"); EXP_FG   = colors.HexColor("#991B1B")


def _esc(t) -> str:
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _diff_color(diff: str):
    d = (diff or "").strip().lower()
    if d.startswith("bas") or d == "easy":     return BASIC_BG, BASIC_FG
    if d.startswith("exp") or d == "hard":     return EXP_BG,   EXP_FG
    return INT_BG, INT_FG


def _make_question_row(q, idx: int, full_w: float, question_s, answer_s, pill_s):
    """Build the rows for a single question: header (Q + pill) and answer."""
    bg, fg = _diff_color(q.difficulty)
    pill = Table(
        [[Paragraph(f"<font color='{fg.hexval()}'>{_esc(q.difficulty or 'Medium')}</font>", pill_s)]],
        colWidths=[2.0*cm],
    )
    pill.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("BOX",           (0,0), (-1,-1), 0.4, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))

    qtext = f"<b>Q{idx}.</b> {_esc(q.question)}"
    row = Table(
        [[Paragraph(qtext, question_s), pill]],
        colWidths=[full_w - 2.2*cm, 2.0*cm],
    )
    row.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING",   (0,0), (-1,-1), 2),
        ("BOTTOMPADDING",(0,0), (-1,-1), 0),
    ]))

    items = [row]
    if q.answer:
        items.append(Paragraph(f"<b>Answer:</b> {_esc(q.answer)}", answer_s))
    items.append(Spacer(1, 5))
    return items


def generate_interview_pdf(
    question_set,
    candidate_name: str = "",
) -> bytes:
    """Render an `agents.schemas.InterviewQuestionSet` as a PDF (bytes)."""
    buf = io.BytesIO()
    full_w = 21*cm - 4*cm

    # ── Styles ────────────────────────────────────────────────────────────────
    title_s   = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22, textColor=colors.white, alignment=TA_LEFT, leading=24)
    sub_s     = ParagraphStyle("sub",   fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#D1D5DB"), alignment=TA_LEFT, leading=14)
    skill_s   = ParagraphStyle("skill", fontName="Helvetica-Bold", fontSize=14, textColor=BLACK, spaceBefore=12, spaceAfter=2, leading=18)
    tier_s    = ParagraphStyle("tier",  fontName="Helvetica-Bold", fontSize=11, textColor=ACCENT, spaceBefore=6, spaceAfter=2, leading=14)
    section_s = ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=13, textColor=BLACK, spaceBefore=12, spaceAfter=2, leading=16)
    question_s= ParagraphStyle("q",     fontName="Helvetica-Bold", fontSize=10.5, textColor=BLACK, leading=14, spaceBefore=4, spaceAfter=2)
    answer_s  = ParagraphStyle("ans",   fontName="Helvetica",      fontSize=9.5,  textColor=DGRAY, leading=13, spaceAfter=2, leftIndent=12)
    summary_s = ParagraphStyle("summary", fontName="Helvetica",    fontSize=10,   textColor=BLACK, leading=14, alignment=TA_LEFT)
    pill_s    = ParagraphStyle("pill",  fontName="Helvetica-Bold", fontSize=8,    textColor=BLACK, leading=10, alignment=TA_CENTER)

    # ── Header (dark band) ────────────────────────────────────────────────────
    name = candidate_name.strip() or "Interview Question Set"
    target = (question_set.target_role or "").strip()
    total_q = question_set.total_questions()

    hdr_left = [Paragraph(f"🎤 Interview Questions — {total_q} Q&amp;A", title_s)]
    if name:
        hdr_left.append(Spacer(1, 3))
        hdr_left.append(Paragraph(f"<font color='#D1D5DB'>{_esc(name)}</font>", sub_s))
    if target:
        hdr_left.append(Paragraph(f"<font color='#A5B4FC'>Target role: {_esc(target)}</font>", sub_s))

    hdr_tbl = Table([[hdr_left]], colWidths=[full_w])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HDR_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
    ]))

    story = [hdr_tbl, Spacer(1, 12)]

    # ── Candidate summary box ─────────────────────────────────────────────────
    if question_set.candidate_summary:
        summary_tbl = Table(
            [[Paragraph(f"<b>Candidate brief:</b> {_esc(question_set.candidate_summary)}", summary_s)]],
            colWidths=[full_w],
        )
        summary_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), BOX_BG),
            ("BOX",          (0,0), (-1,-1), 0.6, BORDER),
            ("LEFTPADDING",  (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING",   (0,0), (-1,-1), 10),
            ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ]))
        story.append(summary_tbl)
        story.append(Spacer(1, 8))

    # ── Per-skill sections (Basic / Intermediate / Expert) ────────────────────
    for sq in question_set.skill_questions:
        if not (sq.basic or sq.intermediate or sq.expert):
            continue

        # Skill name banner
        skill_count = sq.total()
        banner = Table(
            [[Paragraph(
                f"<font color='{ACCENT.hexval()}'>{_esc(sq.skill_name)}</font> "
                f"<font color='{MGRAY.hexval()}' size='10'>· {skill_count} questions</font>",
                skill_s,
            )]],
            colWidths=[full_w],
        )
        banner.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), SKILL_BG),
            ("LEFTPADDING",  (0,0), (-1,-1), 10),
            ("RIGHTPADDING", (0,0), (-1,-1), 10),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ]))
        story.append(banner)
        story.append(Spacer(1, 6))

        # Three tiers
        for tier_name, qs in [("Basic", sq.basic), ("Intermediate", sq.intermediate), ("Expert", sq.expert)]:
            if not qs:
                continue
            story.append(Paragraph(f"<b>{tier_name}</b>", tier_s))
            for idx, q in enumerate(qs, 1):
                for item in _make_question_row(q, idx, full_w, question_s, answer_s, pill_s):
                    story.append(item)

        story.append(Spacer(1, 6))

    # ── Common categories ─────────────────────────────────────────────────────
    common_sections = [
        ("Behavioral / Situational", question_set.behavioral),
        ("Project Deep-Dive",         question_set.project_deep_dive),
        ("System Design",             question_set.system_design),
        ("Role-Specific",             question_set.role_specific),
    ]
    for title, qs in common_sections:
        if not qs:
            continue
        story.append(Paragraph(title, section_s))
        story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=4))
        for idx, q in enumerate(qs, 1):
            for item in _make_question_row(q, idx, full_w, question_s, answer_s, pill_s):
                story.append(item)
        story.append(Spacer(1, 6))

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.4, color=BORDER))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"<font color='{LGRAY.hexval()}' size='8'>"
        f"Generated by AI Resume Builder · {total_q} questions across "
        f"{len(question_set.skill_questions)} skills + 4 common categories · "
        f"answers are AI-suggested rubrics — adapt before live interviews.</font>",
        summary_s,
    ))

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title="Interview Questions",
    )
    doc.build(story)
    return buf.getvalue()
