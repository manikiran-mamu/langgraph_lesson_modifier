# graph/nodes/generate_pptx_node.py

from graph.schema import State
from tools.output.generate_pptx import generate_slide_deck

def generate_pptx_node(state: State) -> State:
    sections = state.get("sections")
    lesson_objective = state.get("lesson_objective", "")
    language_objective = state.get("language_objective", "")

    if not sections:
        raise ValueError("Missing 'sections' in state.")
    
    slide_path = generate_slide_deck(sections, lesson_objective, language_objective)
    print(f"📊 Slides saved at: {slide_path}")

    return state.update({"final_output_pptx": slide_path})
