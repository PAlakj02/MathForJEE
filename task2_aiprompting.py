import pandas as pd
import json
import os
from groq import Groq
import time

# Configurable base path (replace with your own directory)
BASE_PATH = "PATH_TO_YOUR_DATA_DIRECTORY"  # e.g., "/home/user/mathango_data" or "C:\\Users\\user\\Documents\\mathango_data"
DATA_DIR = os.path.join(BASE_PATH, "data")
OUTPUT_DIR = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_prompt(overall, subject_df, weak_df):
    # Find top subject programmatically
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

def generate_feedback(student_id):
    try:
        # Load data
        with open(os.path.join(OUTPUT_DIR, f"overall_{student_id}.json")) as f:
            overall = json.load(f)
        subject_df = pd.read_csv(os.path.join(OUTPUT_DIR, f"subject_{student_id}.csv"))
        weak_df = pd.read_csv(os.path.join(OUTPUT_DIR, f"weak_{student_id}.csv"))

        # Generate prompt
        prompt = build_prompt(overall, subject_df, weak_df)
        print(f"\nPrompt for Student {student_id} ready - length: {len(prompt)} chars")

        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        if not client.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Generate feedback
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

        # Save feedback
        feedback_path = os.path.join(OUTPUT_DIR, f"feedback_{student_id}.txt")
        with open(feedback_path, "w", encoding="utf-8") as f:
            f.write(feedback)
        print(f"✅ Student {student_id} feedback generated")

        return feedback

    except Exception as e:
        print(f"Student {student_id} failed: {str(e)}")
        return None
