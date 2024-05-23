from flask import Flask, render_template, request, redirect, url_for, flash
import os
from utils.pdf_to_excel import pdf_to_excel


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'uploads')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier n\'a été sélectionné.')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('Aucun fichier n\'a été sélectionné.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            excel_filename = os.path.splitext(file.filename)[0] + '.xlsx'
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
            success = pdf_to_excel(file_path, excel_path)
            if success:
                return redirect(url_for('download_file', filename=excel_filename))
            else:
                flash('Une erreur est survenue lors de la conversion du PDF en Excel.')
                return redirect(request.url)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
#run
if __name__ == '__main__':
    app.run(debug=True)
