#!/usr/bin/env python3
"""Agent Signal - fetch GitHub trending AI-agent tooling into data/trends.json.

Data sources (all public, no token required):
  - GitHub Search API (10 req/min unauthenticated)
  - GitHub REST /repos (60 req/hr) for the small curated Hermes-ecosystem list

Outputs:
  - data/trends.json   (site payload)
  - data/history.json  (daily star snapshots; keeps last 90 days)

Score rubric (max 100):
  momentum 0-40  (stars gained over 7d, from history snapshots; None -> provisional)
  activity 0-25  (push recency + forks + issue load)
  fit      0-25  (curated 0-10 * 2.5 from config/fit_scores.yaml; default 5.0)
  docs     0-10  (license known + useful description)
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import subprocess
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CONFIG = os.path.join(ROOT, "config", "fit_scores.yaml")

UA = {"User-Agent": "agent-signal-research/1.0", "Accept": "application/vnd.github+json"}


def get_token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    for exe in ("gh", r"D:\AI-AGENT\Tools\gh\bin\gh.exe"):
        try:
            out = subprocess.check_output([exe, "auth", "token"],
                                          stderr=subprocess.DEVNULL, timeout=10)
            tok = out.decode().strip()
            if tok.startswith(("gho_", "ghp_", "github_pat_")):
                return tok
        except Exception:  # noqa: BLE001
            continue
    return None


TOKEN = get_token()

CATEGORIES = [
    {
        "key": "agent-skills",
        "title": "Agent Skills",
        "blurb": "Các module skill tái sử dụng và registry cho coding agent.",
        "query": "topic:agent-skills+stars:>200",
    },
    {
        "key": "agent-frameworks",
        "title": "Agent Frameworks",
        "blurb": "Harness, orchestration và runtime cho agent tự chủ.",
        "query": "topic:ai-agents+stars:>1000",
    },
    {
        "key": "context-memory",
        "title": "Context & Memory",
        "blurb": "Nén token, bộ nhớ dài hạn và lớp truy xuất cho agent.",
        "query": "memory+context+agents+LLM+stars:>300",
    },
    {
        "key": "mcp-servers",
        "title": "MCP Servers",
        "blurb": "Máy chủ Model Context Protocol — nối agent vào tool thật.",
        "query": "topic:mcp-servers+stars:>100",
    },
]

CURATED_HERMES = [
    "NousResearch/hermes-agent",
    "Aitherium/awskills",
    "reason-machines/ai-agent-skills",
    "mcpbeat/best-mcp-servers",
    "0xNyk/awesome-hermes-agent",
    "openai/skills",
    "anthropics/skills",
]


def http_json(url: str, params: dict | None = None, retries: int = 2):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(
            params, quote_via=urllib.parse.quote)
    for attempt in range(retries + 1):
        try:
            headers = dict(UA)
            if TOKEN:
                headers["Authorization"] = "Bearer " + TOKEN
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            if attempt == retries:
                raise
            print(f"[warn] {url} failed ({exc}); retry {attempt + 1}", file=sys.stderr)
            time.sleep(4)


def search(q: str, per_page: int = 10):
    """Search with search-quota guard."""
    rl = http_json("https://api.github.com/rate_limit")
    left = rl["resources"]["search"]["remaining"]
    reset = rl["resources"]["search"]["reset"]
    if left < 2:
        wait = max(1, int(reset - time.time()) + 2)
        print(f"[info] search quota low ({left}); sleeping {wait}s", file=sys.stderr)
        time.sleep(wait)
    return http_json(
        "https://api.github.com/search/repositories",
        {"q": q.replace("+", " "), "sort": "stars", "order": "desc", "per_page": per_page},
    )


def _unquote(s: str) -> str:
    """Reader này không parse YAML quote -> tự cắt cặp " hoặc ' bao quanh giá trị."""
    s = (s or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1].strip()
    return s


def load_fit() -> dict:
    """Tiny YAML reader for the flat fit_scores map used here."""
    out = {}
    if not os.path.exists(CONFIG):
        return out
    section = False
    current = None
    for raw in open(CONFIG, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("fit_scores:"):
            section = True
            continue
        if not section or not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and ":" in line and not line.startswith("    "):
            current = line.strip().split(":", 1)[0].strip()
            out[current] = {}
        elif line.startswith("    ") and ":" in line and current:
            k, v = line.strip().split(":", 1)
            out[current][k.strip()] = v.strip()
    return {k: (float(v.get("score", 5.0)), _unquote(v.get("why", ""))) for k, v in out.items()}


def load_history() -> dict:
    p = os.path.join(DATA, "history.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"days": {}}


def save_history(h: dict):
    days = h["days"]
    if len(days) > 90:
        for key in sorted(days)[: len(days) - 90]:
            days.pop(key, None)
    json.dump(h, open(os.path.join(DATA, "history.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def delta_7d(history: dict, full_name: str, today: str) -> int | None:
    days = history["days"]
    if today not in days:
        return None
    targets = []
    t = dt.date.fromisoformat(today)
    for back in range(6, 9):
        key = (t - dt.timedelta(days=back)).isoformat()
        snap = days.get(key)
        if snap and full_name in snap:
            targets.append((back, snap[full_name]))
    if not targets:
        return None
    back, prev = targets[0]
    return int(days[today][full_name]) - int(prev)


def score_repo(repo: dict, delta, fit: float) -> tuple[int | None, dict]:
    # momentum
    if delta is None:
        momentum = None
    else:
        momentum = max(0, min(40, round(delta / 300 * 40)))

    pushed = repo.get("pushed_at") or ""
    try:
        age_days = (dt.datetime.now(dt.timezone.utc) -
                    dt.datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days
    except Exception:
        age_days = 9999
    recency = 12 if age_days <= 7 else 9 if age_days <= 30 else 6 if age_days <= 90 else 3 if age_days <= 180 else 1
    forks = int(repo.get("forks_count") or 0)
    fork_pts = 7 if forks >= 1000 else 5 if forks >= 300 else 3 if forks >= 50 else 1
    issues = int(repo.get("open_issues_count") or 0)
    issue_pts = 6 if issues < 200 else 4 if issues < 1000 else 2
    activity = recency + fork_pts + issue_pts

    fit_pts = max(0, min(10, fit)) * 2.5

    lic = (repo.get("license") or {}).get("spdx_id")
    desc = (repo.get("description") or "").strip()
    docs = (5 if lic and lic != "NOASSERTION" else 2) + (5 if len(desc) >= 60 else 3)

    parts = {"momentum": momentum, "activity": activity,
             "fit": round(fit_pts, 1), "docs": docs}
    maxima = {"momentum": 40, "activity": 25, "fit": 25, "docs": 10}
    known = [(parts[k], maxima[k]) for k in parts if parts[k] is not None]
    total = round(sum(v for v, _ in known) / sum(m for _, m in known) * 100) if known else None
    return total, parts


def to_row(repo: dict, history: dict, today: str, fit_map: dict, curated_names: set[str]):
    full = repo["full_name"]
    fit, why = fit_map.get(full, (5.0, ""))
    delta = delta_7d(history, full, today)
    score, parts = score_repo(repo, delta, fit)
    lic = (repo.get("license") or {}).get("spdx_id")
    return {
        "name": repo["name"],
        "full_name": full,
        "url": repo["html_url"],
        "blurb": (repo.get("description") or "").strip()[:160],
        "lang": repo.get("language"),
        "stars": int(repo.get("stargazers_count") or 0),
        "delta_7d": delta,
        "license": lic,
        "pushed_at": repo.get("pushed_at"),
        "topics": repo.get("topics") or [],
        "fit": fit,
        "fit_curated": full in fit_map,
        "fit_note": why if full in fit_map else "Not curated yet — no direct integration assessed.",
        "score": score,
        "score_parts": parts,
        "curated": full in curated_names,
    }


def main():
    os.makedirs(DATA, exist_ok=True)
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).date().isoformat()
    fit_map = load_fit()
    curated_names = {f for f in CURATED_HERMES if "/" in f}
    history = load_history()

    sections = []
    seen = set()
    for cat in CATEGORIES:
        data = search(cat["query"])
        rows = []
        for repo in data.get("items", []):
            if repo["full_name"] in seen:
                continue
            seen.add(repo["full_name"])
            rows.append(to_row(repo, history, today, fit_map, curated_names))
        sections.append({**{k: cat[k] for k in ("key", "title", "blurb")},
                         "query": cat["query"], "count": len(rows), "repos": rows})
        time.sleep(2)

    # Curated Hermes ecosystem via /repos (core quota, not search)
    rows = []
    for full in CURATED_HERMES:
        try:
            repo = http_json(f"https://api.github.com/repos/{full}")
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] curated {full} failed: {exc}", file=sys.stderr)
            continue
        rows.append(to_row(repo, history, today, fit_map, curated_names))
        time.sleep(1)
    sections.append({
        "key": "hermes-ecosystem",
        "title": "Hermes Ecosystem",
        "blurb": "Hệ sinh thái ta đang chạy: runtime Hermes, skills tap, MCP discovery.",
        "query": "curated list (hand-maintained)",
        "count": len(rows),
        "repos": rows,
    })

    # snapshot for future deltas
    snap = {}
    for sec in sections:
        for r in sec["repos"]:
            snap[r["full_name"]] = r["stars"]
    history.setdefault("days", {})[today] = snap
    save_history(history)

    payload = {
        "generated_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(timespec="seconds"),
        "snapshot_date": today,
        "method": {
            "source": "GitHub Search API + /repos (public, no token)",
            "rubric": "momentum 40% + activity 25% + fit 25% (curated) + docs 10%; provisional when 7d delta unavailable",
            "fit_config": "config/fit_scores.yaml",
        },
        "categories": sections,
    }
    out = os.path.join(DATA, "trends.json")
    json.dump(payload, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = sum(s["count"] for s in sections)
    print(f"[saved] {out} | sections={len(sections)} repos={total}")
    for s in sections:
        top = s["repos"][0]["full_name"] if s["repos"] else "-"
        print(f"  {s['key']}: {s['count']} repos | top: {top}")


if __name__ == "__main__":
    raise SystemExit(main())
