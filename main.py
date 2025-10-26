# Updated main.py for Placeholder-based Lesson Editing

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Union, Optional
from bs4 import BeautifulSoup
import html2text
import os
import uuid
import shutil

from tools.llm.student_map_updater import update_rule_file_based_on_feedback
from tools.audio.generate import generate_audio_file
from tools.visuals.fetch import get_image_urls_from_serpapi, download_images
from graph.lesson_placeholder_graph import lesson_placeholders_app
from graph.lesson_graph_from_rules import lesson_from_rules_app
from graph.lesson_docx_graph import lesson_docx_app  # <-- new graph import

app = FastAPI(title="Lesson Modifier API - Placeholder Based")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Request Models =====
class FullPipelineRequest(BaseModel):
    student_profile: Dict[str, Union[str, List[str]]]
    lesson_url: HttpUrl
    file_category: Optional[str] = "Lesson"        # e.g., "Lesson" or "Worksheet"
    number_of_days: Optional[int] = 1    

class ShortPipelineRequest(BaseModel):
    rules: List[str]
    lesson_url: HttpUrl
    file_category: Optional[str] = "Lesson"        # e.g., "Lesson" or "Worksheet"
    number_of_days: Optional[int] = 1   

class ModifyLessonRequest(BaseModel):
    rules: List[str]
    lesson_url: HttpUrl

class GenerateAudioRequest(BaseModel):
    prompt: str

class RuleUpdateRequest(BaseModel):
    rule_file: List[str]
    feedback: str

class RuleUpdateResponse(BaseModel):
    updated_rule_file: List[str]

class LessonDocxRequest(BaseModel):
    student_profile: Dict[str, Union[str, List[str]]]
    lesson_objective: str
    language_objective: Dict[str, str]
    target_language: str

# ===== Root Route =====
@app.get("/")
def root():
    return {"message": "Lesson Modifier API is running 🚀 (Placeholder Mode)"}

# ===== Full Pipeline: Placeholder only =====
@app.post("/full-pipeline")
async def full_pipeline(request: FullPipelineRequest):
    try:
        result = lesson_placeholders_app.invoke({
            "student_profile": request.student_profile,
            "lesson_url": str(request.lesson_url),
            "number_of_days": request.number_of_days,              
            "file_category": str(request.file_category)
        })

        md_file = os.path.basename(result["final_output_md"])
        json_file = os.path.basename(result["final_output_json"])
        txt_file = os.path.basename(result["final_output_path"])

        return {
            "rules": result.get("rules", []),
            "final_output_md": f"https://langgraph-lesson-modifier.onrender.com/markdown/{md_file}",
            "final_output_json": f"https://langgraph-lesson-modifier.onrender.com/json/{json_file}",
            "final_output_path": f"https://langgraph-lesson-modifier.onrender.com/files/{txt_file}",
            "editor_url": f"https://langgraph-lesson-modifier.onrender.com/editor/index.html?file={md_file}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full pipeline failed: {str(e)}")


# ===== Update rules on Feedback =====
@app.post("/update-rule-file", response_model=RuleUpdateResponse)
async def update_rule_file(request: RuleUpdateRequest):
    try:
        updated_rules = update_rule_file_based_on_feedback(request.rule_file, request.feedback)
        return {"updated_rule_file": updated_rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Generate lesson plan from the Inputs =====
@app.post("/generate_lesson_docx")
async def generate_lesson_docx(request: LessonDocxRequest):
    try:
        result = lesson_docx_app.invoke({
            "student_profile": request.student_profile,
            "lesson_objective": request.lesson_objective,
            "language_objective": request.language_objective,
            "target_language": request.target_language
        })

        docx_file = os.path.basename(result["docx_path"])
        return {
            "docx_url": f"https://langgraph-lesson-modifier.onrender.com/files/{docx_file}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX pipeline failed: {str(e)}")



@app.post("/lesson_from_rules")
async def generate_lesson_from_existing_rules(request: ShortPipelineRequest):
    try:
        result = lesson_from_rules_app.invoke({
            "rules": request.rules,
            "lesson_url": str(request.lesson_url),
            "number_of_days": request.number_of_days,              
            "file_category": str(request.file_category)
        })

        md_file = os.path.basename(result["final_output_md"])
        json_file = os.path.basename(result["final_output_json"])
        txt_file = os.path.basename(result["final_output_path"])

        return {
            "final_output_md": f"https://langgraph-lesson-modifier.onrender.com/markdown/{md_file}",
            "final_output_json": f"https://langgraph-lesson-modifier.onrender.com/json/{json_file}",
            "final_output_path": f"https://langgraph-lesson-modifier.onrender.com/files/{txt_file}",
            "editor_url": f"https://langgraph-lesson-modifier.onrender.com/editor/index.html?file={md_file}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson from rules pipeline failed: {str(e)}")
    


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

# ===== Upload Image =====
@app.post("/api/save_markdown")  # ← This adds the route
async def save_markdown(request: Request):
    print("Received request to /api/save_markdown")
    try:
        print("i am here 1")
        data = await request.json()
        print("🔍 Incoming request body:", data)

        html = data.get("markdown", "")
        print("📝 Extracted HTML:", html if html else "[EMPTY]")

        user_id = data.get("user_id", "anon")
        print("👤 Extracted User ID:", user_id)

        # Step 1: Clean HTML
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(True):
            for attr in ["style", "class", "contenteditable", "data-type", "data-id"]:
                tag.attrs.pop(attr, None)

        # Step 2: Replace <audio> with proper markdown links
        for audio in soup.find_all("audio"):
            source_tag = audio.find("source")
            if source_tag and source_tag.has_attr("src"):
                audio_url = source_tag["src"]
                placeholder = f"[AUDIO: {audio_url}]"
            else:
                placeholder = "[AUDIO]"
            audio.replace_with(f"\n\n{placeholder}\n\n")

        # Step 3: Replace [IMAGE: ...] placeholders
        for span in soup.find_all("span"):
            text = span.get_text(strip=True)
            if "[IMAGE:" in text:
                cleaned = text.split("✎")[0].strip()
                span.replace_with(f"\n\n{cleaned}\n\n")

        # Step 4: Convert to Markdown
        cleaned_html = str(soup)

        converter = html2text.HTML2Text()
        converter.body_width = 0                # ✅ Disable auto line breaks
        converter.ignore_links = False
        converter.ignore_images = False
        converter.ignore_emphasis = False
        converter.protect_links = True          # ✅ Keeps full URLs safe
        markdown = converter.handle(cleaned_html)

        # Step 5: Save file
        filename = f"{user_id}_{uuid.uuid4().hex}.md"
        save_dir = "data/outputs/markdown"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        file_url = f"https://langgraph-lesson-modifier.onrender.com/markdown/{filename}"
        print(file_url)
        return {"url": file_url}

    except Exception as e:
        print("i am here 2")
        print("Error in /api/save_markdown:", str(e))
        return {"error": str(e)}

# ===== Static File Routes =====
app.mount("/files", StaticFiles(directory="data/outputs/final"), name="files")
app.mount("/json", StaticFiles(directory="data/outputs/json"), name="json")
app.mount("/markdown", StaticFiles(directory="data/outputs/markdown"), name="markdown")
app.mount("/audio", StaticFiles(directory="data/outputs/audio"), name="audio")
app.mount("/images", StaticFiles(directory="data/outputs/images"), name="images")
app.mount("/editor", StaticFiles(directory="editor"), name="editor")
