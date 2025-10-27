import os
import uuid
from pptx import Presentation  # ✅ Required for generating slides

def generate_slide_deck(slides: list) -> str:
    prs = Presentation()
    for slide in slides:
        if slide["title"].lower() in ["i do", "we do"]:
            _add_center_text_slide(prs, slide["title"])
        else:
            _add_content_slide(prs, slide["title"], slide["content"])

    save_dir = "data/outputs/slides"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"lesson_slides_{uuid.uuid4().hex}.pptx"
    path = os.path.join(save_dir, filename)
    prs.save(path)
    return path
