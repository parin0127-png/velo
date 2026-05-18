import os 
import pdfplumber 

def read_file(path):
    if not os.path.exists(path):
        return "File not found"
    
    if path.endswith(".pdf"):
        return read_pdf(path)
    

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

def read_pdf(path):
    try:
        with pdfplumber.open(path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except ImportError:
        return "Install pdfplumber: pip install pdfplumber"