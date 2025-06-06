import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configurable base path (replace with your own directory)
BASE_PATH = "PATH_TO_YOUR_DATA_DIRECTORY"  # e.g., "/home/user/mathango_data" or "C:\\Users\\user\\Documents\\mathango_data"
DATA_DIR = os.path.join(BASE_PATH, "data")
OUTPUT_DIR = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Utility: Load a JSON file from path
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)[0]  # Each file has a single JSON object inside a list

# Extract top-level performance
def extract_overall_metrics(data):
    return {
        "Total Time (min)": round(data["totalTimeTaken"] / 60, 2),
        "Total Score": data["totalMarkScored"],
        "Total Questions Attempted": data["totalAttempted"],
        "Total Correct": data["totalCorrect"],
        "Accuracy (%)": round(data["accuracy"], 2)
    }

# Extract subject-wise performance
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

# Extract chapter/topic/concept-level performance
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

# Identify weak chapters
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

# Plot and save Time vs Accuracy
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

# Analyze a single student and save outputs
def analyze_single_student(file_path):
    student_id = os.path.basename(file_path).split('_')[-1].split('.')[0]
    print(f"📂 Analyzing File: {os.path.basename(file_path)}\n")
    data = load_json(file_path)

    overall = extract_overall_metrics(data)
    df_subject = extract_subject_metrics(data)
    df_chapters = extract_chapter_stats(data)
    df_weak = identify_weak_chapters(df_chapters)

    # Save outputs
    try:
        # Save overall metrics
        overall_path = os.path.join(OUTPUT_DIR, f"overall_{student_id}.json")
        with open(overall_path, 'w') as f:
            json.dump(overall, f)
        print(f"Saved overall metrics to {overall_path}")

        # Save subject-wise performance
        subject_path = os.path.join(OUTPUT_DIR, f"subject_{student_id}.csv")
        df_subject.to_csv(subject_path, index=False)
        print(f"Saved subject-wise performance to {subject_path}")

        # Save chapter-wise performance
        chapter_path = os.path.join(OUTPUT_DIR, f"chapter_{student_id}.csv")
        df_chapters.to_csv(chapter_path, index=False)
        print(f"Saved chapter-wise performance to {chapter_path}")

        # Save weak chapters
        weak_path = os.path.join(OUTPUT_DIR, f"weak_{student_id}.csv")
        df_weak.to_csv(weak_path, index=False)
        print(f"Saved weak chapters to {weak_path}")

        # Generate and save
        chart_path = plot_time_vs_accuracy(df_subject, student_id)

    except Exception as e:
        print(f"Error saving files for student {student_id}: {e}")

    return {
        "overall": overall,
        "subjects_df": df_subject,
        "chapter_df": df_chapters,
        "weak_df": df_weak
    }
