from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
import os
import re
import uuid

# Helper to add formatted text into a placeholder with colors
def _set_formatted_content(text_frame, content, center=False):
    text_frame.clear()
    text_frame.word_wrap = True
    if center:
        text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE  # Vertically center content

    # --- Detect translation ---
    if "\n\n" in content:
        english_part, translation_part = content.split("\n\n", 1)
    else:
        match = re.search(r'[\u0900-\u097F]', content)
        if match:
            split_index = match.start()
            english_part = content[:split_index].rstrip()
            translation_part = content[split_index:].lstrip()
        else:
            english_part = content.strip()
            translation_part = ""

    # --- English Content ---
    for paragraph_text in english_part.split("\n"):
        clean_text = paragraph_text.strip()
        if not clean_text:
            continue
        p = text_frame.add_paragraph()
        p.alignment = PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
        run = p.add_run()
        run.text = clean_text
        run.font.size = Pt(16)
        run.font.name = "Poppins"
        run.font.color.rgb = RGBColor(0, 102, 204)  # 🔵 Blue

    # Spacer
    if translation_part:
        spacer = text_frame.add_paragraph()
        spacer.text = ""

    # --- Translation Content ---
    for paragraph_text in translation_part.split("\n"):
        clean_text = paragraph_text.strip()
        if not clean_text:
            continue
        p = text_frame.add_paragraph()
        p.alignment = PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
        run = p.add_run()
        run.text = clean_text
        run.font.size = Pt(16)
        run.font.name = "Poppins"
        run.font.color.rgb = RGBColor(255, 0, 0)  # 🔴 Red

# Title + Content Slide with adjusted sizes
def _add_title_content_slide(prs, title, content):
    slide_layout = prs.slide_layouts[6]  # Use blank layout for custom positioning
    slide = prs.slides.add_slide(slide_layout)

    # Add title textbox (smaller height)
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.name = "Poppins"
    run.font.bold = True
    run.font.size = Pt(22)
    p.alignment = PP_ALIGN.LEFT

    # Add content textbox (larger height)
    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(5.5))
    text_frame = content_box.text_frame
    text_frame.word_wrap = True
    _set_formatted_content(text_frame, content)

# Title Only Slide — title centered on screen, large size
def _add_title_only_slide(prs, title):
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)

    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(2))
    title_frame = title_box.text_frame
    title_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    p = title_frame.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.name = "Poppins"
    run.font.bold = True
    run.font.size = Pt(36)
    p.alignment = PP_ALIGN.CENTER

# Content Only Slide — content centered both ways
def _add_content_only_slide(prs, content):
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)

    textbox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(5.5))
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    _set_formatted_content(text_frame, content, center=True)

# Main slide generator
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
