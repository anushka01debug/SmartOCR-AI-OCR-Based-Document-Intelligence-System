import pytesseract
from PIL import Image
import io
import time
import os
import fitz  # PyMuPDF
from classifier import load_settings
def get_tesseract_cmd():
    settings = load_settings()
    return settings.get(
        "tesseract_path",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
def test_tesseract_connection(path=None):
    """Tests if Tesseract OCR binary is reachable and running."""
    if path is None:
        path = get_tesseract_cmd()
    
    old_cmd = pytesseract.pytesseract.tesseract_cmd
    try:
        pytesseract.pytesseract.tesseract_cmd = path
        # Running simple version command
        version = pytesseract.get_tesseract_version()
        return True, str(version)
    except Exception as e:
        return False, str(e)
    finally:
        pytesseract.pytesseract.tesseract_cmd = old_cmd
def run_ocr_on_image(pil_img, lang="eng"):
    """Runs Tesseract OCR on a PIL Image."""
    # Set path from config
    pytesseract.pytesseract.tesseract_cmd = get_tesseract_cmd()
    
    start_time = time.time()
    try:
        text = pytesseract.image_to_string(pil_img, lang=lang)
        duration = time.time() - start_time
        return text, duration
    except Exception as e:
        # Fallback error messaging
        error_msg = f"OCR Error: Could not execute pytesseract. Details: {str(e)}\n\nPlease ensure Tesseract-OCR is installed on your system and the path configured in 'OCR Settings' is correct."
        return error_msg, 0.0
def process_pdf_document(pdf_bytes):
    """
    Opens a PDF document using PyMuPDF (fitz) and gathers basic statistics.
    Returns:
      - doc: fitz.Document object
      - info: dict of page count and text selectable details
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    
    pages_info = []
    for i in range(page_count):
        page = doc.load_page(i)
        # Check if text is selectable
        txt = page.get_text().strip()
        has_text = len(txt) > 20
        pages_info.append({
            "page_num": i + 1,
            "has_selectable_text": has_text,
            "char_count": len(txt)
        })
        
    return doc, pages_info
def extract_page_text_or_render(doc, page_num, zoom_factor=2.0):
    """
    Extracts text from a specific PDF page.
    If the page does not contain digital selectable text, renders it to a PIL Image 
    so it can be preprocessed and OCR'ed.
    Returns:
      - text: str (Extracted text if digital, otherwise None)
      - image: PIL Image (If scanned, otherwise None)
      - is_digital: bool
    """
    page = doc.load_page(page_num)
    text = page.get_text().strip()
    
    # Threshold: if it has more than 30 characters of selectable text, treat it as a digital page
    if len(text) > 30:
        return text, None, True
    
    # Otherwise, it's likely a scanned page - render it to an image
    # Higher matrix value yields higher resolution (zoom_factor=2.0 is roughly 150 DPI, zoom_factor=3.0 is 216 DPI)
    mat = fitz.Matrix(zoom_factor, zoom_factor)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_data))
    
    return None, pil_img, False
