"""AI 简报生成器 - 对采集内容进行摘要、分类、打标签"""

import json
import os
from datetime import datetime


def _get_llm():
    """根据配置获取 LLM 客户端"""
    provider = os.environ.get("AI_PROVIDER", "anthropic").lower()
    api_key = os.environ.get("AI_API_KEY", "")

    if not api_key:
        raise ValueError("AI_API_KEY 未配置")

    if provider == "openai":
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    else:
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 LLM"""
    provider = os.environ.get("AI_PROVIDER", "anthropic").lower()
    model = os.environ.get("AI_MODEL", "claude-sonnet-4-20250514" if provider == "anthropic" else "gpt-4o")

    client = _get_llm()
    if provider == "openai":
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    else:
        resp = client.messages.create(
            model=model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        return resp.content[0].text


CATEGORIES = ["工具类", "商业模式", "行业动态", "观点", "其他"]

BRIEF_SYSTEM_PROMPT = """你是一个 AI 创业资讯分析师。你的任务是从采集的文章中，筛选出与 AI 个人创业、AI 商业化最相关的信息，并为每条信息生成简洁的摘要。

请严格按照 JSON 格式输出。输出的 JSON 结构：
{
  "items": [
    {
      "title": "原标题",
      "summary": "一句话摘要（30字以内）",
      "analysis": "为什么这对创业者有价值（50字以内）",
      "category": "工具类/商业模式/行业动态/观点/其他",
      "tags": ["标签1", "标签2"],
      "importance": 1-5,
      "original_url": "原文链接",
      "source": "来源名称"
    }
  ]
}

筛选标准：
- 只保留与 AI 创业、AI 产品、AI 商业化直接相关的内容
- 过滤掉纯技术研究、与商业无关的 AI 新闻
- importance 1-5，5 为最重要
- summary 控制在 30 字以内，简洁有力
"""


def generate_brief(articles: list[dict]) -> list[dict]:
    """对采集的文章进行 AI 筛选和摘要"""
    if not articles:
        return []

    articles_text = json.dumps(articles, ensure_ascii=False, indent=2)
    user_prompt = f"以下是今日采集的 {len(articles)} 条文章，请分析并生成简报：\n\n{articles_text}"

    try:
        result = _call_llm(BRIEF_SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(result)
        items = parsed.get("items", [])
        for i, item in enumerate(items):
            item["date"] = datetime.now().strftime("%Y-%m-%d")
            item["id"] = f"{item['date']}_{i}"
        return items
    except Exception as e:
        print(f"AI summarizer error: {e}")
        # fallback: 返回原始文章的基础信息
        return [
            {
                "id": f"{datetime.now().strftime('%Y-%m-%d')}_{i}",
                "title": a.get("title", ""),
                "summary": (a.get("summary", "") or "")[:80],
                "analysis": "",
                "category": a.get("category", "其他"),
                "tags": [a.get("category", "其他")],
                "importance": 3,
                "original_url": a.get("url", ""),
                "source": a.get("source", ""),
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            for i, a in enumerate(articles[:20])
        ]
