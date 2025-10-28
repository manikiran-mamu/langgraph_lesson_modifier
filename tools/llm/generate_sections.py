import os
from openai import OpenAI
from dotenv import load_dotenv
from graph.schema import State

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Load individual prompt templates
# -----------------------------
def load_prompt(section_name: str) -> str:
    path = f"prompts/{section_name}.txt"
    with open(path, "r") as f:
        return f.read()

# -----------------------------
# Section groupings
# -----------------------------
TEACHER_SECTIONS = [
    "standards", "content", "language", "purpose",
    "intro_teacher", "i_do_teacher", "we_do_teacher", "you_do_teacher"
]

STUDENT_SECTIONS = [
    "intro_student", "i_do_student", "we_do_student", "you_do_student"
]

# -----------------------------
# Extract key fields from profile
# -----------------------------
def extract_profile_fields(profile: dict) -> dict:
    return {
        "related_services": profile.get("Related Services", "N/A"),
        "disability_category": profile.get("Disability Category/Classification", "N/A"),
        "mobility_needs": profile.get("Mobility Needs", "N/A"),
        "health_needs": profile.get("Health & Physical Needs", "N/A"),
        "management_needs": profile.get("Management Needs", "N/A"),
        "peer_participation": profile.get("Participation with Peers", "N/A"),
        "grade_level": profile.get("English Language Literacy Grade Level", "N/A"),
        "student_interests": profile.get("Student Interests", "N/A"),
        "dominant_language": profile.get("Dominant Language", "N/A")
    }

# -----------------------------
# Helper: Build prompt dynamically
# -----------------------------
def build_combined_prompt(section_list, student_profile, lesson_content, lesson_objective, language_objective, target_language, prior_sections=None):
    prompt_blocks = []
    extracted = extract_profile_fields(student_profile)
    prior_sections = prior_sections or {}

    for section_key in section_list:
        section_prompt = load_prompt(section_key)

        # Fill prompt placeholders
        filled_prompt = section_prompt.format(
            student_profile=student_profile,
            lesson_content=lesson_content,
            lesson_objective=lesson_objective,
            language_objective=language_objective,
            target_language=target_language,
            related_services=extracted["related_services"],
            disability_category=extracted["disability_category"],
            mobility_needs=extracted["mobility_needs"],
            health_needs=extracted["health_needs"],
            management_needs=extracted["management_needs"],
            peer_participation=extracted["peer_participation"],
            grade_level=extracted["grade_level"],
            student_interests=extracted["student_interests"],
            dominant_language=extracted["dominant_language"],
            intro_teacher=prior_sections.get("intro_teacher", ""),
            i_do_teacher=prior_sections.get("i_do_teacher", ""),
            we_do_teacher=prior_sections.get("we_do_teacher", ""),
            you_do_teacher=prior_sections.get("you_do_teacher", "")
        )

        prompt_blocks.append(f"### Section: {section_key.replace('_', ' ').title()}\n{filled_prompt}")

    return "\n\n".join(prompt_blocks)

# -----------------------------
# Helper: Parse response into dict by section
# -----------------------------
def parse_sections(output_text):
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

    if current_section and buffer:
        parsed_sections[current_section] = "\n".join(buffer).strip()

    return parsed_sections

# -----------------------------
# MAIN FUNCTION: Two LLM calls
# -----------------------------
def generate_all_sections(student_profile, lesson_content, lesson_objective, language_objective, target_language):
    # --- FIRST CALL: Generate teacher sections ---
    teacher_prompt = build_combined_prompt(
        TEACHER_SECTIONS, student_profile, lesson_content, lesson_objective, language_objective, target_language
    )

    teacher_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert instructional designer generating teacher-facing lesson sections clearly titled with '### Section:'."
            },
            {
                "role": "user",
                "content": teacher_prompt
            }
        ],
        temperature=0.7
    )

    teacher_output = teacher_response.choices[0].message.content
    teacher_sections = parse_sections(teacher_output)
    print("teacher_sections:", teacher_sections)

    # --- SECOND CALL: Generate student sections using teacher output ---
    student_prompt = build_combined_prompt(
        STUDENT_SECTIONS, student_profile, lesson_content, lesson_objective, language_objective, target_language,
        prior_sections=teacher_sections
    )
    print("student_prompt:", student_prompt)

    student_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert instructional designer generating student-facing lesson sections clearly titled with '### Section:'."
            },
            {
                "role": "user",
                "content": student_prompt
            }
        ],
        temperature=0.7
    )

    student_output = student_response.choices[0].message.content
    student_sections = parse_sections(student_output)

    # Combine all sections
    all_sections = {**teacher_sections, **student_sections}
    print("Student_sections:", student_sections)
    return all_sections
