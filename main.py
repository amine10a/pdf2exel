from flask import Flask, render_template, request, redirect, url_for, flash
import os

# Import the necessary functions for PDF to Excel processing
import pandas as pd
import fitz  # PyMuPDF
import xlsxwriter

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_excel(pdf_path, excel_path):
    try:
        pdf_document = fitz.open(pdf_path)
        num_pages = pdf_document.page_count
        image_text_data = []

        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Image_Text')
            worksheet.set_column('B:B', 40)  # Adjust column width for text

            # Write headers
            worksheet.write('A1', 'Image Path')
            worksheet.write('B1', 'Text')

            row = 1  # Start row for writing data

            for page_num in range(num_pages):
                page = pdf_document.load_page(page_num)
                images = page.get_images(full=True)
                for img_index, img_info in enumerate(images):
                    img_bytes = pdf_document.extract_image(img_info[0])
                    img_format = img_bytes["ext"]
                    image_filename = f'image_{page_num + 1}_{img_index + 1}.{img_format}'
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    with open(image_path, 'wb') as img_file:
                        img_file.write(img_bytes["image"])
                    
                    text = page.get_text()
                    image_text_data.append((image_path, text))

                    # Check if image file exists before inserting into Excel
                    if os.path.isfile(image_path):
                        # Insert image into Excel and adjust size
                        worksheet.insert_image(row, 0, image_path, {'x_offset': 5, 'y_offset': 5, 'x_scale': 0.5, 'y_scale': 0.5})

                        # Write image path and text
                        worksheet.write_url(row, 1, f'external:{image_path}', string=text)
                        row += 1
                    else:
                        print(f"Image file '{image_path}' not found.")

        pdf_document.close()
        return True
    except Exception as e:
        print(f"Error occurred during PDF to Excel conversion: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the file has been uploaded
        if 'file' not in request.files:
            flash('Aucun fichier n\'a été sélectionné.')
            return redirect(request.url)
        
        file = request.files['file']

        # Check if no file has been selected
        if file.filename == '':
            flash('Aucun fichier n\'a été sélectionné.')
            return redirect(request.url)

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Save the file to the uploads folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Convert PDF to Excel
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

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
