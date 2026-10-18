"""调整指定商品的价格。

用法：python scripts/set_price.py <商品id> <新价格> [<商品id> <新价格> ...]
例：  python scripts/set_price.py tiktok-account-ph 5 tiktok-account-th 5
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


def main(argv) -> int:
    if not argv or len(argv) % 2 != 0:
        print(__doc__)
        return 2

    data = json.loads(DATA.read_text(encoding="utf-8"))
    index = {}
    for cat in data["categories"]:
        for item in cat["items"]:
            index[item["id"]] = item

    pairs = list(zip(argv[0::2], argv[1::2]))
    updated = 0
    for item_id, raw in pairs:
        if item_id not in index:
            print(f"找不到商品：{item_id}")
            return 1
        item = index[item_id]
        new = round(float(raw), 2)
        old = item["price"]
        item["price"] = new
        updated += 1
        print(f"  {item['name'][:36]:<38} ${old:g} -> ${new:g}")

    DATA.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"已更新 {updated} 个商品")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
