"""深挖入口脚本：对指定主题进行深度分析并保存结果"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from processor.deep_dive import deep_dive

DATA_DIR = project_root / "data"
DEEP_DIVE_DIR = DATA_DIR / "deep_dives"
DEEP_DIVE_DIR.mkdir(exist_ok=True)


def main():
    topic = os.environ.get("DEEP_DIVE_TOPIC", "")
    context = os.environ.get("DEEP_DIVE_CONTEXT", "")

    if not topic:
        print("❌ 请设置 DEEP_DIVE_TOPIC 环境变量指定要深挖的话题")
        return 1

    print(f"=== 深挖分析: {topic} ===")

    result = deep_dive(topic, context)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:50]
    filename = f"deepdive_{timestamp}_{safe_name}.json"
    filepath = DEEP_DIVE_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 更新深挖索引
    dd_index_path = DATA_DIR / "deep_dives_index.json"
    if dd_index_path.exists():
        with open(dd_index_path, "r", encoding="utf-8") as f:
            dd_index = json.load(f)
    else:
        dd_index = {"dives": []}
    dd_index["dives"].append({
        "topic": topic,
        "file": filename,
        "timestamp": timestamp,
        "date": datetime.now().strftime("%Y-%m-%d"),
    })
    with open(dd_index_path, "w", encoding="utf-8") as f:
        json.dump(dd_index, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 深挖完成！结果保存到: {filepath}")

    if result["status"] == "completed" and result.get("content"):
        content = result["content"]
        print(f"\n📋 概述: {content.get('overview', 'N/A')}")
        print(f"💡 商业模式: {content.get('business_model_analysis', 'N/A')}")
        print(f"🎯 可行建议: {content.get('recommendation', 'N/A')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
