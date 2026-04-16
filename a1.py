"""
Student Mark Slip Generator - Fixed Version
- Reads Anna University Result Sheet PDF (horizontal format)
- Extracts logos embedded in the PDF (Anna University + ACOE)
- Each row = one student, subject grades in columns
- Generates formatted A4 slips with proper course names
- Combines into one print-ready PDF

Usage:
    pip install pdfplumber reportlab pypdf
    python generate_slips.py --input marks.pdf --outdir slips
"""

import os
import re
import argparse
import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image as RLImage
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pypdf import PdfReader, PdfWriter


# ── Known Course Name Map ─────────────────────────────────────────────────────
COURSE_NAME_MAP = {
    "CS23101": "Computational Thinking",
    "CS23C04": "Programming in C",
    "EE23C02": "Fundamentals of Electrical and Electronics Engineering",
    "EN23C01": "Foundation English",
    "MA23C01": "Matrices and Calculus",
    "PH23C01": "Engineering Physics",
    "UC23H01": "Heritage of Tamils / Tamil Ilakanam",
}




# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    return {
        "college_name": ParagraphStyle(
            "college_name", fontName="Helvetica-Bold", fontSize=12,
            textColor=colors.black, alignment=TA_CENTER, leading=16
        ),
        "college_sub": ParagraphStyle(
            "college_sub", fontName="Helvetica", fontSize=9,
            textColor=colors.black, alignment=TA_CENTER, leading=12
        ),
        "section_title": ParagraphStyle(
            "section_title", fontName="Helvetica-Bold", fontSize=10,
            textColor=colors.black, alignment=TA_CENTER,
            leading=13, spaceAfter=3
        ),
        "label": ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=8.5,
            textColor=colors.black, leading=11
        ),
        "value": ParagraphStyle(
            "value", fontName="Helvetica", fontSize=8.5,
            textColor=colors.black, leading=11
        ),
        "th": ParagraphStyle(
            "th", fontName="Helvetica-Bold", fontSize=8,
            textColor=colors.black, alignment=TA_CENTER, leading=10
        ),
        "td": ParagraphStyle(
            "td", fontName="Helvetica", fontSize=8,
            textColor=colors.black, alignment=TA_LEFT, leading=10
        ),
        "td_center": ParagraphStyle(
            "td_center", fontName="Helvetica", fontSize=8,
            textColor=colors.black, alignment=TA_CENTER, leading=10
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica-Oblique", fontSize=7,
            textColor=colors.black, alignment=TA_CENTER, leading=9
        ),
        "sign_label": ParagraphStyle(
            "sign_label", fontName="Helvetica", fontSize=8,
            textColor=colors.black, alignment=TA_CENTER, leading=10
        ),
    }


def load_logo(path, max_width=25*mm, max_height=25*mm):
    if path and os.path.exists(path):
        try:
            return RLImage(path, width=max_width, height=max_height)
        except Exception:
            pass
    return Spacer(1, max_height)


# ── PDF Data Extraction ───────────────────────────────────────────────────────
def extract_students(pdf_path):
    """
    Parse Anna University Result Sheet PDF (horizontal format).
    Header row has subject codes; each data row = one student.
    """
    students = []
    meta = {
        "campus":     "Madras Institute of Technology",
        "dept":       "68 - Computer Technology",
        "branch":     "503 - B.E Computer Science and Engineering",
        "semester":   "1",
        "session":    "NOV - 2025",
        "mode":       "Full Time",
        "regulation": "2023",
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text  = page.extract_text() or ""
            lines = [l.strip() for l in text.splitlines() if l.strip()]

            for line in lines:
                if re.search(r"campus\s*:", line, re.I):
                    m = re.search(r"campus\s*:\s*(.+)", line, re.I)
                    if m: meta["campus"] = m.group(1).strip()
                if re.search(r"department\s*:", line, re.I):
                    m = re.search(r"department\s*:\s*(.+)", line, re.I)
                    if m: meta["dept"] = m.group(1).strip()
                if re.search(r"session\s*:", line, re.I):
                    m = re.search(r"session\s*:\s*(.+)", line, re.I)
                    if m: meta["session"] = m.group(1).strip()
                if re.search(r"semester\s*:\s*(\d)", line, re.I):
                    m = re.search(r"semester\s*:\s*(\d)", line, re.I)
                    if m: meta["semester"] = m.group(1).strip()
                if re.search(r"regulation\s*:", line, re.I):
                    m = re.search(r"regulation\s*:\s*(\d+)", line, re.I)
                    if m: meta["regulation"] = m.group(1).strip()
                if re.search(r"mode\s*:", line, re.I):
                    m = re.search(r"mode\s*:\s*(.+)", line, re.I)
                    if m: meta["mode"] = m.group(1).strip()
                if re.search(r"branch\s*:", line, re.I):
                    m = re.search(r"branch\s*:\s*(.+)", line, re.I)
                    if m: meta["branch"] = m.group(1).strip()

            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Find header row with subject codes
                header_row_idx = None
                for idx, row in enumerate(table):
                    cells = [str(c).strip() if c else "" for c in row]
                    subj_cols = [c for c in cells if re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{2,}$", c.strip().upper())]
                    if len(subj_cols) >= 3:
                        header_row_idx = idx
                        break

                if header_row_idx is None:
                    continue

                header       = [str(c).strip() if c else "" for c in table[header_row_idx]]
                lower_header = [c.lower() for c in header]

                reg_idx  = next((i for i, c in enumerate(lower_header) if "register" in c), 1)
                name_idx = next((i for i, c in enumerate(lower_header) if "name" in c), 2)

                subject_cols = [
                    (i, cell) for i, cell in enumerate(header)
                    if re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{2,}$", str(cell).strip().upper())
                ]
                gpa_idx = next(
                    (i for i, c in enumerate(lower_header) if c in ["gpa", "cgpa"]), None
                )

                for row in table[header_row_idx + 1:]:
                    if not row:
                        continue
                    cells = [str(c).strip() if c else "" for c in row]
                    if not cells[0] or not re.match(r"^\d+$", cells[0].strip()):
                        continue

                    reg_no = cells[reg_idx]  if reg_idx  < len(cells) else ""
                    name   = cells[name_idx] if name_idx < len(cells) else ""
                    gpa    = cells[gpa_idx]  if gpa_idx is not None and gpa_idx < len(cells) else ""

                    if not reg_no and not name:
                        continue

                    subjects = []
                    for col_idx, code in subject_cols:
                        grade = cells[col_idx].strip() if col_idx < len(cells) else ""
                        if not grade:
                            continue
                        result = "Reappear" if grade.upper() in ["U", "AB", "F", "RA", "SA"] else "Pass"
                        subjects.append({
                            "code":   code,
                            "name":   COURSE_NAME_MAP.get(code, code),
                            "grade":  grade,
                            "result": result,
                        })

                    if subjects:
                        students.append({
                            "reg_no":   reg_no,
                            "name":     name,
                            "gpa":      gpa,
                            "subjects": subjects,
                        })

    return students, meta


# ── Build Single Slip ─────────────────────────────────────────────────────────
def build_slip(student, meta, out_path, left_logo_path=None, right_logo_path=None):
    S      = make_styles()
    W, H   = A4
    usable = W - 30 * mm

    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )
    story = []

    left_logo = load_logo(left_logo_path)
    right_logo = load_logo(right_logo_path)

    center_para = Paragraph(
        f"<b>Anna University, Chennai - 600 025</b><br/>"
        f"Additional Controller of Examinations<br/>"
        f"University Departments<br/>"
        f"<b>{meta['campus'].upper()}</b><br/>"
        f"{meta['dept']}",
        S["college_name"]
    )

    hdr_tbl = Table([[left_logo, center_para]], colWidths=[28*mm, usable - 28*mm])
    hdr_tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (-1, -1),  "CENTER"),
        ("BOX",           (0, 0), (-1, -1), 0.8, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 3 * mm))

    # Banner
    banner_text = (
        f"Semester {meta['semester']} Result  |  Session: {meta['session']}  |  "
        f"Mode: {meta['mode']}  |  Regulation: {meta['regulation']}"
    )
    banner = Table([[Paragraph(banner_text, S["college_sub"])]], colWidths=[usable])
    banner.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(banner)
    story.append(Spacer(1, 4 * mm))

    # Student info
    info_data = [
        [
            Paragraph("Register No.", S["label"]),
            Paragraph(student["reg_no"] or "—", S["value"]),
            Paragraph("GPA", S["label"]),
            Paragraph(student.get("gpa", "—") or "—", S["value"]),
        ],
        [
            Paragraph("Student Name", S["label"]),
            Paragraph(student["name"] or "—", S["value"]),
            Paragraph("Branch", S["label"]),
            Paragraph(meta.get("branch", "—"), S["value"]),
        ],
    ]
    cw = [32*mm, 70*mm, 22*mm, usable - 124*mm]
    info_tbl = Table(info_data, colWidths=cw)
    info_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.6, colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 4 * mm))

    # Marks table
    story.append(Paragraph("MARKS STATEMENT", S["section_title"]))

    cw2 = [10*mm, 26*mm, usable - 10*mm - 26*mm - 20*mm - 26*mm, 20*mm, 26*mm]
    marks_data = [[
        Paragraph("S.No",        S["th"]),
        Paragraph("Course Code", S["th"]),
        Paragraph("Course Name", S["th"]),
        Paragraph("Grade",       S["th"]),
        Paragraph("Result",      S["th"]),
    ]]

    for i, subj in enumerate(student["subjects"], start=1):
        is_fail   = subj["result"] == "Reappear"
        res_style = ParagraphStyle(
            f"res_{i}",
            fontName  = "Helvetica-Bold" if is_fail else "Helvetica",
            fontSize  = 8,
            textColor = colors.black,
            alignment = TA_CENTER,
        )
        marks_data.append([
            Paragraph(str(i),                 S["td_center"]),
            Paragraph(subj.get("code", ""),   S["td_center"]),
            Paragraph(subj.get("name", ""),   S["td"]),
            Paragraph(subj.get("grade", ""),  S["td_center"]),
            Paragraph(subj.get("result", ""), res_style),
        ])

    marks_tbl = Table(marks_data, colWidths=cw2, repeatRows=1)
    marks_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.6, colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(marks_tbl)
    story.append(Spacer(1, 10 * mm))

    # Signatures
    sig_data = [
        [Paragraph("___________________", S["sign_label"])] * 3,
        [
            Paragraph("Class Advisor",     S["sign_label"]),
            Paragraph("HOD",               S["sign_label"]),
            Paragraph("Student Signature", S["sign_label"]),
        ],
    ]
    sig_tbl = Table(sig_data, colWidths=[usable / 3] * 3)
    sig_tbl.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_tbl)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "This is a computer-generated mark slip. "
        "For discrepancies, contact the Examination Cell.",
        S["footer"]
    ))

    doc.build(story)


# ── Combine Slips ─────────────────────────────────────────────────────────────
def combine_slips(slip_paths, out_path):
    writer = PdfWriter()
    for path in slip_paths:
        try:
            reader = PdfReader(path)
            if reader.pages:
                writer.add_page(reader.pages[0])
        except Exception as e:
            print(f"  Warning: could not add {path}: {e}")
    with open(out_path, "wb") as f:
        writer.write(f)


def combine_slips_simple(slip_paths, out_path):
    """Alias for combine_slips for compatibility with app.py."""
    return combine_slips(slip_paths, out_path)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate student mark slips")
    parser.add_argument("--input",  default="marks.pdf", help="Input PDF path")
    parser.add_argument("--outdir", default="slips",     help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"[1/4] Reading: {args.input}")
    students, meta = extract_students(args.input)
    print(f"      Campus   : {meta['campus']}")
    print(f"      Session  : {meta['session']}")
    print(f"      Students : {len(students)}")

    if not students:
        print("\n[!] No student data found. Check the PDF format.")
        return

    print("\n[3/4] Generating slips...")
    slip_paths = []
    for i, student in enumerate(students, 1):
        safe = re.sub(r"[^\w]", "_", student["reg_no"] or f"student_{i}")
        out  = os.path.join(args.outdir, f"{safe}.pdf")
        build_slip(student, meta, out)
        slip_paths.append(out)
        print(f"      [{i:02d}/{len(students)}] {student['name']:<30} -> {student['reg_no']}")

    print("\n[4/4] Combining into one PDF...")
    combined = os.path.join(args.outdir, "ALL_SLIPS_PRINT.pdf")
    combine_slips(slip_paths, combined)
    print(f"      -> {combined}")
    print("\nDone!")


if __name__ == "__main__":
    main()
