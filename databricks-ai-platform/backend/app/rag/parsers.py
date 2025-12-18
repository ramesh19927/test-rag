"""Simple parsers for different document types."""
from pathlib import Path
import docx2txt
import PyPDF2


def parse_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return parse_pdf(path)
    if path.suffix.lower() in {".doc", ".docx"}:
        return parse_docx(path)
    return path.read_text()


def parse_pdf(path: Path) -> str:
    text = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def parse_docx(path: Path) -> str:
    return docx2txt.process(str(path)) or ""
