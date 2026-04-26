"""RSS 采集器"""

import feedparser
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
from collector.sources import RSS_SOURCES


def fetch_rss(url: str) -> list[dict]:
    """从 RSS 源获取文章列表"""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:20]:
            articles.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "summary": _clean_html(entry.get("summary", "") or entry.get("description", "")),
                "published": entry.get("published", ""),
                "source": feed.feed.get("title", url),
            })
        return articles
    except Exception as e:
        print(f"RSS fetch error for {url}: {e}")
        return []


def fetch_zhihu_topic(topic_name: str, topic_id: str) -> list[dict]:
    """从知乎话题获取内容（通过热榜 API）"""
    articles = []
    try:
        url = f"https://www.zhihu.com/topic/{topic_id}/hot"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            for item in soup.select("div.TopicFeedItem")[:15]:
                title_el = item.select_one("h2.ContentItem-title")
                if title_el:
                    articles.append({
                        "title": title_el.get_text(strip=True),
                        "url": "https://www.zhihu.com" + (title_el.find("a") or {}).get("href", ""),
                        "summary": "",
                        "published": "",
                        "source": f"知乎-{topic_name}",
                    })
    except Exception as e:
        print(f"Zhihu fetch error for topic {topic_name}: {e}")
    return articles


def _clean_html(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "lxml")
    return soup.get_text(strip=True)[:500]


def collect_all() -> list[dict]:
    """采集所有启用的信息源"""
    all_articles = []

    for source_id, config in RSS_SOURCES.items():
        if not config.get("enabled"):
            continue
        print(f"Collecting from RSS: {config['name']}")
        articles = fetch_rss(config["url"])
        for a in articles:
            a["source_id"] = source_id
            a["category"] = config["category"]
        all_articles.extend(articles)

    for topic in ZHIHU_TOPICS:
        print(f"Collecting from Zhihu: {topic['name']}")
        articles = fetch_zhihu_topic(topic["name"], topic["topic_id"])
        for a in articles:
            a["source_id"] = f"zhihu_{topic['name']}"
            a["category"] = topic["category"]
        all_articles.extend(articles)

    return all_articles
