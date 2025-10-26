# graph/nodes/generate_node.py

from langchain_core.runnables import Runnable
from graph.schema import State
from tools.llm.generate_sections import generate_all_sections

class GenerateNode(Runnable):
    def invoke(self, state: State) -> State:
        if not state.student_profile:
            raise ValueError("Missing student profile.")
        if not state.lesson_content:
            raise ValueError("Missing lesson content.")

        lesson_objective = state.student_profile.get("Lesson Objective", "")
        language_objective = state.student_profile.get("Language Objective", {})
        target_language = state.student_profile.get("Target Language", "English")

        sections = generate_all_sections(
            student_profile=state.student_profile,
            lesson_content=state.lesson_content,
            lesson_objective=lesson_objective,
            language_objective=language_objective,
            target_language=target_language
        )

        return state.update({"sections": sections})

generate_node = GenerateNode()
