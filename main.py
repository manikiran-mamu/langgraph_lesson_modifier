# main.py — FastAPI backend for Placeholder-based Lesson Editing

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Union
import os

from graph.lesson_docx_graph import lesson_docx_app  # LangGraph pipeline

# === Initialize FastAPI App ===
app = FastAPI(title="Lesson Modifier API - Placeholder Based")

# === CORS Configuration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request Schema ===
class LessonDocxRequest(BaseModel):
    student_profile: Dict[str, Union[str, List[str]]]
    lesson_objective: str
    language_objective: Dict[str, str]
    target_language: str
    lesson_url: HttpUrl

# === Root Health Route ===
@app.get("/")
def root():
    return {"message": "Lesson Modifier API is running 🚀 (Placeholder Mode)"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# === Lesson DOCX Generation Endpoint ===
@app.post("/generate_lesson_docx")
async def generate_lesson_docx(request: Request, lesson_request: LessonDocxRequest):
    try:
        # Run LangGraph pipeline
        result = lesson_docx_app.invoke({
            "student_profile": lesson_request.student_profile,
            "lesson_objective": lesson_request.lesson_objective,
            "language_objective": lesson_request.language_objective,
            "target_language": lesson_request.target_language,
            "lesson_url": str(lesson_request.lesson_url)
        })

        base_url = str(request.base_url).rstrip("/")

        # Extract filenames from result
        docx_file = os.path.basename(result.get("final_output_docx", ""))
        pptx_file = os.path.basename(result.get("final_output_pptx", ""))
        worksheet_file = os.path.basename(result.get("student_worksheet_path", ""))
        reference_file = os.path.basename(result.get("source_material_path", ""))

        # Build response with public URLs
        response = {}
        if docx_file:
            response["lesson_plan_url"] = f"{base_url}/outputs/word/{docx_file}"
        if pptx_file:
            response["slide_deck_url"] = f"{base_url}/outputs/slides/{pptx_file}"
        if worksheet_file:
            response["worksheet_url"] = f"{base_url}/outputs/worksheets/{worksheet_file}"
        if reference_file:
            response["reference_material_url"] = f"{base_url}/outputs/source_materials/{reference_file}"

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX pipeline failed: {str(e)}")

# === Ensure Output Directories Exist ===
output_subfolders = ["word", "slides", "worksheets", "source_materials"]
for folder in output_subfolders:
    os.makedirs(f"data/outputs/{folder}", exist_ok=True)
os.makedirs("editor", exist_ok=True)

# === Mount Static File Routes ===
app.mount("/outputs", StaticFiles(directory="data/outputs"), name="outputs")
app.mount("/editor", StaticFiles(directory="editor"), name="editor")