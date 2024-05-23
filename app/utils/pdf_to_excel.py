import os
import pandas as pd
import fitz  # PyMuPDF
import xlsxwriter

def pdf_to_excel(pdf_path, excel_path):
    try:
        pdf_document = fitz.open(pdf_path)
        num_pages = pdf_document.page_count
        image_text_data = []

        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Image_Text')
            worksheet.set_column('B:B', 40)

            worksheet.write('A1', 'Image Path')
            worksheet.write('B1', 'Text')

            row = 1

            for page_num in range(num_pages):
                page = pdf_document.load_page(page_num)
                images = page.get_images(full=True)
                for img_index, img_info in enumerate(images):
                    img_bytes = pdf_document.extract_image(img_info[0])
                    img_format = img_bytes["ext"]
                    image_filename = f'image_{page_num + 1}_{img_index + 1}.{img_format}'
                    image_path = os.path.join('app/static/uploads', image_filename)
                    with open(image_path, 'wb') as img_file:
                        img_file.write(img_bytes["image"])

                    text = page.get_text()
                    image_text_data.append((image_path, text))

                    if os.path.isfile(image_path):
                        worksheet.insert_image(row, 0, image_path, {'x_offset': 5, 'y_offset': 5, 'x_scale': 0.5, 'y_scale': 0.5})
                        worksheet.write_url(row, 1, f'external:{image_path}', string=text)
                        row += 1
                    else:
                        print(f"Image file '{image_path}' not found.")

        pdf_document.close()
        return True
    except Exception as e:
        print(f"Error occurred during PDF to Excel conversion: {e}")
        return False
