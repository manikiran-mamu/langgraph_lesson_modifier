from graph.schema import State
from tools.llm.generate_student_worksheet import generate_student_worksheet_sections
from tools.output.generate_worksheet import generate_student_worksheet_doc

def generate_worksheet_node(state: State) -> State:
    sections = state.sections
    worksheet_sections = generate_student_worksheet_sections(
        intro_student=sections.get("intro_student", ""),
        i_do_student=sections.get("i_do_student", ""),
        we_do_student=sections.get("we_do_student", ""),
        you_do_student=sections.get("you_do_student", ""),
        lesson_content=state.lesson_content
    )
    worksheet_path = generate_student_worksheet_doc(worksheet_sections)
    return state.update({"student_worksheet_path": worksheet_path})
