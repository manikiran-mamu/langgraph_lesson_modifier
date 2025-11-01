from graph.schema import State
from docx import Document
from docx.shared import Pt
import os
import uuid

TEMPLATE_PATH = "templates/lesson_template.docx"
OUTPUT_DIR = "data/outputs/word"

ACTIVITY_TABLE_MAPPING = {
    ("Lesson Intro", "Teacher Activities"): "intro_teacher",
    ("Demonstration, model, or mini-lesson (\"I Do\")", "Teacher Activities"): "i_do_teacher",
    ("Shared Learning or Guided Practice (\"We Do\")", "Teacher Activities"): "we_do_teacher",
    ("Independent or Collaborative Small Group Work (\"You Do\" / \"Y’all Do\" Assessment)", "Teacher Activities"): "you_do_teacher",
    ("Lesson Intro", "Desired Student Actions and Potential Misconceptions"): "intro_student",
    ("Demonstration, model, or mini-lesson (\"I Do\")", "Desired Student Actions and Potential Misconceptions"): "i_do_student",
    ("Shared Learning or Guided Practice (\"We Do\")", "Desired Student Actions and Potential Misconceptions"): "we_do_student",
    ("Independent or Collaborative Small Group Work (\"You Do\" / \"Y’all Do\" Assessment)", "Desired Student Actions and Potential Misconceptions"): "you_do_student",
}

def insert_into_cell(cell, content: str):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(content.strip())
    run.font.name = "Poppins"
    run.font.size = Pt(11)

def save_node(state: State) -> State:
    print("📝 Filling lesson template...")

    sections = state.get("sections")
    if not sections:
        raise ValueError("No 'sections' data found in state.")

    doc = Document(TEMPLATE_PATH)

    # Replace Title
    if doc.paragraphs:
        title_paragraph = doc.paragraphs[0]
        title_paragraph.text = "Lesson Plan"
        run = title_paragraph.runs[0] if title_paragraph.runs else title_paragraph.add_run()
        run.font.name = "Poppins"
        run.font.size = Pt(24)
        run.bold = True

    # === 1. Paragraph-based matching for "CONTENT", "LANGUAGE", etc. ===
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip().upper()

        if text.startswith("STANDARDS ADDRESSED") and "standards" in sections:
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i + 1].text = sections["standards"]

        elif "CONTENT:" in text and "content" in sections:
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i + 1].text = sections["content"]

        elif "LANGUAGE:" in text and "language" in sections:
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i + 1].text = sections["language"]

        elif text.startswith("SO WHAT") and "purpose" in sections:
            if i + 1 < len(doc.paragraphs):
                doc.paragraphs[i + 1].text = sections["purpose"]

    # === 2. Table-based filling for teacher/student activities ===
    for table in doc.tables:
        rows = table.rows
        if len(rows) < 2:
            continue
        header_cells = [cell.text.strip() for cell in rows[0].cells]
        for row in rows[1:]:
            row_label = row.cells[0].text.strip()
            for col_idx, col_text in enumerate(header_cells[1:], start=1):
                key = (row_label, col_text.strip())
                if key in ACTIVITY_TABLE_MAPPING:
                    section_key = ACTIVITY_TABLE_MAPPING[key]
                    if section_key in sections:
                        content = sections[section_key]
                        if isinstance(content, list):
                            content = "\n".join(f"• {item}" for item in content)
                        insert_into_cell(row.cells[col_idx], content)

    # Save final docx
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"lesson_plan_filled_{uuid.uuid4().hex}.docx"
    output_path = os.path.join(OUTPUT_DIR, filename)
    doc.save(output_path)

    print(f"✅ Lesson plan saved at: {output_path}")
    return state.update({"final_output_docx": output_path})
