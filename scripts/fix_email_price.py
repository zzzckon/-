"""把邮箱分类下所有商品价格统一为 1 美元。

用法：python scripts/fix_email_price.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "products.json"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    changed = 0
    for cat in data["categories"]:
        if cat["id"] != "email":
            continue
        for item in cat["items"]:
            old = item["price"]
            if old != 1:
                item["price"] = 1
                changed += 1
                print(f"  {item['name'][:36]:<38} ${old:g} -> $1")
            specs = item.get("specs", {})
            if "最小起订" in specs:
                specs["最小起订"] = "1 个"
    DATA.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"邮箱价格统一为 $1，共修改 {changed} 项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
