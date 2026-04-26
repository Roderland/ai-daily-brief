"""构建静态站点：将数据文件复制到 web 目录"""

import json
import shutil
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
DATA_DIR = project_root / "data"
WEB_DIR = project_root / "web"
WEB_DATA_DIR = WEB_DIR / "data"


def build():
    WEB_DATA_DIR.mkdir(exist_ok=True)

    # 复制 index.json
    src_index = DATA_DIR / "index.json"
    if src_index.exists():
        shutil.copy2(src_index, WEB_DATA_DIR / "index.json")
        print("Copied index.json")

    # 复制所有简报
    for f in DATA_DIR.glob("brief_*.json"):
        shutil.copy2(f, WEB_DATA_DIR / f.name)
        print(f"Copied {f.name}")

    # 复制深挖结果
    src_dd = DATA_DIR / "deep_dives"
    dst_dd = WEB_DATA_DIR / "deep_dives"
    if src_dd.exists():
        dst_dd.mkdir(exist_ok=True)
        for f in src_dd.glob("*.json"):
            shutil.copy2(f, dst_dd / f.name)
            print(f"Copied deep_dives/{f.name}")

    # 生成深挖索引
    dd_index = {"dives": []}
    dd_index_file = DATA_DIR / "deep_dives_index.json"
    if dd_index_file.exists():
        shutil.copy2(dd_index_file, WEB_DATA_DIR / "deep_dives_index.json")
    else:
        with open(WEB_DATA_DIR / "deep_dives_index.json", "w") as f:
            json.dump(dd_index, f)

    print("✅ 站点构建完成")


if __name__ == "__main__":
    build()
