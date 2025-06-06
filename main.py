import glob
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from groq import Groq
from fpdf import FPDF
import time

# Configurable base path (replace with your own directory)
BASE_PATH = "PATH_TO_YOUR_DATA_DIRECTORY"  # e.g., "/home/user/mathango_data" or "C:\\Users\\user\\Documents\\mathango_data"
DATA_DIR = os.path.join(BASE_PATH, "data")
OUTPUT_DIR = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Task 1: Data Processing Functions
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)[0]  # Each file has a single JSON object inside a list

def extract_overall_metrics(data):
    return {
        "Total Time (min)": round(data["totalTimeTaken"] / 60, 2),
        "Total Score": data["totalMarkScored"],
        "Total Questions Attempted": data["totalAttempted"],
        "Total Correct": data["totalCorrect"],
        "Accuracy (%)": round(data["accuracy"], 2)
    }

def extract_subject_metrics(data):
    subject_map = {
        "607018ee404ae53194e73d92": "Physics",
        "607018ee404ae53194e73d90": "Chemistry",
        "607018ee404ae53194e73d91": "Maths"
    }
    rows = []
    for sub in data.get("subjects", []):
        rows.append({
            "Subject": subject_map.get(sub["subjectId"]["$oid"], "Unknown"),
            "Marks Scored": sub.get("totalMarkScored", 0),
            "Attempted": sub.get("totalAttempted", 0),
            "Correct": sub.get("totalCorrect", 0),
            "Accuracy (%)": round(sub.get("accuracy", 0), 2),
            "Time Taken (min)": round(sub.get("totalTimeTaken", 0) / 60, 2)
        })
    return pd.DataFrame(rows)

def extract_chapter_stats(data):
    section_data = []
    for section in data.get("sections", []):
        for q in section.get("questions", []):
            qid = q.get("questionId", {})
            chapters = [c["title"] for c in qid.get("chapters", [])]
            topics = [t["title"] for t in qid.get("topics", [])]
            concepts = [c["title"] for c in qid.get("concepts", [])]
            level = qid.get("level", "unknown")
            correct = any(opt.get("isCorrect", False) for opt in q.get("markedOptions", []))
            section_data.append({
                "Chapter": chapters[0] if chapters else "Unknown",
                "Topic": topics[0] if topics else "Unknown",
                "Concept": concepts[0] if concepts else "Unknown",
                "Difficulty": level,
                "Correct": correct,
                "Time Taken (sec)": q.get("timeTaken", 0),
                "Status": q.get("status", "unknown")
            })
    return pd.DataFrame(section_data)

def identify_weak_chapters(df_chap):
    df = df_chap.copy()
    df_grouped = df.groupby("Chapter").agg({
        "Correct": ["sum", "count"],
        "Time Taken (sec)": "sum"
    }).reset_index()
    df_grouped.columns = ["Chapter", "Correct", "Total", "Total Time (sec)"]
    df_grouped["Accuracy (%)"] = round(df_grouped["Correct"] / df_grouped["Total"] * 100, 2)
    df_grouped["Avg Time per Question (s)"] = round(df_grouped["Total Time (sec)"] / df_grouped["Total"], 2)
    return df_grouped.sort_values("Accuracy (%)")

def plot_time_vs_accuracy(df_subject, student_id):
    try:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_subject, x="Time Taken (min)", y="Accuracy (%)", hue="Subject", s=100)
        plt.title(f"Time vs Accuracy for Student {student_id}")
        plt.grid(True)
        chart_path = os.path.join(OUTPUT_DIR, f"chart_{student_id}.png")
        plt.savefig(chart_path)
        plt.close()
        print(f"Saved chart to {chart_path}")
        return chart_path
    except Exception as e:
        print(f"Error generating chart for student {student_id}: {e}")
        return None

def analyze_single_student(file_path):
    student_id = os.path.basename(file_path).split('_')[-1].split('.')[0]
    print(f"📂 Analyzing File: {os.path.basename(file_path)}")
    try:
        data = load_json(file_path)
        overall = extract_overall_metrics(data)
        df_subject = extract_subject_metrics(data)
        df_chapters = extract_chapter_stats(data)
        df_weak = identify_weak_chapters(df_chapters)

        # Save outputs
        overall_path = os.path.join(OUTPUT_DIR, f"overall_{student_id}.json")
        with open(overall_path, 'w') as f:
            json.dump(overall, f)
        print(f"Saved overall metrics to {overall_path}")

        subject_path = os.path.join(OUTPUT_DIR, f"subject_{student_id}.csv")
        df_subject.to_csv(subject_path, index=False)
        print(f"Saved subject-wise performance to {subject_path}")

        chapter_path = os.path.join(OUTPUT_DIR, f"chapter_{student_id}.csv")
        df_chapters.to_csv(chapter_path, index=False)
        print(f"Saved chapter-wise performance to {chapter_path}")

        weak_path = os.path.join(OUTPUT_DIR, f"weak_{student_id}.csv")
        df_weak.to_csv(weak_path, index=False)
        print(f"Saved weak chapters to {weak_path}")

        chart_path = plot_time_vs_accuracy(df_subject, student_id)

        return {
            "overall": overall,
            "subject_df": df_subject,
            "chapter_df": df_chapters,
            "weak_df": df_weak,
            "chart_path": chart_path
        }
    except Exception as e:
        print(f"Error in data processing for student {student_id}: {e}")
        return {}

# Task 2: Feedback Generation Functions
def build_prompt(overall, subject_df, weak_df):
    top_subject = subject_df.loc[subject_df['Accuracy (%)'].idxmax()]
    return f"""**Generate student performance feedback with:**

1. **Personalized Introduction**
- Start with: "Great work on your recent test!"
- Highlight: "Your strongest subject was {top_subject['Subject']} with {top_subject['Accuracy (%)']}% accuracy"
- Mention: "Overall accuracy: {overall['Accuracy (%)']}% ({overall['Total Correct']}/{overall['Total Questions Attempted']} correct)"

2. **Performance Breakdown**
**Subjects:**
{subject_df.to_markdown()}

**Weakest Chapters:**
{weak_df[['Chapter', 'Accuracy (%)']].to_markdown()}

3. **Time Management Insights**
- Average time per question: {overall['Total Time (min)']/overall['Total Questions Attempted']:.1f} mins
- Fastest chapter: {weak_df.loc[weak_df['Avg Time per Question (s)'].idxmin()]['Chapter']}
- Slowest chapter: {weak_df.loc[weak_df['Avg Time per Question (s)'].idxmax()]['Chapter']}

4. **Actionable Recommendations** (3 specific tips)
- Focus practice on: {weak_df.iloc[0]['Chapter']} (current accuracy: {weak_df.iloc[0]['Accuracy (%)']}%)
- Time management strategy for: {weak_df.loc[weak_df['Avg Time per Question (s)'].idxmax()]['Chapter']}
- Resource suggestion: Khan Academy {top_subject['Subject']} tutorials

**Tone:** Encouraging, specific, and growth-focused"""

def generate_feedback(student_id, overall, subject_df, weak_df):
    try:
        prompt = build_prompt(overall, subject_df, weak_df)
        print(f"Prompt for Student {student_id} ready - length: {len(prompt)} chars")

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        if not client.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert math tutor generating student feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        feedback = response.choices[0].message.content

        feedback_path = os.path.join(OUTPUT_DIR, f"feedback_{student_id}.txt")
        with open(feedback_path, "w", encoding="utf-8") as f:
            f.write(feedback)
        print(f"Saved feedback to {feedback_path}")

        return feedback
    except Exception as e:
        print(f"Error generating feedback for student {student_id}: {e}")
        return None

# Task 3: PDF Generation Functions
def add_table(pdf, df, title, col_widths):
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_fill_color(200, 220, 255)
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

def text_to_pdf(student_id, text, subject_df, weak_df, chart_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_title(f"Student {student_id} Performance Report")
        pdf.set_author("MathonGo AI System")
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=15)

        logo_width = 30
        logo_path = os.path.join(BASE_PATH, "mathongo_logo.jpeg")
        try:
            pdf.image(logo_path, x=pdf.w - logo_width - 15, y=10, w=logo_width)
        except:
            pdf.set_font("Helvetica", 'I', 10)
            pdf.cell(0, 10, "MathonGo Logo Placeholder", ln=True, align="R")
        pdf.ln(25)

        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, f"Performance Report - Student {student_id}", ln=True, align="C")
        pdf.ln(10)

        col_widths_subject = [40, 30, 30, 30, 30, 40]
        add_table(pdf, subject_df, "Subject-Wise Performance", col_widths_subject)

        col_widths_weak = [50, 30, 30, 30, 30, 40]
        add_table(pdf, weak_df, "Chapter-Wise Performance (Weak Areas)", col_widths_weak)

        try:
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Time vs. Accuracy by Subject", ln=True)
            pdf.image(chart_path, x=15, y=pdf.get_y() + 5, w=100)
            pdf.ln(110)
        except:
            pdf.set_font("Helvetica", 'I', 10)
            pdf.cell(0, 10, "Chart not available", ln=True)

        lines = text.split('\n')
        if lines and lines[0].strip() == "Here is the student performance feedback:":
            lines = lines[1:]

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

        pdf.set_font("Helvetica", size=8)
        pdf.set_y(-15)
        pdf.cell(0, 10, f"Page {pdf.page_no()} - MathonGo IIT JEE Prep", align="C")

        pdf_path = os.path.join(OUTPUT_DIR, f"feedback_{student_id}.pdf")
        pdf.output(pdf_path)
        print(f"Saved PDF to {pdf_path}")

        return pdf_path
    except Exception as e:
        print(f"Error generating PDF for student {student_id}: {e}")
        return None

# Main Pipeline
json_files = glob.glob(os.path.join(DATA_DIR, "sample_submission_analysis_*.json"))
for json_file in json_files:
    student_id = os.path.basename(json_file).split('_')[-1].split('.')[0]
    print(f"\nProcessing student {student_id}...")
    try:
        # Task 1: Data processing
        result = analyze_single_student(json_file)
        if not result.get("overall"):
            print(f"❌ Skipping student {student_id} due to data processing failure")
            continue
        print(f"✅ Task 1 completed for student {student_id}")

        # Task 2: Feedback generation
        feedback = generate_feedback(student_id, result["overall"], result["subject_df"], result["weak_df"])
        if not feedback:
            print(f"❌ Skipping student {student_id} due to feedback generation failure")
            continue
        print(f"✅ Task 2 completed for student {student_id}")
        time.sleep(5)  # Rate limit for Groq API

        # Task 3: PDF generation
        pdf_path = text_to_pdf(student_id, feedback, result["subject_df"], result["weak_df"], result["chart_path"])
        if pdf_path:
            print(f"✅ Task 3 completed for student {student_id}: PDF saved to {pdf_path}")
        else:
            print(f"❌ Skipping student {student_id} due to PDF generation failure")

    except Exception as e:
        print(f"❌ Failed for student {student_id}: {str(e)}")