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

    doc.add_paragraph()  # Blank line for spacing

    # --- Helper: detect translation boundary ---
    def detect_translation_split(content: str):
        """
        Detects where translation begins by scanning for non-Latin characters.
        Covers most major language scripts.
        """
        # Unicode ranges for non-Latin scripts
        non_latin_pattern = re.compile(
            r"[\u0370-\u03FF\u0400-\u04FF\u0590-\u05FF\u0600-\u06FF\u0750-\u077F"
            r"\u08A0-\u08FF\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF"
            r"\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F"
            r"\u0E00-\u0E7F\u0F00-\u0FFF\u10A0-\u10FF\u3040-\u30FF\u4E00-\u9FFF"
            r"\uAC00-\uD7AF]"
        )

        if "\n\n" in content:
            english_part, translation_part = content.split("\n\n", 1)
        else:
            match = non_latin_pattern.search(content)
            if match:
                split_index = match.start()
                english_part = content[:split_index].strip()
                translation_part = content[split_index:].strip()
            else:
                english_part = content.strip()
                translation_part = ""
        return english_part, translation_part

    # --- Loop through each section ---
    for section in sections:
        # Section Heading
        heading = doc.add_paragraph()
        heading_run = heading.add_run(section["section"])
        heading_run.font.name = "Poppins SemiBold"
        heading_run.font.size = Pt(18)
        heading_run.font.color.rgb = RGBColor(0, 0, 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()  # Small space between heading and content

        content = section["content"].strip()
        english_part, translation_part = detect_translation_split(content)

        # English content (Blue)
        if english_part:
            p_eng = doc.add_paragraph()
            run_eng = p_eng.add_run(english_part)
            run_eng.font.name = "Poppins"
            run_eng.font.size = Pt(12)
            run_eng.font.color.rgb = RGBColor(0, 102, 204)  # Blue
            p_eng.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Translation content (Red)
        if translation_part:
            p_trans = doc.add_paragraph()
            run_trans = p_trans.add_run(translation_part)
            run_trans.font.name = "Poppins"
            run_trans.font.size = Pt(12)
            run_trans.font.color.rgb = RGBColor(255, 0, 0)  # Red
            p_trans.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()  # Add spacing after each section

    # --- Save file ---
    save_dir = "data/outputs/worksheets"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"student_worksheet_{uuid.uuid4().hex}.docx"
    path = os.path.join(save_dir, filename)
    doc.save(path)

    return path
