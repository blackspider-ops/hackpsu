from flask import Flask, request, render_template, redirect, url_for
import os
from scripts.backend import main as backend_func
from scripts.Resume import pdf_to_json as resume_processing_function
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join('Zoodu','static', 'files')  # Save to static/files directory
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Renamed the route to avoid conflict
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    
    # Check if the POST request has the file part
    if 'resume' not in request.files:
        return "No file part"
    
    file = request.files['resume']
    
    # If the user does not select a file
    if file.filename == '':
        return "No selected file"
    
    # Check if the file is allowed
    if file and allowed_file(file.filename):
        # Sanitize the file name and save it to the specified folder
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File uploaded successfully to static/files"
    
    return "Invalid file type"

# Resume Upload route
@app.route('/resumeupload', methods=['GET', 'POST'])
def resumeupload():
    if request.method == 'POST':
        # Process the resume file uploaded by the user
        resume_file = request.files['resume']
        if resume_file and allowed_file(resume_file.filename):
            # Secure the file name and save the file
            filename = secure_filename(resume_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume_file.save(filepath)
            
            # Call the resume processing function from Resume.py
            processed_data = resume_processing_function(filepath)
            return render_template('result.html', processed_data=processed_data)
    return render_template('resumeupload.html')

# Handle the POST request to save the file
@app.route('/save_file', methods=['POST'])
def save_file():
    # Check if the post request has the file part
    if 'resume' not in request.files:
        return "No file part"
    
    file = request.files['resume']
    
    # If user does not select file
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File uploaded successfully"
    
    return "Invalid file type"

# Resume Button route
@app.route('/resume_button')
def resume_button():
    return render_template('resume_button.html')

# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# About Us page route
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

# Manual page route
@app.route('/manual')
def manual():
    return render_template('manual.html')

# Signup page route
@app.route('/signup')
def signup():
    return render_template('signup.html')



# Result page route
@app.route('/result.html')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
