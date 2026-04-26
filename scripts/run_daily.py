"""每日简报运行入口：采集 → AI 处理 → 生成 JSON 数据"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 path 中
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from collector.rss_collector import collect_all
from processor.ai_summarizer import generate_brief

DATA_DIR = project_root / "data"
DATA_DIR.mkdir(exist_ok=True)


def load_existing_index() -> dict:
    """加载已有的简报索引"""
    index_path = DATA_DIR / "index.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"briefs": []}


def save_index(index: dict):
    """保存简报索引"""
    with open(DATA_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def save_daily_brief(items: list[dict], date_str: str):
    """保存单日简报"""
    brief_path = DATA_DIR / f"brief_{date_str}.json"
    with open(brief_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "items": items,
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved daily brief: {brief_path}")


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"=== AI 创业简报 {date_str} ===")

    # Step 1: 采集
    print("\n[1/3] 采集信息...")
    articles = collect_all()
    print(f"采集到 {len(articles)} 条内容")

    # Step 2: AI 处理
    print("\n[2/3] AI 生成简报...")
    items = generate_brief(articles)
    print(f"生成 {len(items)} 条简报项")

    # Step 3: 保存
    print("\n[3/3] 保存数据...")
    save_daily_brief(items, date_str)

    index = load_existing_index()
    index["briefs"].append({
        "date": date_str,
        "count": len(items),
    })
    save_index(index)

    print(f"\n✅ 简报完成！共 {len(items)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
