from tools.output.generate import generate_final_output

def final_output_node(state: dict) -> dict:
    """
    Creates the final output files (.txt, .json, .md) with just placeholders.
    No audio/image assets are resolved – the output remains editable for user.
    """
    lesson_text = state.get("modified_lesson_text", "")

    if not lesson_text:
        raise ValueError("Missing modified_lesson_text in state.")

    result = generate_final_output(lesson_text)

    state.update({
        "final_output_path": result["txt_path"],
        "final_output_json": result["json_path"],
        "final_output_md": result["md_path"]
    })

    return state