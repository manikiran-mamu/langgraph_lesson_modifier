# graph/nodes/save_node.py

from graph.schema import State
from docx import Document
from docx.shared import Pt
import os
import uuid

def save_node(state: State) -> State:
    """
    Saves the generated lesson plan sections into a formatted Word document.
    """
    print("📝 Saving Word document...")

    sections = state.get("sections")
    if not sections:
        raise ValueError("No 'sections' data found in state. Did generate_node run correctly?")

    # Create document
    doc = Document()

    # Set font style
    style = doc.styles['Normal']
    style.font.name = 'Poppins'
    style.font.size = Pt(12)

    # Add title
    doc.add_heading("Lesson Plan", level=1)

    # Loop through sections (each key = section title, value = text)
    for title, content in sections.items():
        doc.add_heading(title.replace("_", " ").title(), level=2)
        
        # Handle content type (list vs string)
        if isinstance(content, list):
            for item in content:
                doc.add_paragraph(f"• {item}")
        elif isinstance(content, str):
            # Split by newline for clean paragraphs
            for para in content.split("\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())
        else:
            doc.add_paragraph(str(content))

        # Add spacing between sections
        doc.add_paragraph("")

    # Save file
    save_dir = "data/outputs/word"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"lesson_plan_{uuid.uuid4().hex}.docx"
    output_path = os.path.join(save_dir, filename)
    doc.save(output_path)

    print(f"✅ Lesson plan saved at: {output_path}")

    # Update state
    return state.update({"final_output_docx": output_path})
