import PyPDF2
import docx


def read_pdf(file_obj):
    text = ""
    reader = PyPDF2.PdfReader(file_obj)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def read_docx(file_obj):
    doc = docx.Document(file_obj)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text_from_file(file_obj):
    filename = (file_obj.filename or "").lower()

    if filename.endswith(".pdf"):
        return read_pdf(file_obj)
    if filename.endswith(".docx"):
        return read_docx(file_obj)

    raise ValueError("Unsupported file type. Please upload PDF or DOCX.")


def extract_text_from_path(path):
    lowered = path.lower()
    if lowered.endswith(".pdf"):
        with open(path, "rb") as file_obj:
            return read_pdf(file_obj)
    if lowered.endswith(".docx"):
        with open(path, "rb") as file_obj:
            return read_docx(file_obj)
    raise ValueError("Unsupported file type: " + path)
