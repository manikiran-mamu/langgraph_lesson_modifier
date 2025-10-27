import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.llm.generate_sections import load_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_student_worksheet_sections(intro_student, i_do_student, we_do_student, you_do_student, lesson_content):
    prompt_template = load_prompt("student_worksheet")
    filled_prompt = prompt_template.format(
        intro_student=intro_student,
        i_do_student=i_do_student,
        we_do_student=we_do_student,
        you_do_student=you_do_student,
        lesson_content=lesson_content
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert instructional designer. Return only a valid JSON list of worksheet sections. No markdown or backticks."},
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        sections = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'").strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        sections = json.loads(cleaned)

    return sections
