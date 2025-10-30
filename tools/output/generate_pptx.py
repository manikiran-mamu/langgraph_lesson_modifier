from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os
import uuid

# Helper to add formatted text into a placeholder with colors
def _set_formatted_content(text_frame, content):
    text_frame.clear()
    text_frame.word_wrap = True

    # Step 1: Detect split between English and translation
    parts = content.split("\n\n", 1)
    english_part = parts[0].strip()
    translation_part = parts[1].strip() if len(parts) > 1 else ""

    # Step 2: Add English content
    for paragraph_text in english_part.split("\n"):
        clean_text = paragraph_text.strip()
        if not clean_text:
            continue

        p = text_frame.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = clean_text
        run.font.size = Pt(16)
        run.font.name = "Poppins"
        run.font.color.rgb = RGBColor(0, 102, 204)  # 🔵 Blue

    # Step 3: Add spacing paragraph
    if translation_part:
        spacer = text_frame.add_paragraph()
        spacer.text = ""  # Leave empty for visible gap

    # Step 4: Add Translation content
    for paragraph_text in translation_part.split("\n"):
        clean_text = paragraph_text.strip()
        if not clean_text:
            continue

        p = text_frame.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = clean_text
        run.font.size = Pt(16)
        run.font.name = "Poppins"
        run.font.color.rgb = RGBColor(255, 0, 0)  # 🔴 Red

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

    # Set dimensions and position
    left = Inches(0.5)
    top = Inches(0.5)
    width = Inches(9)   # Slightly narrower to allow padding
    height = Inches(6.5)

    textbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = textbox.text_frame
    text_frame.word_wrap = True  # ✅ Enable word wrap

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
