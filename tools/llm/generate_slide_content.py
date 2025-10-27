#tools/llm/generate_slide_content.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.llm.generate_sections import load_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_slide_content(lesson_objective, language_objective, lesson_content, intro_teacher, i_do_teacher, we_do_teacher):
    prompt_template = load_prompt("slide_deck")
    print(prompt_template)
    filled_prompt = prompt_template.format(
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        lesson_content=lesson_content,
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
    print("🔵 Raw LLM Output:")
    print(raw_output)
    # ✅ Try parsing JSON safely
        # Try parsing raw_output directly
    try:
        # Try parsing raw_output directly
        slides = json.loads(raw_output)
    except json.JSONDecodeError:
        # Clean triple backticks and fancy quotes
        cleaned = raw_output.strip()

        # Handle markdown formatting
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()

        # Replace fancy quotes
        cleaned = cleaned.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

        print("🧹 Cleaned fallback content:")
        print(cleaned)

        slides = json.loads(cleaned)
