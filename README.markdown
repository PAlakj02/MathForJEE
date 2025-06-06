# AI-Powered Student Performance Feedback System for MathonGo

**Overview**

This project generates personalized performance feedback reports for students preparing for competitive exams, such as IIT JEE, based on test data in JSON format. Developed for MathonGo, a leading exam preparation platform, it processes student performance metrics, generates detailed feedback using the Groq API, and creates professional PDF reports with tables and charts. The system emphasizes comprehensive feedback on all weak topics, crucial for exam preparation.

**Tech Stack**

- **Python 3.8+**: Core language for data processing, API integration, and PDF generation.
- **Pandas**: For parsing JSON and CSV files (`sample_submission_analysis_*.json`).
- **Groq API (llama3-70b-8192)**: For generating human-like, encouraging feedback.
- **FPDF**: For creating PDF reports with tables, charts, and styled content.
- **Matplotlib & Seaborn**: For generating time vs. accuracy scatter plots.
- **Glob**: For automating file discovery.
- **OS**: For managing file paths with configurable directories.

**Features**

- **Data Processing**: Parses JSON files and generates `overall_*.json`, `subject_*.csv`, `weak_*.csv`, and `chart_*.png`.
- **Feedback Generation**:
  - Motivational introduction highlighting the strongest subject and overall accuracy.
  - Detailed breakdown of subject-wise and chapter-wise performance, including all weak chapters.
  - Time management insights and actionable recommendations.
  - Saves feedback as `feedback_*.txt`.
- **PDF Reports**:
  - Professional layout with title, MathonGo logo, and footer.
  - Tables for subject-wise and chapter-wise performance.
  - Embedded time vs. accuracy charts.
  - Formatted feedback text, skipping unwanted lines.
  - Saves as `feedback_*.pdf`.
- **Automation**: Processes all JSON files in `data/` using `glob`.
- **Error Handling**: Validates inputs and handles missing files or API errors.

**Project Structure**

```
mathango-feedback-system/
├── main.py                  # Main automation script orchestrating tasks
├── task1_processing.py      # Data processing and chart generation
├── task2_aiprompting.py     # Feedback generation with Groq API
├── task3_pdf.py             # PDF report generation
├── mathango(1).ipynb        # Colab notebook with full workflow
├── README.md                # Project documentation
├── requirements.txt         # Dependencies
├── .gitignore               # Excludes output files
├── data/
│   ├── sample_submission_analysis_1.json  # Input JSON for student 1
│   ├── sample_submission_analysis_2.json  # Input JSON for student 2
│   ├── sample_submission_analysis_3.json  # Input JSON for student 3
├── output/                  # Empty (in .gitignore)
└── mathongo_logo.jpeg       # Logo for PDF branding
```

**Setup Instructions**

1. **Prerequisites**:
   - Install Python 3.8+.
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Obtain a Groq API key from [x.ai/api](https://x.ai/api).

2. **Configure Paths**:
   - Open `main.py`, `task1_processing.py`, `task2_aiprompting.py`, and `task3_pdf.py`.
   - Replace `BASE_PATH = "PATH_TO_YOUR_DATA_DIRECTORY"` with your directory path, e.g., `/home/user/mathango_data/` or `C:\Users\user\Documents\mathango_data\`.
   - Ensure `data/` contains input JSON files (`sample_submission_analysis_*.json`) and `mathongo_logo.jpeg` is in the project root.

3. **Environment Configuration**:
   - Set the Groq API key:
     ```bash
     export GROQ_API_KEY=your_key
     ```
   - For Windows:
     ```cmd
     set GROQ_API_KEY=your_key
     ```

4. **Running the Script**:
   - Execute:
     ```bash
     python main.py
     ```
   - Outputs (`overall_*.json`, `subject_*.csv`, `weak_*.csv`, `chart_*.png`, `feedback_*.txt`, `feedback_*.pdf`) are saved in `output/`.

**Implementation Details**

### Task 1: Data Processing
- Parses JSON files to extract overall, subject-wise, and chapter-wise performance metrics.
- Generates time vs. accuracy scatter plots using Matplotlib and Seaborn.
- Saves outputs as `overall_*.json`, `subject_*.csv`, `weak_*.csv`, and `chart_*.png`.

### Task 2: Feedback Generation
- Builds a prompt with:
  - Personalized introduction highlighting the strongest subject and overall accuracy.
  - Performance breakdown for subjects and all weak chapters.
  - Time management insights and three actionable recommendations.
- Uses Groq API (`llama3-70b-8192`, `temperature=0.7`, `max_tokens=800`).
- Saves feedback as `feedback_*.txt`.

### Task 3: PDF Generation
- Creates PDFs with:
  - Title, MathonGo logo (or placeholder), and footer.
  - Tables for subject-wise and chapter-wise performance.
  - Embedded time vs. accuracy charts.
  - Formatted feedback text, skipping unwanted lines.
- Uses FPDF for styling (blue table headers, Helvetica fonts).

### Automation
- Uses `glob` to process all `sample_submission_analysis_*.json` files in `data/`.
- Implements rate limiting (5-second delay) for Groq API calls.
- Handles errors for missing files, invalid inputs, or API failures.


**Submission**
- **PDFs**: Hosted on a public Google Drive link: [MathonGo PDFs](https://drive.google.com/drive/folders/1COyfUF4Gv0KDCuDKpCTcqo4XRnNfFMLl?usp=sharing ) (view-only).

**Sample Output**
Below is a sample time vs. accuracy chart generated for a student:

![Sample Chart](https://github.com/PAlakj02/MathForJEE/blob/5075cc99d7d541684e483f586e31faffc6ed5e5b/data/chart_1.png)

**Troubleshooting**
- Ensure `GROQ_API_KEY` is set.
- Verify input JSON files in `data/` match the expected format.
- Check `output/` for generated files.
- For path issues, update `BASE_PATH` in all `.py` files.


**Contact**
For issues, refer to [x.ai/api](https://x.ai/api) for API-related queries.
