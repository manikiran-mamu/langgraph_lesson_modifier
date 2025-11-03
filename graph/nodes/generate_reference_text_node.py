from tools.output.save_source_material import save_source_material_doc
from graph.schema import State


def generate_reference_text_node(state: State) -> State:
    """
    Generates a formatted Word document containing the processed lesson paragraphs.
    Saves the document and updates the state with its path.
    """
    source_path = save_source_material_doc(state.get("processed_paragraphs", []))
    return state.update({"source_material_path": source_path})