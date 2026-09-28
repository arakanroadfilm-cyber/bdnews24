import os
import json
import requests
import feedparser

# Load credentials securely from GitHub Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

BDNEWS_RSS_URL = "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true"
POSTED_ARTICLES_FILE = "posted_articles.json"


def load_posted_articles():
    if os.path.exists(POSTED_ARTICLES_FILE):
        try:
            with open(POSTED_ARTICLES_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading saved articles: {e}")
            return set()
    return set()


def save_posted_articles(posted_set):
    try:
        with open(POSTED_ARTICLES_FILE, "w") as f:
            json.dump(list(posted_set), f, indent=2)
    except Exception as e:
        print(f"Error saving posted articles: {e}")


def send_telegram_notification(title, link, published):
    message = (
        f"<b>📰 BDNews24 Update</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"🕒 <i>{published}</i>\n"
        f"🔗 <a href='{link}'>Read Full Article</a>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        res_data = response.json()
        if res_data.get("ok"):
            print(f"[SUCCESS] Posted: {title}")
            return True
        else:
            print(f"[ERROR] API Error: {res_data.get('description')}")
            return False
    except Exception as e:
        print(f"[EXCEPTION] Request failed: {e}")
        return False


def run():
    posted_links = load_posted_articles()
    feed = feedparser.parse(BDNEWS_RSS_URL)

    # Process oldest first so notifications arrive in chronological order
    for entry in reversed(feed.entries):
        link = entry.get("link", "")
        title = entry.get("title", "No Title")
        published = entry.get("published", "Recent")

        if link and link not in posted_links:
            success = send_telegram_notification(title, link, published)
            if success:
                posted_links.add(link)

    save_posted_articles(posted_links)
