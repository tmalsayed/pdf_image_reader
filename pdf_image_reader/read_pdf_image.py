import PyPDF2
from pdf2image import convert_from_path
import easyocr
import numpy as np
from PIL import Image

def extract_order_number(text):
    # Implement a function to extract the order number from text
    # For example, using regex if the order number follows a pattern
    pass

def split_pdf_by_order_number(pdf_path, poppler_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader

    for page_num in range(len(pdf_reader.pages)):
        images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1, poppler_path=poppler_path)
        for image in images:
            np_image = np.array(image)

            # Calculate the coordinates for the top right corner
            crop_width, crop_height = 600, 100  # Size of the cropped area
            x = np_image.shape[1] - crop_width  # x coordinate for top right
            y = 200  # y coordinate (top of the image)
            cropped_image = np_image[y:y+crop_height, x:x+crop_width]

            # Convert the cropped NumPy array back to a PIL image
            pil_cropped_image = Image.fromarray(cropped_image)

            # Save the cropped image
            cropped_image_filename = f'cropped_page_{page_num + 1}.png'
            pil_cropped_image.save(cropped_image_filename)
            print(f"Cropped image saved as {cropped_image_filename}")

            results = reader.readtext(cropped_image)
            text = ' '.join([result[1] for result in results])
            print(text)
            order_number = extract_order_number(text)

            if order_number:
                writer = PyPDF2.PdfWriter()
                writer.add_page(pdf_reader.pages[page_num])
                with open(f'order_{order_number}.pdf', 'wb') as output_pdf:
                    writer.write(output_pdf)

poppler_path = 'bin'  # Update this to your Poppler bin path
split_pdf_by_order_number('1706114078273-db29e934-62a1-4334-bd11-fcd0f3faf57e_1.pdf', poppler_path)
