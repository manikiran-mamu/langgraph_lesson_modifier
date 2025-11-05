from tools.visuals.fetch import get_image_urls_from_serpapi, download_images
from openai import OpenAI
import os, ast, re

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_image_queries(text: str, rules: list) -> list:
    """
    Use LLM to suggest what image topics should be added to the lesson.
    """
    print("[VisualNode] Extracting image queries...")  
    if not any("visual" in rule.lower() for rule in rules):
        print("no Visuals rule found")
        return []

    prompt = f"""
You are an assistant that helps make lesson plans more visual and engaging.

Lesson:
{text}

Rules:
{rules}

Extract 3–5 short and searchable visual topics that would help illustrate this lesson. Return them as a Python list of strings.

Visual Suggestions:
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        timeout=30
    )

    raw = response.choices[0].message.content.strip()
    print("raw:", raw)  # debugging

    # --- Clean raw output ---
    if raw.startswith("```"):
        raw = raw.strip("`")                # remove backticks
        lines = raw.splitlines()
        lines = [line for line in lines if not line.strip().startswith("python")]
        raw = "\n".join(lines).strip()

    if "=" in raw:
        try:
            raw = raw.split("=", 1)[1].strip()
        except:
            pass

    try:
        queries = ast.literal_eval(raw)
        return queries if isinstance(queries, list) else []
    except Exception as e:
        print("[VisualNode] Failed to eval raw:", raw, "Error:", e)
        return []

def visual_node(state: dict) -> dict:
    text = state.get("modified_lesson_text", "")
    rules = state.get("rules", [])

    if not text or not rules:
        state.update({"image_paths": []})  # ensure key exists
        return state

    # 1. Extract image queries from lesson
    queries = extract_image_queries(text, rules)

    # 2. Clean and download images for each query
    image_urls = []
    for query in queries:
        urls = get_image_urls_from_serpapi(query, count=1)
        if not urls:
            print(f"[VisualNode] No images found for query: {query}")
            continue
        image_urls.extend(urls)

    if not image_urls:
        print("[VisualNode] No valid image URLs to download.")
        state.update({"image_paths": []})  # ✅ fix
        return state

    image_paths = download_images(image_urls)

    # 3. Replace placeholders using a COPY of image_paths
    image_paths_copy = image_paths.copy()

    def replacement(match, filenames=image_paths_copy):
        if filenames:
            path = filenames.pop(0)
            filename = os.path.basename(path)
            return f"[IMAGE:{filename}]"
        else:
            return match.group(0)

    pattern = r"\[Insert Image:.*?\]"
    text = re.sub(pattern, replacement, text)

    # 4. Append extras if leftover in copy (not original)
    for path in image_paths_copy:
        filename = os.path.basename(path)
        if filename not in text:
            text += f"\n\n[IMAGE:{filename}]"

    # 5. Update state
    state.update({
        "modified_lesson_text": text,
        "image_paths": image_paths
    })
    return state