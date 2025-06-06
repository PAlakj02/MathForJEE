from flask import Flask, request, send_file, render_template_string
import os
import json
import pandas as pd
from werkzeug.utils import secure_filename
from fpdf import FPDF
import glob
import time

app = Flask(__name__)
base_path = "/content/drive/MyDrive/mathango_jsonfiles"
upload_folder = f"{base_path}/uploads"
os.makedirs(upload_folder, exist_ok=True)
app.config['UPLOAD_FOLDER'] = upload_folder

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>MathonGo Performance Feedback</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
        h1 { color: #333; text-align: center; }
        .upload-form { max-width: 600px; margin: auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .file-input { margin: 10px 0; }
        .submit-btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .submit-btn:hover { background-color: #0056b3; }
        .results { margin-top: 20px; }
        .result-item { margin: 10px 0; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>MathonGo Student Performance Feedback</h1>
    <div class="upload-form">
        <form method="post" enctype="multipart/form-data" action="/upload">
            <div class="file-input">
                <label for="file">Upload JSON Files (overall_*.json):</label><br>
                <input type="file" name="files[]" multiple accept=".json">
            </div>
            <button type="submit" class="submit-btn">Generate Reports</button>
        </form>
    </div>
    {% if results %}
    <div class="results">
        <h2>Generated Reports</h2>
        {% for result in results %}
        <div class="result-item">
            <p>Student {{ result.student_id }}: <a href="/download/{{ result.student_id }}">Download PDF</a></p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

# Include load_student_data, build_prompt, generate_feedback, and text_to_pdf functions
# ... [Copy from main.py above] ...

@app.route('/')
def index():
    print("Accessing root endpoint")
    return render_template_string(html_template)

@app.route('/upload', methods=['POST'])
def upload_files():
    print("Received upload request")
    uploaded_files = request.files.getlist("files[]")
    results = []
    
    for file in uploaded_files:
        if file and file.filename.endswith('.json'):
            filename = secure_filename(file.filename)
            student_id = filename.split('_')[-1].split('.')[0]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"Saved file: {file_path}")
            
            overall, subject_df, weak_df = load_student_data(student_id, base_path)
            if overall is None:
                print(f"Failed to load data for student {student_id}")
                continue
            
            prompt = build_prompt(overall, subject_df, weak_df)
            feedback = generate_feedback(prompt)
            if not feedback:
                print(f"Failed to generate feedback for student {student_id}")
                continue
            
            txt_path = f"{base_path}/feedback/feedback_{student_id}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(feedback)
            
            chart_path = f"{base_path}/output/chart_{student_id}.png"
            pdf_path = f"{base_path}/feedback/feedback_{student_id}.pdf"
            text_to_pdf(feedback, pdf_path, student_id, chart_path, subject_df, weak_df)
            print(f"Generated PDF for student {student_id}")
            
            results.append({"student_id": student_id})
            time.sleep(5)
    
    return render_template_string(html_template, results=results)

@app.route('/download/<student_id>')
def download_file(student_id):
    pdf_path = f"{base_path}/feedback/feedback_{student_id}.pdf"
    print(f"Sending PDF: {pdf_path}")
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)