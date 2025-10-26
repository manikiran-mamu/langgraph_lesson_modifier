# schema.py

from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Union, Optional

class State(BaseModel):
    """
    Central state object passed between pipeline nodes.
    Tracks lesson, rules, multimedia paths, and generated outputs.
    """
    student_profile: Optional[Dict[str, Union[str, List[str]]]] = None
    rules: Optional[List[str]] = None
    lesson_url: Optional[HttpUrl] = None
    lesson_file_path: Optional[str] = None
    lesson_content: Optional[str] = None
    modified_lesson_text: Optional[str] = None
    audio_paths: Optional[List[str]] = None
    image_paths: Optional[List[str]] = None

    file_category: Optional[str] = "Lesson"   # e.g., "Lesson" or "Worksheet"
    number_of_days: Optional[int] = 1 

    final_output_path: Optional[str] = None   # path to final .txt file
    final_output_json: Optional[str] = None  # path to final .json file for structured display
    final_output_md: Optional[str] = None    # ✅ path to final .md file

    # 📘 New DOCX Flow Additions
    lesson_objective: Optional[str] = None
    language_objective: Optional[Dict[str, str]] = None
    target_language: Optional[str] = None
    generated_sections: Optional[Dict[str, str]] = None  # from LLM
    docx_path: Optional[str] = None

    def get(self, key, default=None):
        """
        Mimic dict-like get() for pipeline nodes.
        """
        return getattr(self, key, default)

    def update(self, updates: Dict[str, Union[str, List[str], List[Dict], None]]):
        """
        Mimic dict-like update() for pipeline nodes.
        """
        for key, value in updates.items():
            setattr(self, key, value)
        return self
