# tools/llm/generate_sections.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from graph.schema import State

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read all prompts from the prompts/ directory
def load_prompt(section_name: str) -> str:
    path = f"prompts/{section_name}.txt"
    with open(path, "r") as f:
        return f.read()

# Master list of all 12 sections in order
SECTION_TITLES = [
    "standards", "content", "language", "purpose",
    "intro_teacher", "intro_student",
    "i_do_teacher", "i_do_student",
    "we_do_teacher", "we_do_student",
    "you_do_teacher", "you_do_student"
]

def build_combined_prompt(student_profile, lesson_content, lesson_objective, language_objective, target_language):
    prompt_blocks = []

    for section_key in SECTION_TITLES:
        section_prompt = load_prompt(section_key)

        filled_prompt = section_prompt.format(
            student_profile=student_profile,
            lesson_content=lesson_content,
            lesson_objective=lesson_objective,
            language_objective=language_objective,
            target_language=target_language
        )

        prompt_blocks.append(f"### Section: {section_key.replace('_', ' ').title()}\n{filled_prompt}")

    return "\n\n".join(prompt_blocks)

def generate_all_sections(student_profile, lesson_content, lesson_objective, language_objective, target_language):
    full_prompt = build_combined_prompt(
        student_profile, lesson_content, lesson_objective,
        language_objective, target_language
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert instructional designer generating a rich, inclusive lesson plan across 12 sections. Format responses clearly with section titles."
            },
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        temperature=0.7
    )

    output_text = response.choices[0].message.content

    # Split the LLM response into sections using the headers
    parsed_sections = {}
    current_section = None
    buffer = []

    for line in output_text.splitlines():
        if line.startswith("### Section:"):
            if current_section:
                parsed_sections[current_section] = "\n".join(buffer).strip()
                buffer = []
            current_section = line.replace("### Section:", "").strip().lower().replace(" ", "_")
        elif current_section:
            buffer.append(line)

    # Capture final section
    if current_section and buffer:
        parsed_sections[current_section] = "\n".join(buffer).strip()

    return parsed_sections
