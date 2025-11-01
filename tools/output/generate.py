import os
import uuid
import json
import re

FINAL_TXT_DIR = "data/outputs/final"
FINAL_JSON_DIR = "data/outputs/json"
FINAL_MD_DIR = "data/outputs/markdown"

os.makedirs(FINAL_TXT_DIR, exist_ok=True)
os.makedirs(FINAL_JSON_DIR, exist_ok=True)
os.makedirs(FINAL_MD_DIR, exist_ok=True)

def generate_final_output(lesson_text: str) -> dict:
    file_id = uuid.uuid4().hex
    txt_filename = f"final_lesson_{file_id}.txt"
    json_filename = f"final_lesson_{file_id}.json"
    md_filename = f"final_lesson_{file_id}.md"

    txt_path = os.path.join(FINAL_TXT_DIR, txt_filename)
    json_path = os.path.join(FINAL_JSON_DIR, json_filename)
    md_path = os.path.join(FINAL_MD_DIR, md_filename)

    enriched_text = lesson_text
    with open(txt_path, "w") as f:
        f.write(enriched_text)

    # === Markdown Output ===
    md_lines = []
    lines = enriched_text.splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            continue

        if stripped.lower().startswith("title:"):
            md_lines.append(f"# {stripped.replace('Title:', '').strip()}")
            continue
        elif "instructions" in stripped.lower():
            md_lines.append(f"## {stripped}")
            continue
        elif re.match(r"^\d+\.", stripped):
            md_lines.append(f"### {stripped}")
            continue
        elif stripped.endswith(":"):
            md_lines.append(f"**{stripped}**")
            continue

        # Preserve placeholders as plain text
        audio_match = re.search(r"\[Insert Audio:\s*(.+?)\]", stripped)
        if audio_match:
            md_lines.append(f"🔊 [Insert Audio: {audio_match.group(1).strip()}]")
            continue

        image_match = re.search(r"\[Insert Image:\s*(.+?)\]", stripped)
        if image_match:
            md_lines.append(f"🔍 [Insert Image: {image_match.group(1).strip()}]")
            continue

        md_lines.append(stripped)

    with open(md_path, "w") as md:
        md.write("\n\n".join(md_lines))

    # === JSON Output ===
    blocks = []
    for line in lines:
        audio_match = re.search(r"\[Insert Audio:\s*(.+?)\]", line)
        if audio_match:
            blocks.append({"type": "audio", "placeholder": audio_match.group(1).strip()})
            continue

        image_match = re.search(r"\[Insert Image:\s*(.+?)\]", line)
        if image_match:
            blocks.append({"type": "image", "placeholder": image_match.group(1).strip()})
            continue

        text_content = line.strip()
        if text_content:
            blocks.append({"type": "text", "content": text_content})

    with open(json_path, "w") as jf:
        json.dump(blocks, jf, ensure_ascii=False, indent=2)

    return {
        "txt_path": txt_path,
        "json_path": json_path,
        "md_path": md_path
    }