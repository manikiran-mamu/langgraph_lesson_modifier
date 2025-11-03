import os
import json
import re
import ast
import math
import traceback
from openai import OpenAI
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize
from tools.llm.generate_sections import load_prompt

# -------------------- NLTK SETUP --------------------
nltk_data_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../nltk_data')
)
nltk.data.path.append(nltk_data_path)

# -------------------- ENV + OPENAI --------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------- TEXT UTILITIES --------------------
def sanitize_text(text: str) -> str:
    """Clean text for DOCX compatibility."""
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

def split_paragraph(paragraph: str, max_chars: int = 630) -> list[str]:
    """Split long paragraphs into sentence-aligned chunks."""
    sentences = sent_tokenize(paragraph)
    total_chars = sum(len(s) for s in sentences)
    target_chunk = total_chars / max(1, math.ceil(total_chars / max_chars))

    chunks, buffer, size = [], "", 0
    for sentence in sentences:
        if buffer and size + len(sentence) > target_chunk * 1.2:
            chunks.append(buffer.strip())
            buffer, size = sentence, len(sentence)
        else:
            buffer += (" " if buffer else "") + sentence
            size += len(sentence)

    if buffer:
        chunks.append(buffer.strip())
    return chunks

def parse_json_response(raw: str):
    """Handle OpenAI LLM output with JSON fallback and sanitization."""
    try:
        return json.loads(raw)
    except Exception:
        raw = re.sub(r"^```(json)?", "", raw).replace("```", "").strip()
        raw = sanitize_text(raw)

        def escape_quotes(match):
            inner = match.group(1)
            escaped = re.sub(r'(?<!\\)"', r'\\"', inner)
            return f'"content": "{escaped}"'

        raw = re.sub(r'"content":\s*"([^"]*?)"', escape_quotes, raw, flags=re.DOTALL)

        try:
            return json.loads(raw)
        except Exception:
            return ast.literal_eval(raw)

# -------------------- SLIDE GENERATION --------------------

def generate_modified_lesson_content(lesson_content, lesson_objective, language_objective, i_do_teacher):
    prompt_template = load_prompt("modify_lesson_content")

    processed_paragraphs = []
    for para in lesson_content.split("\n"):
        para = para.strip()
        if para:
            processed_paragraphs.extend(
                split_paragraph(para) if len(para) > 630 else [para]
            )

    prompt = prompt_template.format(
        lesson_content="\n\n".join(processed_paragraphs),
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        i_do_teacher=i_do_teacher
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a curriculum adaptation expert..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    parsed = parse_json_response(response.choices[0].message.content.strip())
    slides = [{"title": sanitize_text(s.get("title", "")), "content": sanitize_text(s.get("content", ""))} for s in parsed]

    return slides, processed_paragraphs

def generate_base_slide_structure(lesson_objective, language_objective, lesson_content, intro_teacher, we_do_teacher):
    prompt_template = load_prompt("slide_deck")
    prompt = prompt_template.format(
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        lesson_content=lesson_content,
        intro_teacher=intro_teacher,
        we_do_teacher=we_do_teacher
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert instructional designer..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return parse_json_response(response.choices[0].message.content.strip())

def generate_slide_content(lesson_objective, language_objective, lesson_content, intro_teacher, i_do_teacher, we_do_teacher):
    """
    Pipeline to:
    1. Generate rewritten slide content from lesson text.
    2. Generate base slide structure (title, intro, objectives).
    3. Merge modified slides after "I DO – Teacher Modeling".
    """
    modified_slides, processed_paragraphs = generate_modified_lesson_content(
        lesson_content, lesson_objective, language_objective, i_do_teacher
    )

    base_slides = generate_base_slide_structure(
        lesson_objective, language_objective, lesson_content, intro_teacher, we_do_teacher
    )

    insert_index = next(
        (i for i, s in enumerate(base_slides) if "i do" in s.get("title", "").lower()),
        3
    )

    final_slides = (
        base_slides[:insert_index + 1] + modified_slides + base_slides[insert_index + 1:]
    )

    return final_slides, processed_paragraphs