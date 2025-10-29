import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from tools.llm.generate_sections import load_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------
# FIRST LLM CALL → Generate Modified Lesson Content Slides
# ------------------------------------------------------------
def generate_modified_lesson_content(lesson_content, lesson_objective, language_objective, i_do_teacher):
    """
    Step 1: Rewrite the lesson content into slide-ready instructional chunks
    that align with lesson & language objectives and include translations if required.
    """
    prompt_template = load_prompt("modify_lesson_content")
    filled_prompt = prompt_template.format(
        lesson_content=lesson_content,
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        i_do_teacher=i_do_teacher
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a curriculum adaptation expert generating slide-ready rewritten lesson content. Return only valid JSON with 'title' and 'content'."
            },
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        # Try parsing directly first
        return json.loads(raw_output)

    except json.JSONDecodeError:
        # Cleaning starts here
        cleaned = raw_output

        # Remove triple backticks if present
        if cleaned.startswith("```json") or cleaned.startswith("```"):
            cleaned = re.sub(r"^```json|```$", "", cleaned).strip()

        # Replace smart quotes and normalize line breaks
        cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = cleaned.replace("\\n", "\n").replace("\r", "")
        cleaned = cleaned.replace('\xa0', ' ')  # Remove non-breaking spaces

        # Escape unescaped inner quotes likely causing parsing failure
        cleaned = re.sub(r'(?<!\\)"(?=[^:]*?\n)', r'\"', cleaned)

        # Final fallback: try ast.literal_eval
        try:
            modified_slides = json.loads(cleaned)
        except json.JSONDecodeError:
            try:
                modified_slides = ast.literal_eval(cleaned)
            except Exception as e:
                print("\n❌ Final fallback failed. Output below:\n")
                print(cleaned)
                raise e

        print("\n🧹 Cleaned modified lesson content:")
        print(cleaned)

        print(f"✅ Modified Lesson Slides Generated: {len(modified_slides)}")
        return modified_slides


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
    modified_slides = generate_modified_lesson_content(
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
    return final_slides
