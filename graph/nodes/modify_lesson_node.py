# graph/nodes/modify_lesson_node.py

from tools.llm.modify import modify_lesson_content, modify_lesson_content_worksheet

def split_text_into_chunks(text: str, n: int) -> list:
    """
    Splits text into n chunks by paragraph, keeping boundaries clean.
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    total = len(paragraphs)
    chunk_size = total // n
    remainder = total % n

    chunks = []
    start = 0
    for i in range(n):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append("\n\n".join(paragraphs[start:end]))
        start = end
    return chunks

def modify_lesson_node(state: dict) -> dict:
    """
    Applies adaptation rules to the lesson content using GPT-4o.
    Splits content by number of days only for 'Lesson' category.
    - Lesson: split into days with ### Day N headers.
    - Worksheet: apply full content at once without splitting.
    """
    rules = state.get("rules")
    lesson_content = state.get("lesson_content")
    file_category = state.get("file_category", "Lesson")
    number_of_days = state.get("number_of_days", 1)

    if not rules:
        raise ValueError("Missing 'rules' in state.")
    if not lesson_content:
        raise ValueError("Missing 'lesson_content' in state.")

    try:
        if file_category.lower() == "worksheet":
            # No chunking — apply full worksheet adaptation
            modified = modify_lesson_content_worksheet(lesson_content, rules)
            final_text = modified.strip()

        else:
            # For 'Lesson', split into N days and adapt each
            chunks = split_text_into_chunks(lesson_content, number_of_days)
            modified_sections = []

            for i, chunk in enumerate(chunks):
                modified = modify_lesson_content(chunk, rules)
                modified_sections.append(f"### Day {i + 1}\n\n{modified.strip()}")

            final_text = "\n\n".join(modified_sections)

    except Exception as e:
        raise RuntimeError(f"Failed to modify lesson: {str(e)}")

    state.update({"modified_lesson_text": final_text})
    return state