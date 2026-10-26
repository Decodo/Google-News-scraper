import csv
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ---------- Customize your scrape ----------
# Paste the full category URL or click a subcategory first and copy its URL.
# Subcategory URLs contain /sections/; parent category URLs do not.
TOPIC_URL = (
    "https://news.google.com/topics/"
    "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB"
    "?hl=en-GB&gl=GB&ceid=GB%3Aen"
)
MAX_ITEMS = 50             # Positive integer, or None for all visible results.
MAX_AGE_DAYS = None        # None = any date; examples: 1, 7, or 30.
INCLUDE_RELATED_ARTICLES = True  # False = only the first article in each story group.
OUTPUT_FILE = BASE_DIR / "scraped_articles.csv"
# -------------------------------------------

COLUMNS = ["Title", "URL", "Source", "Published", "Author", "Story Group", "Story URL"]
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def proxy_from_env():
    """Accept a full proxy URL or separate credentials in .env."""
    complete = os.getenv("PROXY_URL", "").strip()
    if complete:
        return complete

    username = os.getenv("PROXY_USERNAME", "")
    password = os.getenv("PROXY_PASSWORD", "")
    server = os.getenv("PROXY_SERVER", "http://gate.decodo.com:7000").strip()
    if not username or not password:
        raise ValueError("Set PROXY_URL or PROXY_USERNAME and PROXY_PASSWORD in .env")
    if not server.startswith(("http://", "https://")):
        server = "http://" + server
    parts = urlsplit(server)
    if not parts.hostname or parts.username is not None:
        raise ValueError("PROXY_SERVER must contain a host, without credentials")
    credentials = f"{quote(username, safe='')}:{quote(password, safe='')}"
    return urlunsplit(
        (parts.scheme, f"{credentials}@{parts.netloc}", parts.path, parts.query, parts.fragment)
    )


def is_topic_url(url):
    """Accept only Google News category/subcategory pages, never search URLs."""
    parts = urlsplit(url)
    return (
        parts.scheme == "https"
        and parts.hostname == "news.google.com"
        and parts.port is None
        and parts.username is None
        and parts.password is None
        and parts.path.startswith("/topics/")
        and len(parts.path) > len("/topics/")
    )


def clean(value):
    return " ".join((value or "").split())


def google_link(href, prefix):
    """Normalize displayed links; never request the linked pages."""
    if not href:
        return ""
    url = urljoin("https://news.google.com/", href)
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != "news.google.com"
            or not parts.path.startswith(prefix)):
        return ""
    return url


def article_anchors(soup):
    anchors = []
    seen = set()
    for a in soup.select("a[href]"):
        if a.get("aria-hidden") == "true" or a.has_attr("hidden"):
            continue
        url = google_link(a.get("href"), "/read/")
        title = clean(a.get_text(" ", strip=True))
        if url and title and len(title) >= 12 and url not in seen:
            seen.add(url)
            anchors.append(a)
    return anchors


def has_another_article(container, own_url):
    """Keep publisher/date/author attached to the correct article card."""
    for a in container.select("a[href]"):
        if a.get("aria-hidden") == "true" or not clean(a.get_text(" ", strip=True)):
            continue
        url = google_link(a.get("href"), "/read/")
        if url and url != own_url:
            return True
    return False


def article_container(anchor):
    own_url = google_link(anchor.get("href"), "/read/")
    for parent in anchor.parents:
        if not isinstance(parent, Tag) or parent.name in {"body", "html", "main"}:
            break
        if has_another_article(parent, own_url):
            break
        if parent.select_one(".vr1PYe, .wEwyrc") and parent.select_one("time[datetime]"):
            return parent

    for parent in anchor.parents:
        if not isinstance(parent, Tag) or parent.name in {"body", "html", "main"}:
            break
        if has_another_article(parent, own_url):
            break
        if parent.select_one(".vr1PYe, .wEwyrc, time[datetime], .bInasb"):
            return parent
    return anchor.parent


def story_details(anchor):
    """Some topic layouts group related publisher articles; others do not."""
    for parent in anchor.parents:
        if not isinstance(parent, Tag) or parent.name in {"body", "html", "main"}:
            break
        link = parent.select_one("a.svxzne[href*='/stories/']")
        if link and 1 <= len(parent.select("a.gPFEn")) <= 15:
            title = clean(link.get_text(" ", strip=True)).replace("chevron_right", "").strip()
            return title, google_link(link.get("href"), "/stories/")
    return "", ""


def extract_articles(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for anchor in article_anchors(soup):
        card = article_container(anchor)
        publisher = card.select_one(".vr1PYe, .wEwyrc")
        published = card.select_one("time[datetime]")
        author = card.select_one(".bInasb")
        author_text = clean(author.get_text(" ", strip=True)) if author else ""
        if author_text.lower().startswith("by "):
            author_text = author_text[3:]
        story_title, story_url = story_details(anchor)
        rows.append({
            "Title": clean(anchor.get_text(" ", strip=True)),
            "URL": google_link(anchor.get("href"), "/read/"),
            "Source": clean(publisher.get_text(" ", strip=True)) if publisher else "",
            "Published": clean(published.get("datetime", "")) if published else "",
            "Author": author_text,
            "Story Group": story_title,
            "Story URL": story_url,
        })
    return rows


def select_articles(rows):
    """Filter before limiting output, preserving the order on Google News."""
    selected = rows

    if MAX_AGE_DAYS is not None:
        if MAX_AGE_DAYS <= 0:
            raise ValueError("MAX_AGE_DAYS must be positive or None")
        cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
        dated = []
        for row in selected:
            try:
                published_at = datetime.fromisoformat(row["Published"].replace("Z", "+00:00"))
                if published_at.tzinfo is not None and published_at >= cutoff:
                    dated.append(row)
            except ValueError:
                continue
        selected = dated

    if not INCLUDE_RELATED_ARTICLES:
        seen_stories = set()
        first_of_each_story = []
        for row in selected:
            story_url = row["Story URL"]
            if story_url and story_url in seen_stories:
                continue
            if story_url:
                seen_stories.add(story_url)
            first_of_each_story.append(row)
        selected = first_of_each_story

    if MAX_ITEMS is not None:
        if not isinstance(MAX_ITEMS, int) or MAX_ITEMS <= 0:
            raise ValueError("MAX_ITEMS must be a positive integer or None")
        selected = selected[:MAX_ITEMS]
    return selected


def main():
    if not is_topic_url(TOPIC_URL):
        raise ValueError("TOPIC_URL must be a Google News https://news.google.com/topics/... URL")

    proxy = proxy_from_env()
    with requests.Session() as session:
        session.trust_env = False
        session.proxies.update({"http": proxy, "https": proxy})
        language = parse_qs(urlsplit(TOPIC_URL).query).get("hl", ["en-US"])[0]
        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": language,
        })
        kind = "subcategory" if "/sections/" in urlsplit(TOPIC_URL).path else "category"
        print(f"Fetching Google News {kind}...")
        response = session.get(TOPIC_URL, timeout=(12, 45), allow_redirects=False)

    print(f"HTTP status: {response.status_code}")
    if 300 <= response.status_code < 400:
        raise RuntimeError("Google returned a redirect; refusing to follow it")
    response.raise_for_status()
    if "text/html" not in response.headers.get("Content-Type", "").lower():
        raise RuntimeError("Expected an HTML page")
    if any(phrase in response.text.lower() for phrase in (
        "our systems have detected unusual traffic", "robot or human?",
        "before you continue to google",
    )):
        raise RuntimeError("Google returned an access or consent page")

    soup = BeautifulSoup(response.text, "html.parser")
    page_heading = soup.find("h1")
    if page_heading:
        print(f"Page heading: {clean(page_heading.get_text(' ', strip=True))}")

    rows = extract_articles(response.text)
    print(f"Articles available in initial HTML: {len(rows)}")
    if not rows:
        debug_file = BASE_DIR / "google_news_debug.html"
        debug_file.write_text(response.text, encoding="utf-8")
        print(f"No articles extracted. HTML saved for inspection: {debug_file}")
        return

    if any(sum(bool(r[f]) for r in rows) < len(rows) * 0.8 for f in ("Source", "Published")):
        debug_file = BASE_DIR / "google_news_debug.html"
        debug_file.write_text(response.text, encoding="utf-8")
        print(f"Some metadata may be missing. Debug HTML: {debug_file}")

    chosen = select_articles(rows)
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(chosen)

    print(f"Articles saved after filters and limit: {len(chosen)}")
    print("Fields in saved CSV:")
    for field in COLUMNS:
        populated = sum(bool(row[field]) for row in chosen)
        print(f"  {field}: {populated}/{len(chosen)}")
    print(f"CSV file: {OUTPUT_FILE}")
    if not chosen:
        print("No articles matched the settings. Try a wider date range.")
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError, RuntimeError, OSError) as error:
        print(f"Scrape failed: {error}")
        raise SystemExit(1)
