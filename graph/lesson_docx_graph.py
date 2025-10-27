# graph/lesson_docx_graph.py

from langgraph.graph import StateGraph
from graph.schema import State
from graph.nodes.download_lesson_node import download_lesson_node
from graph.nodes.generate_node import generate_node
from graph.nodes.generate_pptx_node import generate_pptx_node
from graph.nodes.save_node import save_node

# Initialize LangGraph with the custom shared State schema
workflow = StateGraph(State)

# Register each node
workflow.add_node("download_lesson_node", download_lesson_node)  # downloads the lesson file
workflow.add_node("generate_node", generate_node)                # generates lesson plan sections
workflow.add_node("generate_pptx_node", generate_pptx_node)      # generates slide deck using LLM
workflow.add_node("save_node", save_node)                        # saves Word document

# Define the flow of the pipeline
workflow.set_entry_point("download_lesson_node")                 # Step 1
workflow.add_edge("download_lesson_node", "generate_node")       # Step 2
workflow.add_edge("generate_node", "generate_pptx_node")         # Step 3
workflow.add_edge("generate_pptx_node", "save_node")             # Step 4
workflow.set_finish_point("save_node")                           # Step 5

# Compile and export the full graph app
lesson_docx_app = workflow.compile()
