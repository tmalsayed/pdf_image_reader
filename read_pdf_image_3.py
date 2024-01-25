import PyPDF2
from pdf2image import convert_from_path
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
import re
import os
import tkinter as tk
from tkinter import filedialog

def extract_order_number(text):
    match = re.search(r'Orderno:\s*(WEBO\d+)', text)
    return match.group(1) if match else None

def select_pdf_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path

def split_pdf_by_order_number(pdf_path, poppler_path):
    if not pdf_path:  # If no file is selected, return
        return

    pdf_reader = PyPDF2.PdfReader(pdf_path)
    reader = easyocr.Reader(['en'])
    order_writers = {}
    non_identified_writer = PyPDF2.PdfWriter()
    non_identified_pages = []

    for page_num in range(len(pdf_reader.pages)):
        print("Processing page:", page_num)
        images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1, poppler_path=poppler_path)
        for image in images:
            np_image = np.array(image)
            crop_width, crop_height = 600, 150
            x = np_image.shape[1] - crop_width
            y = 200
            cropped_image = np_image[y:y + crop_height, x:x + crop_width]

            results = reader.readtext(cropped_image)
            text = ' '.join([result[1] for result in results])
            
            order_number = extract_order_number(text)
            if order_number:
                if order_number not in order_writers:
                    order_writers[order_number] = {'writer': PyPDF2.PdfWriter(), 'pages': 0}
                order_writers[order_number]['writer'].add_page(pdf_reader.pages[page_num])
                order_writers[order_number]['pages'] += 1
            else:
                non_identified_writer.add_page(pdf_reader.pages[page_num])
                non_identified_pages.append(page_num + 1)

    directory = os.path.dirname(pdf_path)
    order_data = []
    for order_number, info in order_writers.items():
        output_pdf_path = os.path.join(directory, f'{order_number}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf:
            info['writer'].write(output_pdf)
        print(f"PDF saved as {output_pdf_path}")
        order_data.append({'Order Number': order_number, 'Number of Pages': info['pages']})

    # Save non-identified pages into a separate PDF if there are any
    if non_identified_pages:
        non_identified_pdf_path = os.path.join(directory, f'non_identified_{len(non_identified_pages)}.pdf')
        with open(non_identified_pdf_path, 'wb') as output_pdf:
            non_identified_writer.write(output_pdf)
        print(f"Non-identified PDF saved as {non_identified_pdf_path}")
    else:
        print("No non-identified pages found.")

    # Create an Excel file with the order data
    if order_data:  # Check if there is any order data
        df = pd.DataFrame(order_data)
        excel_path = os.path.join(directory, 'order_pages.xlsx')
        df.to_excel(excel_path, index=False)
        print(f"Excel file saved as {excel_path}")
    else:
        print("No order data found to save to Excel.")

poppler_path = 'bin'
pdf_path = select_pdf_file()  # Open file dialog to select PDF file
split_pdf_by_order_number(pdf_path, poppler_path)
