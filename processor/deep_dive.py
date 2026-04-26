"""深挖 Agent - 对单条内容进行深度分析"""

import json
import os
from datetime import datetime

DEEP_DIVE_SYSTEM_PROMPT = """你是一个 AI 创业分析专家。收到用户感兴趣的一个 AI 相关话题后，你需要：
1. 基于已有信息分析这个方向
2. 利用你的知识补充背景和洞察
3. 给出结构化的深度分析报告

请输出 JSON 格式：
{
  "topic": "分析主题",
  "overview": "概述（100字以内）",
  "business_model_analysis": "商业模式分析（200字以内）",
  "target_users": "目标用户画像（100字以内）",
  "key_insights": ["洞察1", "洞察2", "洞察3"],
  "challenges": ["挑战1", "挑战2"],
  "opportunities": ["机会1", "机会2"],
  "technical_feasibility": "技术可行性评估（100字以内）",
  "difficulty_level": "1-5",
  "similar_cases": "类似案例或竞品（100字以内）",
  "recommendation": "行动建议（100字以内）"
}
"""


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 LLM"""
    provider = os.environ.get("AI_PROVIDER", "anthropic").lower()
    api_key = os.environ.get("AI_API_KEY", "")
    model = os.environ.get("AI_MODEL", "claude-sonnet-4-20250514" if provider == "anthropic" else "gpt-4o")

    if not api_key:
        raise ValueError("AI_API_KEY 未配置")

    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content
    else:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.4,
            max_tokens=4000,
        )
        return resp.content[0].text


def deep_dive(topic: str, context: str = "") -> dict:
    """对指定主题进行深度分析"""
    user_prompt = f"请分析以下 AI 创业话题：\n\n话题：{topic}\n\n"
    if context:
        user_prompt += f"相关背景：{context}\n\n"
    user_prompt += "请给出深度分析报告。"

    report = {
        "topic": topic,
        "requested_at": datetime.now().isoformat(),
        "status": "processing",
        "content": {},
        "error": None,
    }

    try:
        result = _call_llm(DEEP_DIVE_SYSTEM_PROMPT, user_prompt)
        report["content"] = json.loads(result)
        report["status"] = "completed"
    except json.JSONDecodeError as e:
        report["status"] = "completed"
        report["content"] = {"raw_analysis": result}
        report["error"] = f"JSON parse error: {e}"
    except Exception as e:
        report["status"] = "failed"
        report["error"] = str(e)

    return report
