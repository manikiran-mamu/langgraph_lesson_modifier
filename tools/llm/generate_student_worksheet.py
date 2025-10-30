import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.llm.generate_sections import load_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_student_worksheet_sections(
    intro_student,
    i_do_student,
    we_do_student,
    you_do_student,
    lesson_content,
    slides: list[dict] = None
):
    prompt_template = load_prompt("student_worksheet")

    # Insert raw slides JSON (not as a string)
    slides_json_str = json.dumps(slides, indent=2) if slides else "[]"

    filled_prompt = prompt_template.format(
        intro_student=intro_student,
        i_do_student=i_do_student,
        we_do_student=we_do_student,
        you_do_student=you_do_student,
        lesson_content=lesson_content,
        slides=slides_json_str  # ⬅️ Actual JSON list of dicts
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert instructional designer. Use all content below to generate worksheet sections. Return only a valid JSON list. No markdown or backticks."},
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'").strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
