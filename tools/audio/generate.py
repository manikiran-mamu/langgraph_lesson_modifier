# tools/audio/generate.py

import os
import uuid
from openai import OpenAI
from typing import List, Tuple

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

OUTPUT_DIR = "data/outputs/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def split_text_for_audio(text: str) -> List[str]:
    """
    Basic heuristic to split text into chunks for TTS narration.
    You can later improve this with NLP or LLM.
    """
    return text.split("\n\n")  # Split by paragraph

def generate_audio_for_text_chunks(chunks: List[str]) -> List[Tuple[str, str]]:
    """
    Converts each text chunk into an audio file.
    Returns list of (audio_path, audio_caption).
    """
    audio_results = []

    for idx, chunk in enumerate(chunks):
        if not chunk.strip():
            continue  # Skip empty parts

        try:
            filename = f"audio_{uuid.uuid4().hex}.mp3"
            audio_path = os.path.join(OUTPUT_DIR, filename)

            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="sage",  # or "shimmer", "onyx", etc.
                input=chunk
            )
            response.stream_to_file(audio_path)

            audio_results.append((f"https://langgraph-lesson-modifier.onrender.com/audio/{filename}", chunk.strip()))
            #audio_results.append((audio_path, chunk.strip()))
        except Exception as e:
            print(f"[AudioAgent] Failed to generate audio for chunk {idx}: {e}")
            continue

    return audio_results


def generate_audio_file(text: str) -> str:
    """
    Generate audio for a single sentence or prompt.
    Returns the file path to the generated MP3.
    """
    if not text.strip():
        raise ValueError("Empty text provided for TTS.")

    filename = f"audio_{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(OUTPUT_DIR, filename)

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",  # or "tts-1-hd" for better quality
        voice="sage",  # Or coral, shimmer, onyx, etc.
        input=text
    )
    response.stream_to_file(audio_path)

    return audio_path