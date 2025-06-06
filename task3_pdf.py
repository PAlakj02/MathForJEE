from fpdf import FPDF
import os
import pandas as pd

# Configurable base path (replace with your own directory)
BASE_PATH = "PATH_TO_YOUR_DATA_DIRECTORY"  # e.g., "/home/user/mathango_data" or "C:\\Users\\user\\Documents\\mathango_data"
OUTPUT_DIR = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def add_table(pdf, df, title, col_widths):
    """Helper function to add a table to the PDF."""
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_fill_color(200, 220, 255)  # Light blue background
    pdf.cell(0, 10, title, border=1, ln=True, fill=True)
    pdf.set_font("Helvetica", size=10)
    for col in df.columns:
        pdf.cell(col_widths[df.columns.get_loc(col)], 8, col, border=1)
    pdf.ln()
    for _, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_widths[df.columns.get_loc(col)], 8, str(row[col]), border=1)
        pdf.ln()
    pdf.ln(5)

def text_to_pdf(student_id):
    try:
        # Load input files
        txt_path = os.path.join(OUTPUT_DIR, f"feedback_{student_id}.txt")
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        subject_df = pd.read_csv(os.path.join(OUTPUT_DIR, f"subject_{student_id}.csv"))
        weak_df = pd.read_csv(os.path.join(OUTPUT_DIR, f"weak_{student_id}.csv"))
        chart_path = os.path.join(OUTPUT_DIR, f"chart_{student_id}.png")

        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()

        # Set metadata
        pdf.set_title(f"Student {student_id} Performance Report")
        pdf.set_author("MathonGo AI System")

        # Set margins
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=15)

        # Add logo
        logo_width = 30
        logo_path = os.path.join(BASE_PATH, "mathongo_logo.jpeg")
        try:
            pdf.image(logo_path, x=pdf.w - logo_width - 15, y=10, w=logo_width)
        except:
            pdf.set_font("Helvetica", 'I', 10)
            pdf.cell(0, 10, "MathonGo Logo Placeholder", ln=True, align="R")
        pdf.ln(25)

        # Add heading
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, f"Performance Report - Student {student_id}", ln=True, align="C")
        pdf.ln(10)

        # Add subject-wise table
        col_widths_subject = [40, 30, 30, 30, 30, 40]  # Adjust based on columns
        add_table(pdf, subject_df, "Subject-Wise Performance", col_widths_subject)

        # Add weak chapters table
        col_widths_weak = [50, 30, 30, 30, 30, 40]  # Adjust for weak_df columns
        add_table(pdf, weak_df, "Chapter-Wise Performance (Weak Areas)", col_widths_weak)

        # Add time vs. accuracy chart
        try:
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Time vs. Accuracy by Subject", ln=True)
            pdf.image(chart_path, x=15, y=pdf.get_y() + 5, w=100)
            pdf.ln(110)
        except:
            pdf.set_font("Helvetica", 'I', 10)
            pdf.cell(0, 10, "Chart not available", ln=True)

        # Process text, skipping unwanted line
        lines = text.split('\n')
        if lines and lines[0].strip() == "Here is the student performance feedback:":
            lines = lines[1:]  # Skip the first line

        pdf.set_font("Helvetica", size=11)
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(6)
                continue

            if line.startswith('**') and line.endswith('**'):
                pdf.set_font("Helvetica", 'B', 13)
                pdf.cell(0, 8, line.strip('**'), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=11)
                pdf.ln(3)
            elif line.startswith('* '):
                pdf.cell(10)
                pdf.multi_cell(0, 6, line[2:].strip())
                pdf.ln(1)
            elif line[:2].isdigit() and line[2] in '. )':
                pdf.cell(10)
                pdf.multi_cell(0, 6, line)
                pdf.ln(1)
            else:
                pdf.multi_cell(0, 6, line)
                pdf.ln(3)

        # Add footer
        pdf.set_font("Helvetica", size=8)
        pdf.set_y(-15)
        pdf.cell(0, 10, f"Page {pdf.page_no()} - MathonGo IIT JEE Prep", align="C")

        # Save PDF
        pdf_path = os.path.join(OUTPUT_DIR, f"feedback_{student_id}.pdf")
        pdf.output(pdf_path)
        print(f"✅ Enhanced PDF generated for student {student_id}")

        return pdf_path

    except Exception as e:
        print(f"Failed for student {student_id}: {str(e)}")
        return None
