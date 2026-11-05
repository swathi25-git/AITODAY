import os
import json
import re
from datetime import date
from pathlib import Path
import time

from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
DRAFTS_DIR = BASE_DIR / "drafts"

NEWS_FILE = DRAFTS_DIR / "collected_news.json"
PROCESSED_FILE = DRAFTS_DIR / "processed_news.json"

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def make_slug(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")[:70]


def main():
    DRAFTS_DIR.mkdir(exist_ok=True)

    news_data = load_json(NEWS_FILE, [])

    if isinstance(news_data, dict):
        news_items = news_data.get(
            "items", news_data.get("articles", [])
        )
    else:
        news_items = news_data

    processed = load_json(PROCESSED_FILE, [])

    categories = [
    "Artificial Intelligence",
    "Cybersecurity",
    "Technology"
]
    today = date.today().isoformat()
    created = 0

    for category in categories:
        candidates = [
            item for item in news_items
            if item.get("category", "").lower() == category.lower()
            and item.get("url")
            and item["url"] not in processed
        ]

        if not candidates:
            print(f"No new story found for {category}")
            continue

        story = candidates[0]

        prompt = f"""
Write an original, informative blog article for AIToday.

CATEGORY: {category}
NEWS HEADLINE: {story.get('title', '')}
RSS SUMMARY: {story.get('summary', '')}
ORIGINAL SOURCE: {story.get('url', '')}
PUBLICATION DATE: {story.get('published', '')}

Rules:
- Write approximately 350-450 words.
- Use clear, natural English for general readers.
- Create an engaging, accurate headline.
- Explain why the development matters.
- Use only facts supported by the supplied headline and summary.
- Do not invent quotes, statistics, dates, names or technical details.
- Do not pretend you read the complete source article.
- If information is insufficient, keep the article brief and identify
  what readers should verify.
- Do not copy the source wording.
- Do not reproduce copyrighted passages.
- Include a short conclusion.
- Return the article in Markdown.
- Do not invent additional sources.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an accurate technology journalist. "
                    "Never fabricate facts. Write original articles "
                    "and clearly distinguish confirmed information "
                    "from anything that needs verification."
                ),
                max_output_tokens=1200,
                temperature=0.4
            )
        )

        article = (response.text or "").strip()

        if not article:
            raise RuntimeError("Gemini returned an empty response.")

        filename = (
            f"{today}-{category.lower()}-"
            f"{make_slug(story.get('title', 'news'))}.md"
        )

        output_path = DRAFTS_DIR / filename

        content = f"""---
date: {today}
category: {category}
status: draft
source: "{story['url']}"
---

# {story.get('title', 'News update')}

**Category:** {category}

**Original source:** {story['url']}

---

{article}

---

## Editor verification

- [ ] Verify facts against the original source.
- [ ] Check names, dates and statistics.
- [ ] Review copyright and image permissions.
- [ ] Approve before publishing.
"""

        output_path.write_text(content, encoding="utf-8")

        processed.append(story["url"])
        created += 1

        print(f"Created draft: {filename}")

    PROCESSED_FILE.write_text(
        json.dumps(processed, indent=2),
        encoding="utf-8"
    )

    print(f"Finished. Created {created} article drafts.")


if __name__ == "__main__":
    main()
