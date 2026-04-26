"""信息源配置"""

RSS_SOURCES = {
    "36kr_ai": {
        "name": "36氪 AI",
        "url": "https://36kr.com/feed/flow/ai",
        "type": "rss",
        "category": "行业动态",
        "enabled": True,
    },
    "huxiu_ai": {
        "name": "虎嗅 AI",
        "url": "https://www.huxiu.com/rss/0.xml",
        "type": "rss",
        "category": "行业动态",
        "enabled": True,
    },
    "sspai": {
        "name": "少数派",
        "url": "https://sspai.com/feed",
        "type": "rss",
        "category": "工具类",
        "enabled": True,
    },
}

ZHIHU_TOPICS = [
    {"name": "AI 创业", "topic_id": "198198", "category": "商业模式"},
    {"name": "AI 产品", "topic_id": "198199", "category": "工具类"},
    {"name": "大模型", "topic_id": "198200", "category": "行业动态"},
]
