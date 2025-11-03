# graph/lesson_docx_graph.py

from langgraph.graph import StateGraph
from graph.schema import State
from graph.nodes.download_lesson_node import download_lesson_node
from graph.nodes.generate_node import generate_node
from graph.nodes.generate_pptx_node import generate_pptx_node
from graph.nodes.save_node import save_node
from graph.nodes.generate_worksheet_node import generate_worksheet_node
from graph.nodes.generate_reference_text_node import generate_reference_text_node

# Initialize LangGraph with the custom shared State schema
workflow = StateGraph(State)

# Register each node
workflow.add_node("download_lesson_node", download_lesson_node)
workflow.add_node("generate_node", generate_node)
workflow.add_node("generate_pptx_node", generate_pptx_node)
workflow.add_node("generate_worksheet_node", generate_worksheet_node)  # ✅ NEW
workflow.add_node("save_node", save_node)
workflow.add_node("generate_reference_text_node", generate_reference_text_node)  # ✅ NEW

# Define the flow of the pipeline
workflow.set_entry_point("download_lesson_node")
workflow.add_edge("download_lesson_node", "generate_node")
workflow.add_edge("generate_node", "generate_pptx_node")
workflow.add_edge("generate_pptx_node", "generate_worksheet_node")     # ✅ NEW
workflow.add_edge("generate_worksheet_node", "save_node")     
workflow.add_edge("save_node", "generate_reference_text_node")     # ✅ NEW
workflow.set_finish_point("generate_reference_text_node")


# Compile and export the full graph app
lesson_docx_app = workflow.compile()
