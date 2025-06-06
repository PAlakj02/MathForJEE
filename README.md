**AI-Powered Student Performance Feedback System for MathonGo**
Overview
  This project generates personalized performance feedback reports for  students based on test data in JSON format. Built for MathonGo, a competitive exam  preparation platform, it processes student performance metrics, generates detailed feedback using the Groq API, and creates professional PDF reports with tables and charts. The system emphasizes comprehensive feedback on all weak topics, crucial for exam preparation.
Tech Stack

Python 3.8+: Core language for data processing, API integration, and PDF generation.
Pandas: For parsing JSON and CSV files.
Groq API (llama3-70b-8192): For generating human-like, encouraging feedback.
FPDF: For creating PDF reports with tables, charts, and styled content.
Matplotlib & Seaborn: For generating time vs. accuracy scatter plots.
Glob: For automating file discovery.
OS: For managing file paths with configurable directories.

Features

Data Processing: Parses JSON files (sample_submission_analysis_*.json) and generates overall_*.json, subject_*.csv, weak_*.csv, and chart_*.png.

Feedback Generation:
Motivational introduction with strongest subject and overall accuracy.
Detailed breakdown of subjects and all weak chapters.
Time management insights and actionable recommendations.
Saves feedback as feedback_*.txt.


PDF Reports:
Professional layout with title, MathonGo logo, and footer.
Tables for subject-wise and chapter-wise performance.
Embedded time vs. accuracy charts.
Formatted feedback text.
Saves as feedback_*.pdf.


Automation: Processes all JSON files in data/ using glob.
Error Handling: Validates inputs and handles missing files or API errors.

Project Structure
mathango-feedback-system/
├── task1_processing.py # Data processing and chart generation
├── task2_aiprompting.py    # Feedback generation with Groq API
├── task3_pdf.py         # PDF report generation
├── mathango(1).ipynb  # Colab notebook with full workflow
├── README.md               # Project documentation
├── requirements.txt         # Dependencies
├── .gitignore              # Excludes output files
├── data/
│   ├── sample_submission_analysis_1.json
│   ├── sample_submission_analysis_2.json
│   ├── sample_submission_analysis_3.json
├── output/                 # Empty (in .gitignore)
└── mathongo_logo.jpeg      # Logo for PDFs

Setup Instructions

Prerequisites:

Install Python 3.8+.
Install dependencies:pip install -r requirements.txt


Obtain a Groq API key from x.ai/api.


Configure Paths:

Open main.py, task1_processing.py, task2_aiprompting.py, and task3_pdf.py.
Replace BASE_PATH = "PATH_TO_YOUR_DATA_DIRECTORY" with your directory path, e.g., /home/user/mathango_data/ or C:\Users\user\Documents\mathango_data\.
Ensure data/ contains input JSON files and mathongo_logo.jpeg is in the project root.


Environment Configuration:

Set the Groq API key:export GROQ_API_KEY=your_key


For Windows:set GROQ_API_KEY=your_key


Running the Script:

Execute:python main.py


Outputs (overall_*.json, subject_*.csv, weak_*.csv, chart_*.png, feedback_*.txt, feedback_*.pdf) are saved in output/.



Implementation Details
Task 1: Data Processing

Parses JSON files to extract overall, subject-wise, and chapter-wise metrics.
Generates time vs. accuracy scatter plots.
Saves outputs as JSON, CSV, and PNG files.

Task 2: Feedback Generation

Builds a prompt with personalized introduction, performance breakdown, time insights, and recommendations.
Uses Groq API (llama3-70b-8192, temperature=0.7, max_tokens=800).
Saves feedback as text files.

Task 3: PDF Generation

Creates PDFs with:
Title, logo, and footer.
Tables for subject-wise and chapter-wise data.
Embedded time vs. accuracy charts.
Formatted feedback text, skipping unwanted lines.


Uses FPDF for styling (blue headers, consistent fonts).


Troubleshooting

Ensure GROQ_API_KEY is set.
Verify input JSON files in data/ match the expected format.
Check output/ for generated files.
For path issues, update BASE_PATH in all .py files.

Contact
  For issues, refer to x.ai/api for API-related queries.
