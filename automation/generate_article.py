import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parent.parent
DRAFTS_DIR = BASE_DIR / "drafts"

NEWS_FILE = DRAFTS_DIR / "collected_news.json"
PROCESSED_FILE = DRAFTS_DIR / "processed_news.json"

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
TIMEZONE = ZoneInfo("Asia/Kolkata")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def load_json(path, default):
    """Load JSON safely, using the default when the file does not exist."""
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"Could not read {path.name}: {error}")
        return default


def make_slug(title):
    """Create a filesystem-friendly filename part."""
    slug = re.sub(r"[^a-z0-9]+", "-", str(title).lower())
    return slug.strip("-")[:70] or "news-update"


def make_meta_description(summary, headline):
    """Create a short draft description from supplied RSS information."""
    text = re.sub(r"\s+", " ", str(summary or "")).strip()
    if not text:
        text = str(headline or "The latest technology news from AIToday.")
    if len(text) > 155:
        text = text[:152].rsplit(" ", 1)[0].rstrip(" ,;:-") + "..."
    return text


def remove_leading_h1(article):
    """Avoid a second main title because the draft wrapper supplies the H1."""
    lines = article.strip().splitlines()

    while lines and not lines[0].strip():
        lines.pop(0)

    if lines and re.match(r"^\s*#\s+", lines[0]):
        lines.pop(0)

    return "\n".join(lines).strip()


def generate_with_retry(prompt):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an accurate technology journalist for AIToday. "
                        "Never fabricate facts. Use only the supplied information. "
                        "Clearly label uncertainty and do not imply that you read "
                        "the full source article when only an RSS summary is provided."
                    ),
                    max_output_tokens=1600,
                    temperature=0.3,
                ),
            )

            article = (response.text or "").strip()

            if not article:
                raise RuntimeError("Gemini returned an empty response.")

            return remove_leading_h1(article)

        except Exception as error:
            print(f"Gemini attempt {attempt + 1} failed: {error}")

            if attempt == 2:
                print("Skipping this article after 3 failed attempts.")
