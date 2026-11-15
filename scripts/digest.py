#!/usr/bin/env python3
"""Agent Signal — bản tin sáng (digest) từ data/trends.json.

Dùng:  python scripts/digest.py            # bản tin tiếng Việt
       python scripts/digest.py --json     # JSON để đẩy tiếp

Nguồn: data/trends.json (do scripts/fetch_trends.py sinh). Không gọi API, không ghi file.
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRENDS = os.path.join(ROOT, "data", "trends.json")


def load(path=TRENDS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def flatten(data):
    out = []
    for cat in data.get("categories", []):
        for repo in cat.get("repos", []):
            out.append((cat.get("title", ""), repo))
    return out


def rank(items):
    """Sắp theo delta_7d (thiếu = -inf) rồi tới score — giống UI 'Tóm tắt sáng'.

    Một repo có thể trùng giữa các category (cùng query trả về); giữ bản có điểm cao nhất.
    """
    best = {}
    for cat, repo in items:
        name = repo.get("full_name")
        score = repo.get("score") or 0
        if name not in best or score > (best[name][1].get("score") or 0):
            best[name] = (cat, repo)
    ordered = list(best.values())

    def key(x):
        d = x[1].get("delta_7d")
        return (d if d is not None else float("-inf"), x[1].get("score") or 0)

    return sorted(ordered, key=key, reverse=True)


def fmt_move(repo):
    d = repo.get("delta_7d")
    if d is None:
        return "mới vào radar"
    sign = "+" if d >= 0 else ""
    return f"{sign}{d:,}★ / 7 ngày".replace(",", ".")


def text(data, limit=5):
    items = rank(flatten(data))
    lines = []
    lines.append(f"Agent Signal — bản tin sáng · {data.get('snapshot_date', '—')}")
    lines.append(f"Nguồn: {data.get('method', {}).get('source', 'GitHub API')}")
    lines.append("")
    for cat, r in items[:limit]:
        lines.append(f"• {r['full_name']} ({cat}) — {fmt_move(r)} · ★ {r.get('stars', 0):,} · {r.get('blurb', '')}")
    lines.append("")
    lines.append("Điểm = 40% momentum + 25% activity + 25% fit + 10% docs; fit do curator chấm.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()
    data = load()
    if args.json:
        items = rank(flatten(data))[: args.limit]
        print(json.dumps({
            "snapshot_date": data.get("snapshot_date"),
            "brief": [{"name": r["full_name"], "category": c, "stars": r.get("stars"),
                       "delta_7d": r.get("delta_7d"), "score": r.get("score"),
                       "blurb": r.get("blurb")} for c, r in items],
        }, ensure_ascii=False, indent=1))
    else:
        print(text(data, args.limit))


if __name__ == "__main__":
    main()
