"""
5 Professional Resume Templates.
T1: Dark header, serif body, red accent (working - unchanged)
T2: FIXED - Dark top band + two-column grey sidebar (Image 2 style)
T3: FIXED - Centered name, icon contact row, thin rules (Image 3 style)  
T4: FIXED - Left-right header, compact rules, IIIT style (Image 4 style)
T5: Executive bold teal header (working - unchanged)
"""
from __future__ import annotations
import io, re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, BaseDocTemplate, PageTemplate, Frame, FrameBreak,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

W, H   = A4
BLACK  = colors.HexColor("#111111")
WHITE  = colors.white
DGRAY  = colors.HexColor("#333333")
MGRAY  = colors.HexColor("#666666")
LGRAY  = colors.HexColor("#999999")
XLGRAY = colors.HexColor("#CCCCCC")


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clean(text):
    for pat, rep in [
        (r"\*\*(.*?)\*\*", r"\1"),
        (r"\*(.*?)\*",     r"\1"),
        (r"`(.*?)`",       r"\1"),
        (r"#{1,6}\s*",     ""),
        (r"\[(.*?)\]\(.*?\)", r"\1"),
    ]:
        text = re.sub(pat, rep, text)
    return text.strip()


def parse_sections(md):
    sections, current, lines = {}, "header", []
    for line in md.split("\n"):
        s = line.strip()
        if s.startswith("## "):
            sections[current] = "\n".join(lines).strip()
            key = re.sub(r"[^a-z0-9]+", "_", s[3:].lower()).strip("_")
            current, lines = key, []
        elif s.startswith("# "):
            sections[current] = "\n".join(lines).strip()
            current, lines = "header", [s[2:]]
        else:
            lines.append(line)
    sections[current] = "\n".join(lines).strip()
    return sections


SECTION_ORDER = [
    ("summary",                "Professional Summary"),
    ("professional_summary",   "Professional Summary"),
    ("objective",              "Objective"),
    ("experience",             "Work Experience"),
    ("work_experience",        "Work Experience"),
    ("professional_experience","Work Experience"),
    ("education",              "Education"),
    ("technical_skills",       "Technical Skills"),
    ("skills",                 "Technical Skills"),
    ("core_competencies",      "Technical Skills"),
    ("projects",               "Projects"),
    ("key_projects",           "Projects"),
    ("personal_projects",      "Projects"),
    ("certifications",         "Certifications"),
    ("certifications___awards","Certifications"),
    ("achievements",           "Achievements"),
    ("positions_of_responsibility", "Positions of Responsibility"),
    ("publications",           "Publications"),
    ("awards",                 "Awards"),
    ("volunteering",           "Volunteering"),
]


def ordered(sections):
    seen, result = set(), []
    for key, display in SECTION_ORDER:
        for sk, content in sections.items():
            if key in sk and content.strip() and display not in seen:
                result.append((display, content.strip()))
                seen.add(display)
                break
    return result


def contact_str(pi, sep="  |  "):
    return sep.join(esc(p) for p in [pi.get("mobile",""), pi.get("email",""), pi.get("location","")] if p)


def link_para(pi, color="#0A66C2"):
    parts = []
    if pi.get("linkedin"): parts.append(f'<a href="{pi["linkedin"]}" color="{color}">LinkedIn</a>')
    if pi.get("github"):   parts.append(f'<a href="{pi["github"]}" color="{color}">GitHub</a>')
    return parts


def render(story, content, body_s, bul_s, bold_s, bchar="•"):
    for line in content.split("\n"):
        raw = line.strip()
        if not raw:
            story.append(Spacer(1, 3))
            continue
        if raw.startswith(("- ", "* ", "• ")):
            story.append(Paragraph(f"{bchar}  {esc(clean(raw[2:]))}", bul_s))
        elif re.match(r"^\*\*.+\*\*", raw) or re.match(r"^#{1,4}\s", raw):
            story.append(Paragraph(esc(clean(raw)), bold_s))
        else:
            story.append(Paragraph(esc(clean(raw)), body_s))


# ══════════════════════════════════════════════════════════════════════════════
# T1 — SERIF CLASSIC (unchanged — working)
# ══════════════════════════════════════════════════════════════════════════════
def t1_serif_classic(pi, sections):
    buf  = io.BytesIO()
    DARK = colors.HexColor("#2D2D2D")
    RED  = colors.HexColor("#C0392B")

    NS = ParagraphStyle("n1", fontName="Times-Bold",  fontSize=24, textColor=WHITE, alignment=TA_CENTER, spaceAfter=0, leading=26)
    RS = ParagraphStyle("r1", fontName="Times-Roman", fontSize=10, textColor=colors.HexColor("#BBBBBB"), alignment=TA_CENTER, spaceAfter=0)
    CS = ParagraphStyle("c1", fontName="Times-Roman", fontSize=9.5, textColor=MGRAY, alignment=TA_CENTER, spaceAfter=2)
    LS = ParagraphStyle("l1", fontName="Times-Roman", fontSize=9.5, textColor=MGRAY, alignment=TA_CENTER, spaceAfter=0)
    SS = ParagraphStyle("s1", fontName="Times-Bold",  fontSize=14, textColor=RED, spaceBefore=10, spaceAfter=0)
    BS = ParagraphStyle("b1", fontName="Times-Roman", fontSize=10, textColor=BLACK, leading=15, spaceAfter=2, alignment=TA_JUSTIFY)
    BL = ParagraphStyle("bl1",fontName="Times-Roman", fontSize=10, textColor=BLACK, leading=15, leftIndent=14, firstLineIndent=-8, spaceAfter=2)
    BH = ParagraphStyle("bh1",fontName="Times-Bold",  fontSize=10.5, textColor=BLACK, spaceAfter=1, spaceBefore=5)

    fn = esc(pi.get("first_name","")); ln = esc(pi.get("last_name",""))
    role_hint = ""
    for sk, sv in sections.items():
        if "experience" in sk and sv.strip():
            for line in sv.split("\n"):
                c = clean(line.strip())
                if c and len(c) > 4: role_hint = c[:70]; break
            break

    hdr_content = [Paragraph(f'{fn} <b>{ln}</b>', NS)]
    if role_hint:
        hdr_content.append(Spacer(1, 3))
        hdr_content.append(Paragraph(esc(role_hint), RS))

    hdr_tbl = Table([[hdr_content]], colWidths=[W - 4*cm])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 18),
        ("BOTTOMPADDING", (0,0),(-1,-1), 16),
        ("LEFTPADDING",   (0,0),(-1,-1), 16),
        ("RIGHTPADDING",  (0,0),(-1,-1), 16),
    ]))

    story = [hdr_tbl, Spacer(1, 8)]
    cont = contact_str(pi)
    lp   = link_para(pi, "#C0392B")
    if cont: story.append(Paragraph(cont, CS))
    if lp:   story.append(Paragraph("  |  ".join(lp), LS))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=XLGRAY))

    for title, content in ordered(sections):
        story.append(Spacer(1, 4))
        story.append(Paragraph(title, SS))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=0.4, color=XLGRAY))
        story.append(Spacer(1, 3))
        render(story, content, BS, BL, BH)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=1.5*cm, bottomMargin=1.8*cm)
    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# T2 — FIXED: Dark top band + light grey sidebar + white main (Image 2 style)
# Full dark header across top, grey left column for About/Education/Links/Skills
# White right column for Experience, Projects, Volunteering
# ══════════════════════════════════════════════════════════════════════════════
def t2_dark_band_twocol(pi, sections, raw_skills):
    buf      = io.BytesIO()
    DARK     = colors.HexColor("#1A1A1A")   # near-black header
    SB_BG    = colors.HexColor("#F2F2F2")   # light grey sidebar
    SB_RULE  = colors.HexColor("#CCCCCC")
    MAIN_BG  = colors.white

    inner_w  = W - 4*cm                    # usable width for full-width header
    sb_w     = 5.8*cm
    main_w   = W - sb_w - 1.2*cm
    gap      = 0.25*cm

    # ── Full-width header styles
    HN = ParagraphStyle("hn2",  fontName="Helvetica-Bold", fontSize=18,
                         textColor=WHITE, spaceAfter=1, leading=20)
    HC = ParagraphStyle("hc2",  fontName="Helvetica",      fontSize=8,
                         textColor=colors.HexColor("#AAAAAA"), spaceAfter=0, alignment=TA_RIGHT)

    # ── Sidebar styles
    SBH = ParagraphStyle("sbh2", fontName="Helvetica-Bold", fontSize=9,
                          textColor=BLACK, spaceBefore=10, spaceAfter=0,
                          textTransform="uppercase", letterSpacing=0.8)
    SBB = ParagraphStyle("sbb2", fontName="Helvetica",      fontSize=8.5,
                          textColor=DGRAY, leading=13, spaceAfter=2)
    SBL = ParagraphStyle("sbl2", fontName="Helvetica",      fontSize=8.5,
                          textColor=DGRAY, leading=13, spaceAfter=2,
                          leftIndent=6)

    # ── Main area styles
    MSH = ParagraphStyle("msh2", fontName="Helvetica-Bold", fontSize=10,
                          textColor=BLACK, spaceBefore=8, spaceAfter=0,
                          textTransform="uppercase")
    MSB = ParagraphStyle("msb2", fontName="Helvetica",      fontSize=9,
                          textColor=BLACK, leading=13, spaceAfter=2)
    MSL = ParagraphStyle("msl2", fontName="Helvetica",      fontSize=9,
                          textColor=BLACK, leading=13, leftIndent=10,
                          firstLineIndent=-6, spaceAfter=2)
    MSE = ParagraphStyle("mse2", fontName="Helvetica-Bold", fontSize=9.5,
                          textColor=BLACK, spaceAfter=1, spaceBefore=5)

    fn        = pi.get("first_name", "")
    ln        = pi.get("last_name", "")
    full_name = f"{fn} {ln}".strip()

    # ── Build full-width header table
    contact_right = []
    for item in [pi.get("email",""), pi.get("mobile",""), pi.get("location","")]:
        if item:
            contact_right.append(esc(item))
    contact_html = "<br/>".join(
        f'<font size="8" color="#AAAAAA">{x}</font>' for x in contact_right
    )

    name_cell    = Paragraph(f'<font size="18" color="white"><b>{esc(full_name)}</b></font>',
                             ParagraphStyle("_hn"))
    contact_cell = Paragraph(contact_html, HC)

    hdr_tbl = Table(
        [[name_cell, contact_cell]],
        colWidths=[inner_w * 0.62, inner_w * 0.38],
    )
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 16),
        ("BOTTOMPADDING", (0,0), (-1,-1), 16),
        ("LEFTPADDING",   (0,0), (0,-1),  14),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 14),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))

    # ── Sidebar content
    sb = []

    # About Me from summary
    about_text = ""
    for sk, sv in sections.items():
        if "summary" in sk and sv.strip():
            about_text = sv.strip(); break
    if about_text:
        sb.append(Paragraph("ABOUT ME", SBH))
        sb.append(HRFlowable(width="100%", thickness=0.5, color=SB_RULE))
        sb.append(Spacer(1, 3))
        for line in about_text.split("\n"):
            c = clean(line.strip())
            if c:
                sb.append(Paragraph(esc(c), SBB))

    # Education
    for sk, sv in sections.items():
        if "education" in sk and sv.strip():
            sb.append(Paragraph("EDUCATION", SBH))
            sb.append(HRFlowable(width="100%", thickness=0.5, color=SB_RULE))
            sb.append(Spacer(1, 3))
            for line in sv.split("\n"):
                c = clean(line.strip())
                if c:
                    if line.strip().startswith(("- ","* ")):
                        sb.append(Paragraph(f"• {esc(c)}", SBL))
                    else:
                        sb.append(Paragraph(esc(c), SBB))
            break

    # Links
    lps = link_para(pi, "#1A1A1A")
    if lps:
        sb.append(Paragraph("LINKS", SBH))
        sb.append(HRFlowable(width="100%", thickness=0.5, color=SB_RULE))
        sb.append(Spacer(1, 3))
        if pi.get("github"):
            sb.append(Paragraph(f'<a href="{pi["github"]}" color="#333333">🔗 GitHub</a>', SBB))
        if pi.get("linkedin"):
            sb.append(Paragraph(f'<a href="{pi["linkedin"]}" color="#333333">🔗 LinkedIn</a>', SBB))

    # Honors / Certifications
    for sk, sv in sections.items():
        if "certif" in sk and sv.strip():
            sb.append(Paragraph("HONORS &amp; AWARDS", SBH))
            sb.append(HRFlowable(width="100%", thickness=0.5, color=SB_RULE))
            sb.append(Spacer(1, 3))
            for line in sv.split("\n"):
                c = clean(line.strip())
                if c: sb.append(Paragraph(esc(c), SBB))
            break

    # Skills / Interests
    if raw_skills:
        sb.append(Paragraph("HOBBIES &amp; SKILLS", SBH))
        sb.append(HRFlowable(width="100%", thickness=0.5, color=SB_RULE))
        sb.append(Spacer(1, 3))
        for sk in raw_skills:
            sn = sk.get("name", "").strip()
            if sn: sb.append(Paragraph(f"• {esc(sn)}", SBL))

    # ── Main content
    SKIP = {
        "summary", "professional_summary", "education",
        "technical_skills", "skills", "certifications",
        "certifications___awards",
    }
    main = []
    for title, content in ordered(sections):
        key_check = title.lower().replace(" ", "_")
        if any(k in key_check for k in SKIP):
            continue
        main.append(Paragraph(title.upper(), MSH))
        main.append(HRFlowable(width="100%", thickness=0.8, color=BLACK, spaceAfter=3))
        render(main, content, MSB, MSL, MSE, bchar="•")
        main.append(Spacer(1, 4))

    # ── Build with frames
    def draw_bg(c, doc):
        c.saveState()
        # Sidebar grey background
        c.setFillColor(SB_BG)
        c.rect(0, 0, sb_w, H, fill=1, stroke=0)
        c.restoreState()

    # The header goes in a frame that spans the full width first
    # We use a single-column approach: header top, then two columns below

    # Frame for sidebar
    fr_sb   = Frame(
        0.25*cm, 1.5*cm, sb_w - 0.25*cm, H - 4.5*cm,
        leftPadding=10, rightPadding=8, topPadding=10, bottomPadding=0,
    )
    # Frame for main
    fr_main = Frame(
        sb_w + gap, 1.5*cm, main_w, H - 4.5*cm,
        leftPadding=8, rightPadding=4, topPadding=10, bottomPadding=0,
    )

    tpl = PageTemplate(id="tp2", frames=[fr_sb, fr_main], onPage=draw_bg)

    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=0, rightMargin=0,
        topMargin=0, bottomMargin=1.5*cm,
    )
    doc.addPageTemplates([tpl])

    # Build: header (full width) then sidebar content then frame break then main
    # We need the header to appear above both columns.
    # Strategy: put header in a separate single-frame page first, then two-col.
    # Simpler: use a top Frame for header only.

    # Rebuild with 3 frames: top header, left sidebar, right main
    fr_header = Frame(
        0, H - 4.0*cm, W, 3.8*cm,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    fr_sb2 = Frame(
        0.25*cm, 1.5*cm, sb_w - 0.25*cm, H - 5.8*cm,
        leftPadding=10, rightPadding=8, topPadding=8, bottomPadding=0,
    )
    fr_main2 = Frame(
        sb_w + gap, 1.5*cm, main_w, H - 5.8*cm,
        leftPadding=8, rightPadding=4, topPadding=8, bottomPadding=0,
    )

    tpl2 = PageTemplate(id="tp2b", frames=[fr_header, fr_sb2, fr_main2], onPage=draw_bg)
    doc2  = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=0, rightMargin=0,
        topMargin=0, bottomMargin=1.5*cm,
    )
    doc2.addPageTemplates([tpl2])

    # Header table padded to full width
    hdr_full = Table([[name_cell, contact_cell]], colWidths=[W*0.60, W*0.40])
    hdr_full.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        ("LEFTPADDING",   (0,0), (0,-1),  16),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 16),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))

    flow = [hdr_full, FrameBreak()] + sb + [FrameBreak()] + main
    doc2.build(flow)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# T3 — FIXED: Centered name, icon contact row, thin rules (Image 3 style)
# Pure white, name centered large, contact icons in one row, small-caps headings
# ══════════════════════════════════════════════════════════════════════════════
def t3_centered_academic(pi, sections):
    buf  = io.BytesIO()
    NAVY = colors.HexColor("#1A237E")   # dark navy for headings

    # Styles
    NS = ParagraphStyle(
        "n3", fontName="Times-Roman", fontSize=22,
        textColor=BLACK, alignment=TA_CENTER, spaceAfter=0, leading=24,
    )
    # Contact row — navy links, black text
    CS = ParagraphStyle(
        "c3", fontName="Helvetica", fontSize=9,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=4, leading=13,
    )
    # Section heading — small caps style using uppercase bold serif
    SS = ParagraphStyle(
        "s3", fontName="Times-Bold", fontSize=11,
        textColor=BLACK, spaceBefore=10, spaceAfter=0,
        # We simulate small caps by using uppercase in text
    )
    BS = ParagraphStyle(
        "b3", fontName="Times-Roman", fontSize=10,
        textColor=BLACK, leading=15, spaceAfter=2,
    )
    BL = ParagraphStyle(
        "bl3", fontName="Times-Roman", fontSize=10,
        textColor=BLACK, leading=15, leftIndent=14,
        firstLineIndent=-8, spaceAfter=2,
    )
    BH = ParagraphStyle(
        "bh3", fontName="Times-Bold", fontSize=10.5,
        textColor=BLACK, spaceAfter=1, spaceBefore=5,
    )
    # Right-aligned date for experience entries
    DR = ParagraphStyle(
        "dr3", fontName="Times-Roman", fontSize=10,
        textColor=MGRAY, alignment=TA_RIGHT, spaceAfter=0,
    )

    fn = pi.get("first_name", ""); ln = pi.get("last_name", "")
    full = f"{fn} {ln}".strip()

    story = []

    # ── Name (centered, large)
    story.append(Paragraph(esc(full), NS))
    story.append(Spacer(1, 8))  # space under name

    # ── Contact row with icons (like Image 3)
    cp = []
    if pi.get("github"):
        cp.append(f'<a href="{pi["github"]}" color="#1A237E">🔗 {esc(pi["github"].rstrip("/").split("/")[-1])}</a>')
    if pi.get("linkedin"):
        cp.append(f'<a href="{pi["linkedin"]}" color="#1A237E">🔗 LinkedIn</a>')
    if pi.get("mobile"):
        cp.append(f'📞 {esc(pi["mobile"])}')
    if pi.get("email"):
        cp.append(f'✉ {esc(pi["email"])}')
    if pi.get("location"):
        cp.append(f'📍 {esc(pi["location"])}')

    if cp:
        story.append(Paragraph("  |  ".join(cp), CS))

    # ── Full-width rule (like Image 3 — single line below contact)
    story.append(HRFlowable(width="100%", thickness=0.8, color=BLACK))
    story.append(Spacer(1, 2))

    # ── Sections with small-caps headings and thin rules
    for title, content in ordered(sections):
        # Heading in small-caps style (Times Bold uppercase)
        story.append(Paragraph(title, SS))   # title already capitalised by display name
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BLACK))
        story.append(Spacer(1, 3))
        render(story, content, BS, BL, BH, bchar="–")
        story.append(Spacer(1, 4))

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
    )
    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# T4 — FIXED: IIIT-style compact (Image 4 style)
# Name + details top-left, contact top-right, Education/Experience with bullet rules
# Compact, formal, black-and-white, small-caps section headings
# ══════════════════════════════════════════════════════════════════════════════
def t4_iiit_compact(pi, sections):
    buf   = io.BytesIO()
    inner = W - 4.0*cm  # usable width

    # ── Styles
    # Name — larger, bold
    NS = ParagraphStyle(
        "n4", fontName="Helvetica-Bold", fontSize=18,
        textColor=BLACK, spaceAfter=0, leading=20,
    )
    # Sub-details under name (programme, institution)
    SD = ParagraphStyle(
        "sd4", fontName="Helvetica", fontSize=9,
        textColor=BLACK, spaceAfter=0, leading=12,
    )
    # Right column contact
    RC = ParagraphStyle(
        "rc4", fontName="Helvetica", fontSize=9,
        textColor=BLACK, alignment=TA_RIGHT, spaceAfter=1, leading=12,
    )
    # Section heading — small caps (Times Bold, uppercase)
    SS = ParagraphStyle(
        "ss4", fontName="Times-Bold", fontSize=11,
        textColor=BLACK, spaceBefore=6, spaceAfter=0,
        # Simulated small caps via uppercase text
    )
    # Body
    BS = ParagraphStyle(
        "bs4", fontName="Times-Roman", fontSize=10,
        textColor=BLACK, leading=14, spaceAfter=1,
    )
    # Bullets
    BL = ParagraphStyle(
        "bl4", fontName="Times-Roman", fontSize=10,
        textColor=BLACK, leading=14, leftIndent=16,
        firstLineIndent=-10, spaceAfter=1,
    )
    # Bold entry header (company/institution name)
    BH = ParagraphStyle(
        "bh4", fontName="Times-Bold", fontSize=10.5,
        textColor=BLACK, spaceAfter=0, spaceBefore=4,
    )
    # Italic sub-entry (role, degree)
    IT = ParagraphStyle(
        "it4", fontName="Times-Italic", fontSize=10,
        textColor=BLACK, spaceAfter=1,
    )
    # Right-aligned date
    DR = ParagraphStyle(
        "dr4", fontName="Times-Roman", fontSize=10,
        textColor=BLACK, alignment=TA_RIGHT, spaceAfter=0,
    )

    fn = pi.get("first_name", ""); ln = pi.get("last_name", "")
    full = f"{fn} {ln}".strip()

    # ── Header: name block left, contact right
    left_items = [
        Paragraph(f"<b>{esc(full)}</b>", NS),
        Spacer(1, 4),
    ]
    # Add location as sub-detail if present
    if pi.get("location"):
        left_items.append(Paragraph(esc(pi["location"]), SD))

    right_items = []
    if pi.get("mobile"):
        right_items.append(Paragraph(f"📞 {esc(pi['mobile'])}", RC))
    if pi.get("email"):
        right_items.append(Paragraph(f"✉ {esc(pi['email'])}", RC))
    if pi.get("github"):
        right_items.append(Paragraph(
            f'<a href="{pi["github"]}" color="#111111">🔗 GitHub</a>', RC))
    if pi.get("linkedin"):
        right_items.append(Paragraph(
            f'<a href="{pi["linkedin"]}" color="#111111">🔗 LinkedIn</a>', RC))

    if right_items:
        hdr = Table(
            [[left_items, right_items]],
            colWidths=[inner * 0.58, inner * 0.42],
        )
        hdr.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 0),
            ("BOTTOMPADDING",(0,0), (-1,-1), 0),
            ("LEFTPADDING",  (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ]))
    else:
        hdr = Table([[left_items]], colWidths=[inner])
        hdr.setStyle(TableStyle([
            ("TOPPADDING",   (0,0), (-1,-1), 0),
            ("BOTTOMPADDING",(0,0), (-1,-1), 0),
            ("LEFTPADDING",  (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ]))

    story = [
        hdr,
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1.5, color=BLACK),
        Spacer(1, 4),
    ]

    # ── Sections with IIIT-style small-caps headings
    for title, content in ordered(sections):
        # Small-caps heading (simulated: Times Bold uppercase)
        # Add the thin rule below as in Image 4
        story.append(Paragraph(title.upper(), SS))
        story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.6, color=BLACK))
        story.append(Spacer(1, 3))

        # Render content
        for line in content.split("\n"):
            raw = line.strip()
            if not raw:
                story.append(Spacer(1, 2))
                continue
            if raw.startswith(("- ", "* ", "• ")):
                txt = clean(raw[2:])
                story.append(Paragraph(f"– {esc(txt)}", BL))
            elif re.match(r"^\*\*.+\*\*", raw) or re.match(r"^#{1,4}\s", raw):
                txt = clean(raw)
                story.append(Paragraph(f"•{esc(txt)}", BH))
            else:
                story.append(Paragraph(esc(clean(raw)), BS))

        story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.8*cm,  bottomMargin=1.8*cm,
    )
    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# T5 — EXECUTIVE BOLD (unchanged — working)
# ══════════════════════════════════════════════════════════════════════════════
def t5_executive_bold(pi, sections, raw_skills):
    buf    = io.BytesIO()
    TEAL   = colors.HexColor("#0F4C5C")
    ORANGE = colors.HexColor("#E8680A")
    inner  = W - 4*cm

    NS  = ParagraphStyle("n5",  fontName="Helvetica-Bold", fontSize=28,
                          textColor=WHITE, spaceAfter=2, leading=30)
    RS  = ParagraphStyle("r5",  fontName="Helvetica",      fontSize=10,
                          textColor=colors.HexColor("#7DD3E0"), spaceAfter=0)
    CS  = ParagraphStyle("c5",  fontName="Helvetica",      fontSize=8.5,
                          textColor=colors.HexColor("#A0C8D0"), spaceAfter=0)
    SS  = ParagraphStyle("s5",  fontName="Helvetica-Bold", fontSize=10,
                          textColor=WHITE, spaceAfter=0)
    BS  = ParagraphStyle("b5",  fontName="Helvetica",      fontSize=9.5,
                          textColor=BLACK, leading=14, spaceAfter=2)
    BL  = ParagraphStyle("bl5", fontName="Helvetica",      fontSize=9.5,
                          textColor=BLACK, leading=14, leftIndent=14,
                          firstLineIndent=-8, spaceAfter=2)
    BH  = ParagraphStyle("bh5", fontName="Helvetica-Bold", fontSize=10,
                          textColor=TEAL, spaceAfter=1, spaceBefore=5)

    fn   = pi.get("first_name", ""); ln = pi.get("last_name", "")
    full = f"{fn} {ln}".strip()

    role_hint = ""
    for sk, sv in sections.items():
        if "experience" in sk and sv.strip():
            for line in sv.split("\n"):
                c = clean(line.strip())
                if c and len(c) > 4:
                    role_hint = c[:70]; break
            break

    hdr_left = [Paragraph(f"<b>{esc(full)}</b>", NS), Spacer(1, 5)]
    if role_hint:
        hdr_left.append(Paragraph(esc(role_hint), RS))

    hdr_right = []
    for item in [pi.get("mobile",""), pi.get("email",""), pi.get("location","")]:
        if item: hdr_right.append(Paragraph(esc(item), CS))
    for lp in link_para(pi, "#7DD3E0"):
        hdr_right.append(Paragraph(lp, CS))

    hdr_tbl = Table([[hdr_left, hdr_right]], colWidths=[inner*0.6, inner*0.4])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), TEAL),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (0,-1),  16),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 16),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))

    story = [hdr_tbl, Spacer(1, 10)]

    for title, content in ordered(sections):
        sec_bar = Table(
            [[Paragraph(f"<b>{title.upper()}</b>", SS)]],
            colWidths=[inner],
        )
        sec_bar.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), ORANGE),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ]))
        story.append(sec_bar)
        story.append(Spacer(1, 5))
        render(story, content, BS, BL, BH, bchar="▪")
        story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.8*cm,
    )
    doc.build(story)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────
def generate_resume_pdf(profile_data, resume_draft, template_id=0):
    pi       = profile_data.get("personal_info", {})
    sections = parse_sections(resume_draft)
    skills   = profile_data.get("skills", [])
    tid      = min(max(int(template_id), 0), 4)

    if tid == 0: return t1_serif_classic(pi, sections)
    if tid == 1: return t2_dark_band_twocol(pi, sections, skills)
    if tid == 2: return t3_centered_academic(pi, sections)
    if tid == 3: return t4_iiit_compact(pi, sections)
    if tid == 4: return t5_executive_bold(pi, sections, skills)
    return t1_serif_classic(pi, sections)
