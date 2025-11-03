# graph/nodes/generate_pptx_node.py

from graph.schema import State
from tools.llm.generate_slide_content import generate_slide_content
from tools.output.generate_pptx import generate_slide_deck

def generate_pptx_node(state: State) -> State:
    lesson_obj = state.lesson_objective
    lang_obj = state.language_objective
    content = state.lesson_content
    sections = state.sections

    slides, processed_paragraphs = generate_slide_content(
        lesson_objective=lesson_obj,
        language_objective=lang_obj,
        lesson_content=content,
        intro_teacher=sections.get("intro_teacher", ""),
        i_do_teacher=sections.get("i_do_teacher", ""),
        we_do_teacher=sections.get("we_do_teacher", "")
    )

    pptx_path = generate_slide_deck(slides)
    return state.update({
        "final_output_pptx": pptx_path,
        "slide_data": slides,  # ✅ storing slide list in state
        "processed_paragraphs": processed_paragraphs  # ✅ storing processed paragraphs in state
    })
