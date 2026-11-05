
import feedparser
import json
import os
import hashlib
from datetime import datetime, timezone

NEWS_SOURCES = {
    "Artificial Intelligence": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.technologyreview.com/feed/"
    ],
    "Cybersecurity": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.bleepingcomputer.com/feed/"
    ],
    "Technology": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://techcrunch.com/feed/"
    ]
}

OUTPUT_DIR = "drafts"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "collected_news.json")


def collect_news():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    collected = []
    seen = set()

    for category, feeds in NEWS_SOURCES.items():
        print(f"Collecting: {category}")

        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:15]:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "")

                    if not title or not link:
                        continue

                    news_id = hashlib.sha256(
                        link.encode("utf-8")
                    ).hexdigest()

                    if news_id in seen:
                        continue

                    seen.add(news_id)

                    collected.append({
                        "id": news_id,
                        "category": category,
                        "title": title,
                        "summary": entry.get(
                            "summary", ""
                        )[:3000],
                        "url": link,
                        "published": entry.get(
                            "published", ""
                        ),
                        "collected_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    })

            except Exception as error:
                print(f"Feed error: {feed_url}: {error}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            collected,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"Collected {len(collected)} unique news items.")


if __name__ == "__main__":
    collect_news()
