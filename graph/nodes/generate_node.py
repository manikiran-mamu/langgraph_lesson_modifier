# graph/nodes/generate_node.py

from graph.schema import State
from tools.llm.generate_sections import generate_sections

def generate_node(state: State) -> State:
    if not state.student_profile:
        raise ValueError("Missing student profile.")
    if not state.lesson_content:
        raise ValueError("Missing lesson content.")

    lesson_objective = state.lesson_objective
    language_objective = state.language_objective
    target_language = state.target_language

    sections = generate_all_sections(
        student_profile=state.student_profile,
        lesson_content=state.lesson_content,
        lesson_objective=lesson_objective,
        language_objective=language_objective,
        target_language=target_language
    )

    return state.update({"sections": sections})
