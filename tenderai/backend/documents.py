from io import BytesIO
from pypdf import PdfReader


def extract_pdf(data: bytes) -> str:
    if not data.startswith(b"%PDF-"):
        raise ValueError("Choose a PDF document.")
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("Unlock the PDF first.")
        if len(reader.pages) > 40:
            raise ValueError("Choose a PDF with 40 pages or fewer.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The PDF could not be read.") from exc
    if not text:
        raise ValueError("This scan has no selectable text. Paste its scope manually.")
    return text
