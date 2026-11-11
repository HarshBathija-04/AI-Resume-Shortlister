import docx
import pypdf


def read_pdf(file_obj):
    pages = (page.extract_text() for page in pypdf.PdfReader(file_obj).pages)
    return "".join(text + "\n" for text in pages if text)


def read_docx(file_obj):
    return "\n".join(p.text for p in docx.Document(file_obj).paragraphs)


def extract_text_from_file(file_obj, filename):
    filename = filename.lower()
    if filename.endswith(".pdf"):
        return read_pdf(file_obj)
    if filename.endswith(".docx"):
        return read_docx(file_obj)
    raise ValueError("Unsupported file type. Please upload PDF or DOCX.")


def extract_text_from_path(path):
    with open(path, "rb") as file_obj:
        return extract_text_from_file(file_obj, str(path))
