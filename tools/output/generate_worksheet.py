import os
import re
import uuid
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def generate_student_worksheet_doc(sections: list) -> str:
    doc = Document()

    # --- Title ---
    title = doc.add_paragraph()
    title_run = title.add_run("Student Worksheet")
    title_run.font.name = "Poppins"
    title_run.font.bold = True
    title_run.font.size = Pt(24)
    title_run.font.color.rgb = RGBColor(0, 0, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()  # spacing

    # --- Helper: Detect translation using same strategy as PPTX ---
    def split_translation(content: str):
        content = content.strip()

        # 1️⃣ If explicit \n\n separator exists
        if "\n\n" in content:
            english_part, translation_part = content.split("\n\n", 1)
            return english_part.strip(), translation_part.strip()

        # 2️⃣ Otherwise detect translation start using non‑Latin scripts
        # This includes Devanagari, Arabic, Chinese, Japanese, Korean, Cyrillic, etc.
        match = re.search(r'[^\x00-\x7F]', content)
        if match:
            split_index = match.start()
            english_part = content[:split_index].rstrip()
            translation_part = content[split_index:].lstrip()
        else:
            english_part = content
            translation_part = ""

        return english_part, translation_part

    # --- Process each section ---
    for section in sections:
        # Section Heading
        heading = doc.add_paragraph()
        heading_run = heading.add_run(section["section"])
        heading_run.font.name = "Poppins SemiBold"
        heading_run.font.size = Pt(18)
        heading_run.font.color.rgb = RGBColor(0, 0, 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()  # spacing

        content = section["content"].strip()
        english_part, translation_part = split_translation(content)

        # --- English Content (Blue) ---
        if english_part:
            for paragraph_text in english_part.split("\n"):
                clean_text = paragraph_text.strip()
                if not clean_text:
                    continue
                p = doc.add_paragraph()
                run = p.add_run(clean_text)
                run.font.name = "Poppins"
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(0, 102, 204)  # 🔵 Blue
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Spacer
        if translation_part:
            doc.add_paragraph()

        # --- Translation Content (Red) ---
        if translation_part:
            for paragraph_text in translation_part.split("\n"):
                clean_text = paragraph_text.strip()
                if not clean_text:
                    continue
                p = doc.add_paragraph()
                run = p.add_run(clean_text)
                run.font.name = "Poppins"
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(255, 0, 0)  # 🔴 Red
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()  # extra space after each section

    # --- Save the file ---
    save_dir = "data/outputs/worksheets"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"student_worksheet_{uuid.uuid4().hex}.docx"
    path = os.path.join(save_dir, filename)
    doc.save(path)

    return path
