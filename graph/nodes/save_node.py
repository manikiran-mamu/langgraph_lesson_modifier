# graph/nodes/save_node.py

from langchain_core.runnables import Runnable
from graph.schema import State
from docx import Document
import os
import uuid

class SaveNode(Runnable):
    def invoke(self, state: State) -> State:
        print("📝 Saving Word document...")

        # Extract modified text from state
        text = state.get("modified_lesson_text")
        if not text:
            raise ValueError("No modified lesson text found in state.")

        # Create Word document
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)

        # Save to file
        filename = f"lesson_plan_{uuid.uuid4().hex}.docx"
        save_dir = "data/outputs/word"
        os.makedirs(save_dir, exist_ok=True)
        output_path = os.path.join(save_dir, filename)
        doc.save(output_path)

        # Update state
        return state.update({
            "final_output_docx": output_path
        })

save_node = SaveNode()
