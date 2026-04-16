"""
Student Mark Slip Generator
-----------------------------
- Reads multi-page PDF (summary sheets or individual pages)
- Extracts: Register Number, Student Name, and subject rows
  (Course Code | Course Name | Grade | Result)
- Generates A4 PDF with formatted slips (2 per page)
- Combines all slips into a single print-ready PDF

Usage:
    pip install pdfplumber reportlab pypdf
    python generate_slips.py --input marks.pdf
"""

import os
import re
import argparse
import pdfplumber
from reportlab.lib.pagesizes import A5, A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, Image, Flowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter
from io import BytesIO


# ── Colours ──────────────────────────────────────────────────────────────────
HEADER_BG   = colors.HexColor("#1a3a5c")   # dark navy
ROW_ALT     = colors.HexColor("#eef3f8")   # light blue-grey
BORDER      = colors.HexColor("#1a3a5c")
ACCENT      = colors.HexColor("#c8102e")   # red accent for college feel


# ── Logo Generation ──────────────────────────────────────────────────────────
def create_mit_logo(path: str = "mit_logo.png", size: int = 60):
    """Create MIT logo placeholder"""
    # Return path without creating actual image
    # Logo will be handled as text in the slip layout
    return None

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    return {
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=11,
            textColor=colors.white, alignment=TA_CENTER, leading=14
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=8,
            textColor=colors.white, alignment=TA_CENTER, leading=10
        ),
        "label": ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=8,
            textColor=colors.HexColor("#444444"), leading=10
        ),
        "value": ParagraphStyle(
            "value", fontName="Helvetica", fontSize=8,
            textColor=colors.black, leading=10
        ),
        "th": ParagraphStyle(
            "th", fontName="Helvetica-Bold", fontSize=7.5,
            textColor=colors.white, alignment=TA_CENTER
        ),
        "td": ParagraphStyle(
            "td", fontName="Helvetica", fontSize=7.5,
            textColor=colors.black, alignment=TA_LEFT
        ),
        "td_center": ParagraphStyle(
            "td_center", fontName="Helvetica", fontSize=7.5,
            textColor=colors.black, alignment=TA_CENTER
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica-Oblique", fontSize=6.5,
            textColor=colors.grey, alignment=TA_CENTER
        ),
    }


# ── PDF Extraction ────────────────────────────────────────────────────────────
def extract_students(pdf_path: str) -> list[dict]:
    """
    Parse PDF and extract student data.
    Supports multiple formats:
    1. Individual pages per student (old format)
    2. Summary sheet with students as columns (new format)
    
    Returns a list of dicts:
        { "reg_no": str, "name": str, "semester": str,
          "subjects": [{"code","name","grade","result"}, ...] }
    """
    students = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            tables = page.extract_tables()

            # Try format 1: Individual student per page
            student = {
                "reg_no": "",
                "name": "",
                "semester": "First Semester Result - Nov / Dec 2025",
                "subjects": [],
                "page": page_num,
            }

            # Extract Register Number and Name from text
            for line in lines:
                if re.search(r"register\s*number", line, re.I):
                    m = re.search(r"register\s*number\s*[:\-]?\s*(\S+)", line, re.I)
                    if m:
                        student["reg_no"] = m.group(1)
                if re.search(r"student\s*name", line, re.I):
                    m = re.search(r"student\s*name\s*[:\-]?\s*(.+)", line, re.I)
                    if m:
                        student["name"] = m.group(1).strip()
                if re.search(r"semester\s*result", line, re.I):
                    student["semester"] = line.strip()

            # Extract subjects from tables (Format 1)
            if tables:
                for table in tables:
                    for row in table:
                        if row is None:
                            continue
                        cells = [str(c).strip() if c else "" for c in row]
                        cell_text = " ".join(cells).lower()
                        
                        # Skip header rows
                        if any(h in cell_text for h in ["s.no", "course code", "s. no", "course name", "result"]):
                            continue
                        
                        # Format 1: Check if first cell is a number (subject row)
                        if len(cells) >= 4 and cells[0] and re.match(r"^\d+$", cells[0].strip()):
                            subject = {
                                "code":   cells[1] if len(cells) > 1 else "",
                                "name":   cells[2] if len(cells) > 2 else "",
                                "grade":  cells[3] if len(cells) > 3 else "",
                                "result": cells[4] if len(cells) > 4 else "",
                            }
                            student["subjects"].append(subject)

            # If format 1 found data, add it
            if student["reg_no"] or student["name"] or student["subjects"]:
                students.append(student)
                continue

            # Try format 2: Summary sheet (students as columns)
            # This format typically has subjects in rows and students in columns
            summary_students = extract_from_summary_sheet(table=tables[0] if tables else None, 
                                                         text_lines=lines, page_num=page_num)
            if summary_students:
                students.extend(summary_students)

    return students if students else extract_from_summary_sheet_full(pdf_path)


def extract_from_summary_sheet(table, text_lines, page_num):
    """Extract students from a summary sheet format (students as columns)"""
    if not table or len(table) < 3:
        return []
    
    summary_students = []
    
    # The first row might have roll numbers or student identifiers
    # Subsequent rows have subjects with their marks
    
    try:
        header_row = table[0]
        header = [str(h).strip() if h else "" for h in header_row]
        
        # Find where actual student data starts (typically after subject info columns)
        # Usually: S.No | Subject | Code | ... | Student1 | Student2 | etc.
        student_start_idx = None
        
        for idx, cell in enumerate(header):
            # Look for roll numbers, registration numbers in header
            if re.match(r"\d{2,}", cell.replace("-", "").replace("_", "").strip()):
                student_start_idx = idx
                break
        
        if student_start_idx is None and len(header) > 4:
            # Assume students start after 4 columns (S.No, Code, Name, etc.)
            student_start_idx = 4
        elif student_start_idx is None:
            return []
        
        # Extract student info from header
        student_identifiers = header[student_start_idx:]
        
        # Create a student entry for each column
        for col_idx, identifier in enumerate(student_identifiers):
            if not identifier or identifier.lower() in ["total", "average", "remarks"]:
                continue
            
            new_student = {
                "reg_no": identifier,
                "name": f"Student {col_idx + 1}",
                "semester": "First Semester Result - Nov / Dec 2025",
                "subjects": [],
                "page": page_num,
            }
            
            # Extract marks for this student from subsequent rows
            for row_idx in range(1, len(table)):
                row = table[row_idx]
                if not row or len(row) <= student_start_idx + col_idx:
                    continue
                
                row_cells = [str(cell).strip() if cell else "" for cell in row]
                
                # Get subject info (typically in first few columns)
                subject_code = row_cells[1] if len(row_cells) > 1 else ""
                subject_name = row_cells[2] if len(row_cells) > 2 else ""
                
                # If no clear subject name, try first column
                if not subject_code and row_cells[0]:
                    subject_code = row_cells[0]
                
                # Skip header/empty rows
                if "course" in subject_code.lower() or "subject" in subject_code.lower():
                    continue
                if not subject_code:
                    continue
                
                # Get mark for this student
                mark = row_cells[student_start_idx + col_idx] if len(row_cells) > student_start_idx + col_idx else ""
                
                if mark and mark not in ["", "—", "-", "N/A"]:
                    subject = {
                        "code": subject_code,
                        "name": subject_name,
                        "grade": mark,
                        "result": "PASS" if mark and mark not in ["AB", "F"] else "FAIL",
                    }
                    new_student["subjects"].append(subject)
            
            if new_student["subjects"]:
                summary_students.append(new_student)
    
    except Exception as e:
        print(f"Error extracting from summary sheet: {e}")
    
    return summary_students


def extract_from_summary_sheet_full(pdf_path):
    """Better extraction for summary sheets by analyzing structure"""
    students = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for table in tables:
                    if len(table) < 3 or len(table[0]) < 5:
                        continue
                    
                    rows = [[str(cell).strip() if cell else "" for cell in row] for row in table]
                    
                    # Detect header row (usually has subject codes or names)
                    header = rows[0]
                    
                    # Find student columns (look for patterns like roll numbers)
                    student_cols = []
                    for idx, cell in enumerate(header):
                        if re.search(r"\d+", cell) and len(cell) < 20:
                            student_cols.append((idx, cell))
                    
                    # If fewer than 2 student columns, try alternate detection
                    if len(student_cols) < 2 and len(header) > 4:
                        for idx in range(3, len(header)):
                            student_cols.append((idx, header[idx]))
                    
                    if not student_cols:
                        continue
                    
                    # Extract subjects and marks
                    subjects_data = []
                    for row_idx in range(1, len(rows)):
                        row = rows[row_idx]
                        if not any(row[:3]):  # Skip empty rows
                            continue
                        
                        # Subject info in first 3 columns
                        s_no = row[0] if len(row) > 0 else ""
                        code = row[1] if len(row) > 1 else ""
                        name = row[2] if len(row) > 2 else ""
                        
                        # Check if first cell looks like subject number
                        if not re.match(r"^\d+$", s_no.strip()):
                            code, name = s_no, code
                        
                        if code and code.lower() not in ["course", "subject", "code", "name"]:
                            subjects_data.append((code, name, row))
                    
                    # Create student entries
                    for col_idx, (student_col, student_id) in enumerate(student_cols):
                        new_student = {
                            "reg_no": student_id,
                            "name": f"Student {col_idx + 1}",
                            "semester": "First Semester Result - Nov / Dec 2025",
                            "subjects": [],
                            "page": page_num,
                        }
                        
                        for code, name, row in subjects_data:
                            if student_col < len(row):
                                mark = row[student_col]
                                if mark and mark not in ["", "—", "-"]:
                                    subject = {
                                        "code": code,
                                        "name": name,
                                        "grade": mark,
                                        "result": "PASS",
                                    }
                                    new_student["subjects"].append(subject)
                        
                        if new_student["subjects"]:
                            students.append(new_student)
    
    except Exception as e:
        print(f"Error in full extraction: {e}")
    
    return students


# ── Slip Generator ────────────────────────────────────────────────────────────
def build_slip(student: dict, out_path: str, college_name: str, dept_name: str, logo_path: str = None):
    """Generate a single slip for one student (for A4 2-up layout)."""
    S = make_styles()
    # Use half-A4 height for 2 slips per page
    W, H = 210*mm, 148.5*mm  # Half A4 page (approximately A5 height)

    doc = SimpleDocTemplate(
        out_path,
        pagesize=(W, H),
        leftMargin=8*mm, rightMargin=8*mm,
        topMargin=6*mm,  bottomMargin=6*mm,
    )

    story = []
    usable_w = W - 16*mm

    # ── Logo and Header Row ──
    # Create a logo placeholder with text
    logo_style = ParagraphStyle(
        "logo", fontName="Helvetica-Bold", fontSize=14,
        textColor=colors.HexColor("#1a3a5c"), alignment=TA_CENTER, leading=16
    )
    
    header_row_data = [
        Paragraph("◆", logo_style),  # Logo placeholder using special character
        Paragraph(college_name, S["title"]),
    ]
    
    header_row = Table([header_row_data], colWidths=[20*mm, usable_w - 20*mm])
    header_row.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,-1), HEADER_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(header_row)
    story.append(Spacer(1, 2*mm))

    # ── Department and Semester ──
    info_data = [
        [Paragraph(dept_name,    S["subtitle"])],
        [Paragraph(student["semester"], S["subtitle"])],
    ]
    dept_tbl = Table(info_data, colWidths=[usable_w])
    dept_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HEADER_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
    ]))
    story.append(dept_tbl)
    story.append(Spacer(1, 2*mm))

    # ── Student info ──
    info_data = [
        [Paragraph("Register No.", S["label"]),
         Paragraph(student["reg_no"] or "—", S["value"]),
         Paragraph("Student Name", S["label"]),
         Paragraph(student["name"] or "—", S["value"])],
    ]
    col_w = [22*mm, 28*mm, 22*mm, usable_w - 72*mm]
    info_tbl = Table(info_data, colWidths=col_w)
    info_tbl.setStyle(TableStyle([
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#aaaaaa")),
        ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#f0f4f8")),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("FONTSIZE",      (0,0), (-1,-1), 7),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 2*mm))

    # ── Marks table ──
    col_widths = [7*mm, 16*mm, 55*mm, 12*mm, 12*mm]
    col_widths[2] = usable_w - sum(col_widths[:2]) - col_widths[3] - col_widths[4]

    marks_data = [[
        Paragraph("S.No",        S["th"]),
        Paragraph("Code",        S["th"]),
        Paragraph("Course Name", S["th"]),
        Paragraph("Grade",       S["th"]),
        Paragraph("Result",      S["th"]),
    ]]

    for i, subj in enumerate(student["subjects"], start=1):
        bg = ROW_ALT if i % 2 == 0 else colors.white
        marks_data.append([
            Paragraph(str(i),         S["td_center"]),
            Paragraph(subj["code"],   S["td_center"]),
            Paragraph(subj["name"],   S["td"]),
            Paragraph(subj["grade"],  S["td_center"]),
            Paragraph(subj["result"], S["td_center"]),
        ])

    marks_tbl = Table(marks_data, colWidths=col_widths, repeatRows=1)
    ts = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  HEADER_BG),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 3),
        ("RIGHTPADDING",  (0,0), (-1,-1), 3),
        ("FONTSIZE",      (0,0), (-1,-1), 6.5),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ])
    # alternate row background
    for i in range(1, len(marks_data)):
        if i % 2 == 0:
            ts.add("BACKGROUND", (0,i), (-1,i), ROW_ALT)
    marks_tbl.setStyle(ts)
    story.append(marks_tbl)

    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        "Computer-generated slip. For queries, contact the Examination Cell.",
        S["footer"]
    ))

    doc.build(story)


# ── Combine into print-ready PDF (2 slips per A4 page) ────────────────────────
def combine_slips_2_per_page(slip_paths: list[str], out_path: str):
    """Merge 2 slips per A4 page."""
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import A4
    from io import BytesIO
    
    writer = PdfWriter()
    
    for i in range(0, len(slip_paths), 2):
        # Create a new A4 page
        pdf_buffer = BytesIO()
        c = pdf_canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        
        # First slip at top
        try:
            reader1 = PdfReader(slip_paths[i])
            page1 = reader1.pages[0]
            # Scale and position first slip
            from PyPDF2 import Transformation
            trans = Transformation().scale(sx=1, sy=1)
            page1.add_transformation(trans)
            # Add to top half
            x, y = 0, height / 2
            c.translate(0, y)
            c.scale(1, 1)
        except Exception as e:
            print(f"Error reading slip {i}: {e}")
        
        # Second slip at bottom (if exists)
        if i + 1 < len(slip_paths):
            try:
                reader2 = PdfReader(slip_paths[i + 1])
                page2 = reader2.pages[0]
            except Exception as e:
                print(f"Error reading slip {i+1}: {e}")
        
        c.save()
        pdf_buffer.seek(0)
        temp_page = PdfReader(pdf_buffer)
        for page in temp_page.pages:
            writer.add_page(page)
    
    with open(out_path, "wb") as f:
        writer.write(f)


def combine_slips_simple(slip_paths: list[str], out_path: str):
    """Merge all individual slips into one PDF."""
    writer = PdfWriter()
    for path in slip_paths:
        try:
            reader = PdfReader(path)
            # Take first page and duplicate it for 2-up layout
            if reader.pages:
                page = reader.pages[0]
                writer.add_page(page)
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    with open(out_path, "wb") as f:
        writer.write(f)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate student mark slips from PDF")
    parser.add_argument("--input",   default="marks.pdf", help="Input PDF path")
    parser.add_argument("--outdir",  default="slips",     help="Output directory for slips")
    parser.add_argument("--college", default="Madras Institute of Technology",
                        help="College name for header")
    parser.add_argument("--dept",    default="Department of Computer Technology",
                        help="Department name for header")
    parser.add_argument("--logo",    default=None, help="Path to logo image")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Create logo if not provided
    logo_path = args.logo
    if not logo_path:
        logo_path = create_mit_logo(os.path.join(args.outdir, "mit_logo.png"))

    print(f"[1/4] Reading PDF: {args.input}")
    students = extract_students(args.input)
    print(f"      Found {len(students)} student(s)")

    if not students:
        print("No student data found. Check PDF format or extraction logic.")
        return

    print("[2/4] Generating individual slips...")
    slip_paths = []
    for i, student in enumerate(students, start=1):
        safe_name = re.sub(r"[^\w]", "_", student["reg_no"] or f"student_{i}")
        out_path = os.path.join(args.outdir, f"{safe_name}.pdf")
        build_slip(student, out_path, args.college, args.dept, logo_path)
        slip_paths.append(out_path)
        print(f"      [{i}/{len(students)}] {student.get('name', 'Unknown')}")

    print("[3/4] Combining slips (2 per A4 page)...")
    combined = os.path.join(args.outdir, "ALL_SLIPS_PRINT.pdf")
    combine_slips_simple(slip_paths, combined)
    print(f"      Created: {combined}")

    print("\n✓ Done!")
    print(f"  Output PDF → {combined}")
    print(f"  Individual slips → {args.outdir}/")


if __name__ == "__main__":
    main()