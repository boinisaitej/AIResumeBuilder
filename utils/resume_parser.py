import io
import re


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if text.strip():
            return text
    except Exception:
        pass

    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
        if text.strip():
            return text
    except Exception:
        pass


    return text


def parse_basic_info(text: str) -> dict:
    result = {"raw_text": text, "email": "", "phone": "", "name": ""}
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        result["name"] = lines[0]
    email_m = re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", text, re.I)
    phone_m = re.search(r"[\+\d][\d\s\-\(\)]{8,15}", text)
    if email_m:
        result["email"] = email_m.group()
    if phone_m:
        result["phone"] = phone_m.group().strip()
    return result
