# main.py — FastAPI backend for Placeholder-based Lesson Editing

from requests import request
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Union, Optional
import os
import uuid
import shutil

from tools.audio.generate import generate_audio_file
from tools.visuals.fetch import get_image_urls_from_serpapi, download_images
from graph.lesson_docx_graph import lesson_docx_app  # LangGraph pipeline
from graph.lesson_placeholder_graph import lesson_placeholders_app

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

class FullPipelineRequest(BaseModel):
    student_profile: Dict[str, Union[str, List[str]]]
    lesson_url: HttpUrl
    file_category: Optional[str] = "Lesson"        # e.g., "Lesson" or "Worksheet"
    number_of_days: Optional[int] = 1    

class GenerateAudioRequest(BaseModel):
    prompt: str


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
    

# ===== Full Pipeline: Placeholder only =====
@app.post("/full-pipeline")
async def full_pipeline(request: Request, lesson_request: FullPipelineRequest):
    try:
        result = lesson_placeholders_app.invoke({
            "student_profile": lesson_request.student_profile,
            "lesson_url": str(lesson_request.lesson_url),
            "number_of_days": lesson_request.number_of_days,
            "file_category": str(lesson_request.file_category)
        })

        base_url = str(request.base_url).rstrip("/")

        md_file = os.path.basename(result["final_output_md"])
        json_file = os.path.basename(result["final_output_json"])
        txt_file = os.path.basename(result["final_output_path"])

        return {
            "rules": result.get("rules", []),
            "final_output_md": f"{base_url}/outputs/markdown/{md_file}",
            "final_output_json": f"{base_url}/outputs/json/{json_file}",
            "final_output_path": f"{base_url}/outputs/files/{txt_file}",
            "editor_url": f"{base_url}/editor/index.html?file={md_file}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full pipeline failed: {str(e)}")
    

# ===== Image Search for Placeholder Replacement =====
@app.get("/api/search_images")
async def search_images(q: str = Query(...)):
    try:
        urls = get_image_urls_from_serpapi(q, count=5)
        return download_images(urls)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    

# ===== Generate Audio on Demand =====
@app.post("/api/generate_audio")
async def generate_audio(request: GenerateAudioRequest):
    try:
        path = generate_audio_file(request.prompt)
        filename = os.path.basename(path)
        return {"audio_url": f"https://langgraph-lesson-modifier.onrender.com/audio/{filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ===== Upload Audio =====
@app.post("/api/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        out_path = f"data/outputs/audio/{uuid.uuid4().hex}_{file.filename}"
        with open(out_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
        filename = os.path.basename(out_path)
        return {"audio_url": f"https://langgraph-lesson-modifier.onrender.com/audio/{filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# === Ensure Output Directories Exist ===
output_subfolders = ["word", "slides", "worksheets", "source_materials", "markdown", "json", "files"]
for folder in output_subfolders:
    os.makedirs(f"data/outputs/{folder}", exist_ok=True)
os.makedirs("editor", exist_ok=True)

# === Mount Static File Routes ===
app.mount("/outputs", StaticFiles(directory="data/outputs"), name="outputs")
app.mount("/editor", StaticFiles(directory="editor"), name="editor")
app.mount("/audio", StaticFiles(directory="data/outputs/audio"), name="audio")
app.mount("/images", StaticFiles(directory="data/outputs/images"), name="images")