from flask import Flask, render_template, request, redirect, url_for
import os
from scripts.backend import main as backend_func
from scripts.Resume import pdf_to_json as resume_processing_function
#from scripts.linkedin import linkedin_integration_function
# Add imports for other scripts if needed

app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template('template/home.html')

# About Us page route
@app.route('/about_us')
def about_us():
    return render_template('template/about_us.html')

# Manual page route
@app.route('/manual')
def manual():
    return render_template('manual.html')

# Signup page route
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Resume Upload route
@app.route('/resumeupload', methods=['GET', 'POST'])
def resumeupload():
    if request.method == 'POST':
        # Process the resume file uploaded by the user
        resume_file = request.files['resume']
        if resume_file:
            filepath = os.path.join('static/uploads', resume_file.filename)
            resume_file.save(filepath)
            # Call the resume processing function from Resume.py
            processed_data = resume_processing_function(filepath)
            return render_template('result.html', processed_data=processed_data)
    return render_template('resumeupload.html')

# LinkedIn Integration route
# @app.route('/linkedin', methods=['POST'])
# def linkedin():
#     linkedin_data = request.form.get('linkedin_data')  # Get LinkedIn data (adjust based on your logic)
#     if linkedin_data:
#         # Call LinkedIn integration function from linkedin.py
#         result = linkedin_integration_function(linkedin_data)
#         return render_template('result.html', result=result)
#     return redirect(url_for('home'))

# Result page route
@app.route('/result')
def result():
    return render_template('result.html')

# Resume Button route (if there's functionality tied to it)
@app.route('/resume_button')
def resume_button():
    return render_template('resume_button.html')

# Backend logic handling (optional based on your project's needs)
@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.form.get('data')  # Example, adjust according to your form
    if data:
        processed_data = backend_func(data)
        return render_template('result.html', processed_data=processed_data)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=7896)
