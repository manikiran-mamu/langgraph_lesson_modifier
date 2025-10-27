import os
import uuid
from docx import Document

def generate_student_worksheet_doc(sections: list) -> str:
    doc = Document()
    doc.add_heading("Student Worksheet", level=1)

    for section in sections:
        doc.add_heading(section["section"], level=2)
        doc.add_paragraph(section["content"])

    save_dir = "data/outputs/worksheets"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"student_worksheet_{uuid.uuid4().hex}.docx"
    path = os.path.join(save_dir, filename)
    doc.save(path)
    return path
