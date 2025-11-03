import os
import json
import re
import ast 
from openai import OpenAI
import traceback
from dotenv import load_dotenv
from tools.llm.generate_sections import load_prompt
import nltk
from nltk.tokenize import sent_tokenize
import math

nltk_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../nltk_data'))
nltk.data.path.append(nltk_data_path)

# Only download if not already available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=nltk_data_path)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def sanitize_text_for_docx(text: str) -> str:
    """Sanitize text for DOCX-safe output (remove danda, smart quotes, etc.)."""
    return (
        text.replace("।", ".")
            .replace("\u0964", ".")
            .replace("\xa0", " ")
            .replace("\r", "")
            .replace("\u2028", " ")
            .replace("\u2029", " ")
            .replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
    )


def split_paragraph_by_sentence_limit(paragraph: str, max_chars: int = 630) -> list[str]:
    """
    Split a paragraph into balanced chunks of roughly equal length (<= max_chars),
    while preserving sentence boundaries.
    """
    sentences = sent_tokenize(paragraph)
    total_chars = sum(len(s) for s in sentences)

    # Estimate number of chunks needed
    est_chunks = max(1, math.ceil(total_chars / max_chars))
    target_chunk_size = total_chars / est_chunks

    chunks = []
    current_chunk = ""
    current_size = 0

    for sentence in sentences:
        if current_chunk and current_size + len(sentence) > target_chunk_size * 1.2:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
            current_size = len(sentence)
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
            current_size += len(sentence)

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def generate_modified_lesson_content(lesson_content, lesson_objective, language_objective, i_do_teacher):
    """Generate slide‑ready modified lesson content aligned with objectives."""
    prompt_template = load_prompt("modify_lesson_content")

    # 🪓 Split long paragraphs in lesson_content before sending to LLM
    processed_paragraphs = []
    for para in lesson_content.split("\n"):
        para = para.strip()
        if not para:
            continue
        if len(para) > 630:
            processed_paragraphs.extend(split_paragraph_by_sentence_limit(para, max_chars=630))
        else:
            processed_paragraphs.append(para)

    # 🧱 Rebuild lesson_content with cleaned paragraphs
    print(processed_paragraphs)
    lesson_content_split = "\n\n".join(processed_paragraphs)

    # 🧠 Prompt with updated content
    filled_prompt = prompt_template.format(
        lesson_content=lesson_content_split,
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        i_do_teacher=i_do_teacher
    )

    # 🧠 LLM Call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a curriculum adaptation expert generating slide-ready rewritten lesson content. "
                    "Return only valid JSON with 'title' and 'content'. Do NOT include markdown or triple backticks."
                )
            },
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    # ---------- Basic parsing ----------
    try:
        parsed = json.loads(raw_output)
    except Exception:
        cleaned = raw_output.strip()

        # Remove Markdown fences
        cleaned = re.sub(r"^```(json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()

        # Replace smart quotes / unsafe chars
        cleaned = sanitize_text_for_docx(cleaned)

        # ✅ Escape unescaped internal quotes in content
        def escape_inner_quotes(match):
            inner = match.group(1)
            # escape only double quotes that are not already escaped
            inner_escaped = re.sub(r'(?<!\\)"', r'\\"', inner)
            return f'"content": "{inner_escaped}"'

        cleaned = re.sub(r'"content":\s*"([^"]*?)"', escape_inner_quotes, cleaned, flags=re.DOTALL)

        # ---------- Try parsing again ----------
        try:
            parsed = json.loads(cleaned)
        except Exception:
            try:
                parsed = ast.literal_eval(cleaned)
            except Exception as e:
                print("\n❌ Parsing failed. Output preview:\n", cleaned[:1000])
                print("\n🚨 Traceback:\n", traceback.format_exc())
                raise e

    # ---------- Final cleanup ----------
    sanitized_slides = []
    for slide in parsed:
        sanitized_slides.append({
            "title": sanitize_text_for_docx(slide.get("title", "")),
            "content": sanitize_text_for_docx(slide.get("content", "")),
        })

    print(f"✅ Modified Lesson Slides Generated: {len(sanitized_slides)}")
    return sanitized_slides, processed_paragraphs
    
# ------------------------------------------------------------
# SECOND LLM CALL → Generate Main Lesson Slide Structure
# ------------------------------------------------------------
def generate_base_slide_structure(lesson_objective, language_objective, lesson_content, intro_teacher, we_do_teacher):
    """
    Step 2: Generate the core slide structure (title, engager, I DO, WE DO, etc.)
    without including the modified lesson slides.
    """
    prompt_template = load_prompt("slide_deck")  # New prompt file (see below)
    filled_prompt = prompt_template.format(
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        lesson_content=lesson_content,
        intro_teacher=intro_teacher,
        we_do_teacher=we_do_teacher
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert instructional designer. Return only valid JSON with 'title' and 'content'. No markdown or extra text."
            },
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        base_slides = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()

        cleaned = cleaned.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

        print("\n🧹 Cleaned base slide structure:")
        print(cleaned)

        base_slides = json.loads(cleaned)

    print(f"✅ Base Slide Structure Generated: {len(base_slides)}")
    return base_slides


# ------------------------------------------------------------
# FINAL COMBINED FUNCTION → Merge Slides
# ------------------------------------------------------------
def generate_slide_content(lesson_objective, language_objective, lesson_content, intro_teacher, i_do_teacher, we_do_teacher):
    """
    Full pipeline:
      1️⃣ Generate modified lesson slides (LLM #1)
      2️⃣ Generate base slide structure (LLM #2)
      3️⃣ Insert modified slides right after 'I DO – Teacher Modeling'
    """
    # Step 1: Modified lesson slides
    modified_slides, processed_paragraphs = generate_modified_lesson_content(
        lesson_content=lesson_content,
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        i_do_teacher=i_do_teacher
    )

    # Step 2: Main structure slides
    base_slides = generate_base_slide_structure(
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        lesson_content=lesson_content,
        intro_teacher=intro_teacher,
        we_do_teacher=we_do_teacher
    )

    # Step 3: Find index of “I DO – Teacher Modeling” slide
    insert_index = next(
        (i for i, slide in enumerate(base_slides) if "i do" in slide["title"].lower()),
        3  # default after 3rd slide
    )

    # Step 4: Merge
    final_slides = base_slides[:insert_index + 1] + modified_slides + base_slides[insert_index + 1:]

    print(f"✅ Final Slide Deck Generated: {len(final_slides)} slides total")
    return final_slides, processed_paragraphs
