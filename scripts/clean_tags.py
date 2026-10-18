"""清理页面上无意义的内部标记。

「自有定价」是定价溯源时加的数据标记，不该出现在给客户看的商品卡片上。
用法：python scripts/clean_tags.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "products.json"

# 这些标签只用于内部溯源，不对外展示
INTERNAL_TAGS = {"自有定价"}

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    removed = 0
    for cat in data["categories"]:
        for item in cat["items"]:
            tags = item.get("tags", [])
            kept = [t for t in tags if t not in INTERNAL_TAGS]
            if len(kept) != len(tags):
                removed += len(tags) - len(kept)
                item["tags"] = kept
    DATA.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"已移除 {removed} 个内部标记")
    return 0


if __name__ == "__main__":
    sys.exit(main())
