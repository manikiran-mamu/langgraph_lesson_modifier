import os
import uuid
import requests
from typing import List
from serpapi import GoogleSearch

# Directory to store downloaded images
IMAGE_OUTPUT_DIR = "data/outputs/images"
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

# Environment variable
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
BASE_IMAGE_URL = "https://langgraph-lesson-modifier.onrender.com/images/"

def get_image_urls_from_serpapi(query: str, count: int = 1) -> List[str]:
    """
    Fetch image URLs from Google Images using SerpAPI.
    """
    if not SERPAPI_KEY:
        print("[SerpAPI] SERPAPI_KEY is missing.")
        return []

    try:
        params = {
            "engine": "google_images",         # Correct engine for image search
            "q": query,
            "location": "United States",        # Optional but helpful for localization
            "api_key": SERPAPI_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "images_results" not in results:
            print(f"[SerpAPI] No results found for query: {query}")
            return []

        # Extract original image URLs
        image_urls = [img["original"] for img in results["images_results"][:count]]
        print(f"[SerpAPI] Fetched {len(image_urls)} images for: '{query}'")
        return image_urls

    except Exception as e:
        print(f"[SerpAPI] Error fetching images for '{query}': {e}")
        return []

def download_images(image_urls: List[str]) -> List[str]:
    """
    Downloads images and returns their public URLs.
    """
    downloaded_urls = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in image_urls:
        try:
            print(f"[Download] Downloading: {url}")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"[Download] Failed with status {response.status_code}")
                continue

            filename = f"image_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            public_url = f"{BASE_IMAGE_URL}{filename}"
            downloaded_urls.append(public_url)

        except Exception as e:
            print(f"[Download] Error downloading image from {url}: {e}")

    print(f"[Download] Total images downloaded: {len(downloaded_urls)}")
    return downloaded_urls