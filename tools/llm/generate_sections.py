import os
from openai import OpenAI
from dotenv import load_dotenv
from graph.schema import State

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read all prompts from the prompts/ directory
def load_prompt(section_name: str) -> str:
    print("i am here")
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

# Extract values from student_profile dict for prompts requiring individual fields
def extract_profile_fields(profile: dict) -> dict:
    return {
        "related_services": profile.get("Related_Services", "N/A"),
        "disability_category": profile.get("Disability_Category", "N/A"),
        "mobility_needs": profile.get("Mobility_Needs", "N/A"),
        "health_needs": profile.get("Health_&_Physical_Needs", "N/A"),
        "management_needs": profile.get("Management_Needs", "N/A"),
        "peer_participation": profile.get("Participation_with_Peers", "N/A"),
        "grade_level": profile.get("English_Language_Literacy_Grade_Level", "N/A"),
        "student_interests": profile.get("Student_Interests", "N/A"),
    }

def build_combined_prompt(student_profile, lesson_content, lesson_objective, language_objective, target_language, prior_sections=None):
    prompt_blocks = []
    extracted = extract_profile_fields(student_profile)
    prior_sections = prior_sections or {}

    for section_key in SECTION_TITLES:
        section_prompt = load_prompt(section_key)

        # Dynamically determine inputs based on section
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
            intro_teacher=prior_sections.get("intro_teacher", ""),
            we_do_teacher=prior_sections.get("we_do_teacher", ""),
            you_do_teacher=prior_sections.get("you_do_teacher", "")
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

    if current_section and buffer:
        parsed_sections[current_section] = "\n".join(buffer).strip()

    return parsed_sections
