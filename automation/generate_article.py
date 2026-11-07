import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types


# ------------------------------------------------------------
# AIToday daily article draft generator
# This script creates drafts only. It NEVER publishes articles.
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DRAFTS_DIR = BASE_DIR / "drafts"
NEWS_FILE = DRAFTS_DIR / "collected_news.json"
PROCESSED_FILE = DRAFTS_DIR / "processed_news.json"

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
TIMEZONE = ZoneInfo("Asia/Kolkata")


def load_json(path, default):
    """Read JSON. Do not silently erase a corrupted processed-news file."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"{path.name} contains invalid JSON. Fix that file before running again."
        ) from error
    except OSError as error:
        raise RuntimeError(f"Could not read {path}: {error}") from error


def save_json(path, data):
    """Write JSON safely using a temporary file, then replace the original."""
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temporary_path.replace(path)


def make_slug(value):
    """Convert a headline into a filename-safe slug."""
    value = str(value or "").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:90].strip("-") or "untitled"


def clean_text(value):
    """Normalize a value from an RSS feed."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def yaml_quote(value):
    """Safely quote a string for YAML front matter."""
    return json.dumps(str(value or ""), ensure_ascii=False)


def remove_leading_h1(text):
    """Remove a generated first-level heading; the RSS title is used as H1."""
    lines = (text or "").strip().splitlines()

    while lines and not lines[0].strip():
        lines.pop(0)

    if lines and re.match(r"^\s*#\s+", lines[0]):
        lines.pop(0)

    return "\n".join(lines).strip()


def make_meta_description(summary, headline):
    """Create a short search description from supplied RSS text."""
    source_text = clean_text(summary) or clean_text(headline)
    source_text = re.sub(r"\s+", " ", source_text)
    if len(source_text) > 155:
        source_text = source_text[:152].rsplit(" ", 1)[0] + "..."
    return source_text



def generate_with_retry(client, prompt):
    """Ask Gemini to draft an article, retrying temporary failures."""
    last_error = None

    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an accurate technology news editor. "
                        "Use only facts explicitly present in the supplied headline "
                        "and RSS summary. Never invent names, dates, statistics, "
                        "quotes, financial terms, technical details, or events. "
                        "If information is missing, say it is not specified or omit it. "
                        "Do not claim you read the linked article. "
                        "Write clear, original, neutral English."
                    ),
                    temperature=0.3,
                    max_output_tokens=1600,
                ),
            )

            article_text = getattr(response, "text", None)
            if not article_text or not article_text.strip():
                raise RuntimeError("Gemini returned an empty response.")

            return remove_leading_h1(article_text)

        except Exception as error:
            last_error = error
            print(f"Generation attempt {attempt}/3 failed: {error}")
            if attempt < 3:
                time.sleep(attempt * 5)

    raise RuntimeError(f"Article generation failed after 3 attempts: {last_error}")


def get_news_items(news_data):
    """Accept either a list or a dictionary containing an articles list."""
    if isinstance(news_data, list):
        return news_data

    if isinstance(news_data, dict):
        articles = news_data.get("articles", [])
        if isinstance(articles, list):
            return articles

    raise RuntimeError(
        "collected_news.json must contain a list of articles "
        "or an object with an 'articles' list."
    )


def main():
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is missing from the environment.")

    news_data = load_json(NEWS_FILE, [])
    news_items = get_news_items(news_data)

    processed_data = load_json(PROCESSED_FILE, [])
    if not isinstance(processed_data, list):
        raise RuntimeError("processed_news.json must contain a JSON list.")

    processed_urls = {
        str(url) for url in processed_data if isinstance(url, str)
    }

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    today = datetime.now(TIMEZONE).date().isoformat()

    categories = [
        "Artificial Intelligence",
        "Cybersecurity",
        "Technology",
    ]

    new_drafts = 0

    for category in categories:
        selected_item = None

        for item in news_items:
            if not isinstance(item, dict):
                continue

            item_category = clean_text(item.get("category"))
            headline = clean_text(item.get("title"))
            summary = clean_text(item.get("summary"))
            url = clean_text(item.get("url"))

            if item_category != category:
                continue
            if not headline or not url:
                continue
            if not url.startswith(("https://", "http://")):
                continue
            if url in processed_urls:
                continue

            selected_item = {
                "title": headline,
                "summary": summary,
                "url": url,
            }
            break
        if selected_item is None:
            print(f"No new unprocessed article found for {category}.")
            continue

        headline = selected_item["title"]
        summary = selected_item["summary"]
        url = selected_item["url"]

        filename = (
            f"{today}-{make_slug(category)}-{make_slug(headline)}.md"
        )
        output_path = DRAFTS_DIR / filename

        # Never overwrite an existing draft.
        if output_path.exists():
            print(f"Draft already exists; skipping: {filename}")
            processed_urls.add(url)
            continue

        prompt = f"""
Create an original technology news article draft using ONLY the supplied RSS
headline and summary.

CATEGORY: {category}
HEADLINE: {headline}
RSS SUMMARY: {summary}

Requirements:
- Write approximately 300-400 words when the supplied facts support it.
- Use a clear opening paragraph and useful Markdown section headings.
- Explain why the reported development may matter, but do not speculate as fact.
- Do not invent quotes, statistics, dates, people, company statements, prices,
  technical details, or events.
- Do not add facts from your general knowledge.
- If the RSS summary is too limited to support 300 words, write a shorter,
  accurate article rather than adding unsupported material.
- Do not include an H1 heading; the publisher adds the headline separately.
- Do not include a source list or editor checklist in the article body.
- Do not say you read the full linked source.
- Return only the article body in Markdown.
"""

        try:
            article_body = generate_with_retry(client, prompt)
        except Exception as error:
            print(f"Could not generate draft for {category}: {error}")
            # Do not mark the URL processed; it can be retried next time.
            continue

        if not article_body:
            print(f"Empty article body for {category}; skipping.")
            continue

        meta_description = make_meta_description(summary, headline)

        front_matter = f"""---
date: {today}
category: {yaml_quote(category)}
status: pending_review
review_status: pending
approval_status: pending
source: {yaml_quote(url)}
seo_title: {yaml_quote(headline[:60])}
meta_description: {yaml_quote(meta_description)}
---

"""

        document = (
            front_matter
            + f"# {headline}\n\n"
            + f"**Category:** {category}  \n"
            + f"**Source:** [{url}]({url})\n\n"
            + article_body
            + "\n\n---\n\n"
            + "## Editor verification checklist\n\n"
            + "- [ ] Open and read the original source.\n"
            + "- [ ] Verify every factual claim against the original source.\n"
            + "- [ ] Remove or correct unsupported details.\n"
            + "- [ ] Check names, dates, numbers, and company statements.\n"
            + "- [ ] Review headline, SEO title, and meta description.\n"
            + "- [ ] Approve this draft manually before publication.\n"
        )

        try:
            # Exclusive creation avoids accidentally replacing another draft.
            with output_path.open("x", encoding="utf-8") as file:
                file.write(document)
        except FileExistsError:
            print(f"Draft appeared during generation; not overwriting: {filename}")
            processed_urls.add(url)
            continue
        except OSError as error:
            print(f"Could not save {filename}: {error}")
            continue

        processed_urls.add(url)
        new_drafts += 1
        print(f"Created pending-review draft: {filename}")

    save_json(PROCESSED_FILE, sorted(processed_urls))
    print(f"Finished. New drafts created: {new_drafts}")
    print("Safety: this script creates drafts only; it does not publish anything.")


if __name__ == "__main__":
    main()

