rate# graph/lesson_docx_graph.py

from langgraph.graph import StateGraph
from graph.schema import State
from graph.nodes.download_lesson_node import download_lesson_node
from graph.nodes.generate_node import generate_node
from graph.nodes.save_node import save_node

# Build the graph for docx generation
workflow = StateGraph(State)

workflow.add_node("download_lesson_node", download_lesson_node)
workflow.add_node("generate_node", generate_node)
workflow.add_node("save_node", save_node)

# Define flow
workflow.set_entry_point("download_lesson_node")
workflow.add_edge("download_lesson_node", "generate_node")
workflow.add_edge("generate_node", "save_node")
workflow.set_finish_point("save_node")

# Compile app
lesson_docx_app = workflow.compile()
