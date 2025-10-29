# tools/llm/generate_slide_content.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.llm.generate_sections import load_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_modified_lesson_content(lesson_content, lesson_objective, language_objective, i_do_teacher):
    """Call GPT to rewrite the lesson content into scaffolded instructional chunks for slide use."""
    prompt_template = load_prompt("modify_lesson_content")  # This should be your detailed prompt file
    filled_prompt = prompt_template.format(
        lesson_content=lesson_content,
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        i_do_teacher=i_do_teacher
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a curriculum adaptation expert generating slide-ready rewritten lesson content. Return only valid JSON."},
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        modified_chunks = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip()

        # Remove markdown formatting
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()

        cleaned = cleaned.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

        print("🧹 Cleaned modified lesson content:")
        print(cleaned)

        modified_chunks = json.loads(cleaned)

    return modified_chunks


def generate_slide_content(lesson_objective, language_objective, lesson_content, intro_teacher, i_do_teacher, we_do_teacher):
    # Step 1: Preprocess lesson_content via LLM
    modified_chunks = generate_modified_lesson_content(
        lesson_content=lesson_content,
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        i_do_teacher=i_do_teacher
    )

    # Optional: flatten modified content into a single string if your slide prompt expects one string
    modified_lesson_content = "\n\n".join(chunk["content"] for chunk in modified_chunks)

    # Step 2: Generate slides using the modified content
    prompt_template = load_prompt("slide_deck")
    filled_prompt = prompt_template.format(
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        lesson_content=modified_lesson_content,
        intro_teacher=intro_teacher,
        i_do_teacher=i_do_teacher,
        we_do_teacher=we_do_teacher
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert instructional designer. Return only a valid JSON list of slides. Do not use markdown or triple backticks. No explanation — just plain JSON."},
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        slides = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()

        cleaned = cleaned.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

        print("🧹 Cleaned fallback slide content:")
        print(cleaned)

        slides = json.loads(cleaned)

    print("✅ Generated Slides:", slides)
    return slides
