import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def handle_file(file_path, subject):
    image_files = []

    # Check if the input file is a PDF or an image
    if file_path.lower().endswith('.pdf'):
        # Open the PDF file
        pdf_document = fitz.open(file_path)
        
        # Convert each page to an image
        zoom_x = 10.0  # horizontal zoom
        zoom_y = 10.0  # vertical zoom
        matrix = fitz.Matrix(zoom_x, zoom_y)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(matrix=matrix)
            image_file = f'page_{page_num + 1}.png'
            pix.save(image_file)
            image_files.append(image_file)
    
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_files.append(file_path)
    
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or an image file.")
    
    GOOGLE_API_KEY = 'AIzaSyA69r6qP6dBD1agDCBYgf1fk4xMNLogovk'
    genai.configure(api_key=GOOGLE_API_KEY)

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    extracted_text = ""

    # Process each image with the generative model
    for image_file in image_files:
        image = Image.open(image_file)
        result = model.generate_content(['''EXTRACT TEXT FROM IT,
                                         IF IT'S IN A TABLE EXTRACT THE TABLE,
                                         IF THERE IS A DIAGRAM SUMMARIZE THE DIAGRAM''', image],
                                         safety_settings=safety_settings)
        extracted_text += result.text + "\n\n"

    # Process the extracted text with the generative model    
    response = model.generate_content(
        [f'''I have extracted text from a pdf, which is my {subject} assignment. Please answer these questions:{extracted_text}.
             NOTE: 1. Start every answer with Ans1-, next with Ans2- and so on.
                   2. Don't use to **bold** or *italics* or ## for headings, just normal text without any markdown.
                   3. You can use a line break for next line.
                   4. If the question says to draw a diagram don't draw it.'''],
        safety_settings=safety_settings
    )
    
    return response.text
