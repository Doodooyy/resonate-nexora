import fitz # PyMuPDF
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def clean_text(text: str) -> str:
    """Basic normalization of whitespace and special characters."""
    # Replace non-breaking spaces and unusual characters
    text = text.replace('\xa0', ' ')
    # Normalize newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()

def parse_pdf(pdf_path: str) -> str:
    """Main entry point for parsing a PDF resume."""
    raw_text = extract_text_from_pdf(pdf_path)
    return clean_text(raw_text)
