"""
PDF_Generator.py
================
Purpose:
    Generates downloadable, formatted PDF documents for course syllabi and individual
    module notes using Python's open-source ReportLab library.

Viva Talking Points:
    - Zero Paid Dependencies: Uses the open-source ReportLab library entirely in-memory via io.BytesIO.
    - Security & Ownership: Validates course/module ownership before generating any PDF document.
    - Professional Document Layout: Uses Flowable objects (SimpleDocTemplate, Paragraph,
      Spacer, Table, PageBreak) with customized ParagraphStyles and color schemes.
"""

import io
import re
from flask import Blueprint, send_file, session, flash, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from Database_Connection import query_db
from Login import login_required

pdf_bp = Blueprint("pdf", __name__)


def build_pdf_styles():
    """Returns customized ReportLab paragraph styles."""
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=12,
        spaceAfter=6
    )

    h3_style = ParagraphStyle(
        "DocH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        "DocCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=6
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "h2": h2_style,
        "h3": h3_style,
        "body": body_style,
        "code": code_style
    }


def parse_markdown_to_flowables(text, styles):
    """Converts structured markdown notes into ReportLab Flowable elements."""
    flowables = []
    lines = text.split("\n")
    in_code_block = False
    code_lines = []

    def inline_format(raw_line):
        """Converts markdown bold and inline code to ReportLab XML tags."""
        # Escape any standalone & not part of an entity
        formatted = re.sub(r"&(?!([a-zA-Z]+|#[0-9]+);)", "&amp;", raw_line)
        # Convert **bold** to <b>bold</b>
        formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", formatted)
        # Convert `code` to <font face="Courier">code</font>
        formatted = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', formatted)
        return formatted

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                # End of code block
                code_text = "<br/>".join(
                    code_lines
                ).replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
                flowables.append(Paragraph(code_text, styles["code"]))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            flowables.append(Spacer(1, 4))
            continue

        if stripped.startswith("# "):
            flowables.append(Paragraph(inline_format(stripped[2:]), styles["title"]))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(inline_format(stripped[3:]), styles["h2"]))
        elif stripped.startswith("### "):
            flowables.append(Paragraph(inline_format(stripped[4:]), styles["h3"]))
        elif stripped.startswith("---"):
            flowables.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=10))
        elif stripped.startswith("• ") or stripped.startswith("* ") or stripped.startswith("- "):
            bullet_text = f"&bull; {inline_format(stripped[2:])}"
            flowables.append(Paragraph(bullet_text, styles["body"]))
        else:
            flowables.append(Paragraph(inline_format(stripped), styles["body"]))

    return flowables


@pdf_bp.route("/download_module_pdf/<int:module_id>")
@login_required
def download_module_pdf(module_id):
    """Generates and downloads a PDF containing comprehensive notes for a specific module."""
    user_id = session["user_id"]

    mod = query_db("""
        SELECT m.*, c.title as course_title, c.topic, c.difficulty, c.duration, c.user_id
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,), one=True)

    if not mod or mod["user_id"] != user_id:
        flash("Unauthorized or module not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = build_pdf_styles()
    story = []

    # Header section
    story.append(Paragraph(f"Course: {mod['course_title']}", styles["subtitle"]))
    story.append(Paragraph(f"Module {mod['module_number']}: {mod['title']}", styles["title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # Notes content
    notes_flowables = parse_markdown_to_flowables(mod["notes"], styles)
    story.extend(notes_flowables)

    doc.build(story)
    buffer.seek(0)

    filename = f"Module_{mod['module_number']}_Notes.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )


@pdf_bp.route("/download_course_pdf/<int:course_id>")
@login_required
def download_course_pdf(course_id):
    """Generates and downloads a complete course syllabus and all module notes in one PDF."""
    user_id = session["user_id"]

    course = query_db(
        "SELECT * FROM courses WHERE id = ? AND user_id = ?",
        (course_id, user_id),
        one=True
    )
    if not course:
        flash("Unauthorized or course not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    modules = query_db(
        "SELECT * FROM modules WHERE course_id = ? ORDER BY module_number ASC",
        (course_id,)
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = build_pdf_styles()
    story = []

    # Cover Header
    story.append(Paragraph(course["title"], styles["title"]))
    meta_info = f"<b>Topic:</b> {course['topic']} &nbsp;|&nbsp; <b>Level:</b> {course['difficulty']} &nbsp;|&nbsp; <b>Duration:</b> {course['duration']} &nbsp;|&nbsp; <b>Total Modules:</b> {course['module_count']}"
    story.append(Paragraph(meta_info, styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceAfter=15))

    # Table of Contents
    story.append(Paragraph("Course Syllabus Outline", styles["h2"]))
    table_data = [["Module #", "Module Title"]]
    for m in modules:
        table_data.append([f"Module {m['module_number']}", m["title"]])

    t = Table(table_data, colWidths=[80, 440])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Modules detail sections
    for i, m in enumerate(modules):
        story.append(PageBreak())
        story.append(Paragraph(f"Module {m['module_number']}: {m['title']}", styles["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        story.extend(parse_markdown_to_flowables(m["notes"], styles))

    doc.build(story)
    buffer.seek(0)

    filename = f"{course['topic']}_Complete_Course_Syllabus.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
