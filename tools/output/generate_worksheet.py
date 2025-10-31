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
    doc.add_paragraph()

    def split_parts(content: str):
        content = content.strip()
        english_part, translation_part, supports_part = "", "", ""

        # First split by \n\n for main division
        parts = content.split("\n\n")
        if len(parts) == 3:
            english_part, translation_part, supports_part = parts
        elif len(parts) == 2:
            english_part, translation_part = parts
        else:
            # fallback to non-Latin script detection
            match = re.search(r'[^\x00-\x7F]', content)
            if match:
                split_index = match.start()
                english_part = content[:split_index].rstrip()
                remainder = content[split_index:].lstrip()
                # Try splitting remainder into translation and supports
                support_match = re.search(r'Supports:\s*', remainder)
                if support_match:
                    support_index = support_match.start()
                    translation_part = remainder[:support_index].rstrip()
                    supports_part = remainder[support_index:].lstrip()
                else:
                    translation_part = remainder
            else:
                english_part = content

        return english_part.strip(), translation_part.strip(), supports_part.strip()

    # --- Add sections ---
    for section in sections:
        heading = doc.add_paragraph()
        heading_run = heading.add_run(section["section"])
        heading_run.font.name = "Poppins SemiBold"
        heading_run.font.size = Pt(18)
        heading_run.font.color.rgb = RGBColor(0, 0, 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        doc.add_paragraph()

        # Split content
        content = section["content"]
        english_part, translation_part, supports_part = split_parts(content)

        # 🔵 English
        if english_part:
            for line in english_part.split("\n"):
                if line.strip():
                    p = doc.add_paragraph()
                    run = p.add_run(line.strip())
                    run.font.name = "Poppins"
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(0, 102, 204)  # Blue
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # 🔴 Translated
        if translation_part:
            for line in translation_part.split("\n"):
                if line.strip():
                    p = doc.add_paragraph()
                    run = p.add_run(line.strip())
                    run.font.name = "Poppins"
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(255, 0, 0)  # Red
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # 🟢 Supports
        if supports_part:
            for line in supports_part.split("\n"):
                if line.strip():
                    p = doc.add_paragraph()
                    run = p.add_run(line.strip())
                    run.font.name = "Poppins"
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(0, 153, 0)  # Green
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()

    # --- Save the file ---
    save_dir = "data/outputs/worksheets"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"student_worksheet_{uuid.uuid4().hex}.docx"
    path = os.path.join(save_dir, filename)
    doc.save(path)

    return path
