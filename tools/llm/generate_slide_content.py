#tools/llm/generate_slide_content.py
from tools.llm.generate_sections import load_prompt
import json

def generate_slide_content(lesson_objective, language_objective, lesson_content, intro_teacher, i_do_teacher, we_do_teacher):
    prompt_template = load_prompt("slide_deck")
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
            {"role": "system", "content": "You are an expert instructional designer returning a JSON list of slides with title and content."},
            {"role": "user", "content": filled_prompt}
        ],
        temperature=0.7
    )

    print(response)
    return eval(response.choices[0].message.content)  # or use json.loads() if valid JSON
