from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os
import uuid

# Helper to add formatted text into a placeholder with colors
def _set_formatted_content(text_frame, content):
    text_frame.clear()

    for paragraph_text in content.split("\n"):
        if not paragraph_text.strip():
            continue

        p = text_frame.add_paragraph()
        run = p.add_run()

        # Detect translation vs English
        if "Translation" in paragraph_text or "Translation" in paragraph_text.lower() or "अनुवाद" in paragraph_text:
            run.text = paragraph_text.strip()
            run.font.color.rgb = RGBColor(255, 0, 0)  # Red for translation
        else:
            run.text = paragraph_text.strip()
            run.font.color.rgb = RGBColor(0, 102, 204)  # Blue for English

        run.font.size = Pt(16)
        run.font.name = "Poppins"
        p.alignment = PP_ALIGN.LEFT

# Title + Content Slide
def _add_title_content_slide(prs, title, content):
    slide_layout = prs.slide_layouts[1]  # Title + Content
    slide = prs.slides.add_slide(slide_layout)

    title_placeholder = slide.shapes.title
    content_placeholder = slide.placeholders[1]

    # Set title
    title_placeholder.text = title
    for p in title_placeholder.text_frame.paragraphs:
        for run in p.runs:
            run.font.name = "Poppins"
            run.font.bold = True
            run.font.size = Pt(22)

    # Set content with colors
    _set_formatted_content(content_placeholder.text_frame, content)

# Title Only (Centered)
def _add_title_only_slide(prs, title):
    slide_layout = prs.slide_layouts[5]  # Title Only
    slide = prs.slides.add_slide(slide_layout)

    title_placeholder = slide.shapes.title
    title_placeholder.text = title

    for p in title_placeholder.text_frame.paragraphs:
        for run in p.runs:
            run.font.name = "Poppins"
            run.font.bold = True
            run.font.size = Pt(22)
        p.alignment = PP_ALIGN.CENTER

# Content Only (No Title)
def _add_content_only_slide(prs, content):
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)

    left = Inches(0.75)
    top = Inches(1)
    width = Inches(8.5)
    height = Inches(5.5)

    textbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = textbox.text_frame

    _set_formatted_content(text_frame, content)

# Master generator
def generate_slide_deck(slides: list) -> str:
    prs = Presentation()

    for slide in slides:
        title = slide.get("title", "").strip()
        content = slide.get("content", "").strip()

        if not content:
            _add_title_only_slide(prs, title)
        elif not title:
            _add_content_only_slide(prs, content)
        elif title.lower() in ["i do", "we do"]:
            _add_title_only_slide(prs, title)
        else:
            _add_title_content_slide(prs, title, content)

    save_dir = "data/outputs/slides"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"lesson_slides_{uuid.uuid4().hex}.pptx"
    path = os.path.join(save_dir, filename)
    prs.save(path)
    return path
