# Agent Signal

A morning radar of trending GitHub tooling for AI agents — refreshed daily at **05:00 ICT**
(22:00 UTC) by a GitHub Actions job and published to GitHub Pages.

Sections: Agent Skills · Agent Frameworks · Context & Memory · MCP Servers · Hermes Ecosystem.

Every repo carries:
- live stars + 7-day delta (from daily snapshots in `data/history.json`)
- an auto-score 0–100 with a visible formula
- a short “Why here” note when it is curated against our stack (`config/fit_scores.yaml`)

## Run locally

```bash
python3 -m http.server 8080 --bind 127.0.0.1   # from this folder
python3 scripts/fetch_trends.py                # writes data/trends.json + history
```

Open http://127.0.0.1:8080/index.html

Optional: set `GITHUB_TOKEN` (or keep `gh auth token` available) for higher API limits.

## Scoring

`momentum 0–40 (7d star delta)` + `activity 0–25 (push recency, forks, issues)`
+ `fit 0–25 (curated 0–10 × 2.5, default neutral 5.0)` + `docs 0–10 (license, description)`.

Auto-generated; not endorsements. See [methodology](methodology.html).

## Nightly job

`.github/workflows/daily.yml` runs `scripts/fetch_trends.py`, commits changed data,
and redeploys Pages. Safe to trigger manually via `workflow_dispatch`.
