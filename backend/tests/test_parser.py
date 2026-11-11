import io

import docx
import pytest

from resume_parser import extract_text_from_file, extract_text_from_path
from tests.conftest import SAMPLES


def _docx_bytes(*paragraphs):
    document = docx.Document()
    for p in paragraphs:
        document.add_paragraph(p)
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


def test_reads_docx_from_stream():
    text = extract_text_from_file(_docx_bytes("Jane Doe", "Python, SQL"), "cv.DOCX")
    assert text == "Jane Doe\nPython, SQL"


def test_reads_bundled_pdf():
    text = extract_text_from_path(str(SAMPLES / "SampleResume.pdf"))
    assert "python" in text.lower()


def test_rejects_unsupported_type():
    with pytest.raises(ValueError):
        extract_text_from_file(io.BytesIO(b"hello"), "resume.txt")
    with pytest.raises(ValueError):
        extract_text_from_path("resume.txt")
