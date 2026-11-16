# Agent Signal — schema chuẩn (đối chiếu với đề xuất của ChatGPT)

Cập nhật: 2026-11-16. Nguồn đối chiếu: `cache/scratch/gpt_fit.json` (ChatGPT đề xuất cấu trúc
`fit_scores` với `schema_version` / `fit_status` / `score_0_10` / `fit_note_en` / `reason`).

## 1. `config/fit_scores.yaml` — curator nhập tay

```yaml
fit_scores:
  <owner/repo>:
    score: <0-10>      # điểm fit do người curate chấm (Hermes + chủ nhân)
    why:   "<1 dòng>"  # lý do, dịch sang fit_note ở dữ liệu đầu ra
```

Ngưỡng: `>=8` cài được ngay; `5-7` cần verify/kế hoạch; `<5` chỉ theo dõi.
Chưa curate → không khai báo; pipeline dùng mặc định `score=5.0` và `fit_status=not_curated_yet`.

## 2. `data/trends.json` — đầu ra cho UI

Mỗi repo có: `blurb`, `fit` (0-10), `fit_curated` (bool), `fit_note`, `score` (0-100),
`score_parts {momentum, activity, fit, docs}`, `curated`, `delta_7d`.

## 3. Ánh xạ sang đề xuất của ChatGPT

| ChatGPT (`gpt_fit.json`) | Agent Signal (hiện hành) | Ghi chú |
|---|---|---|
| `schema_version: 1` | — (ngầm 1) | đã thống nhất |
| `defaults.score_0_10: 5` | `fit=5.0`, `curated=false` | cùng ngữ nghĩa |
| `defaults.fit_status: not_curated_yet` | `fit_note` mặc định "Not curated yet…" | cùng ngữ nghĩa |
| `repos.<x>.score_0_10` | `config.score` → `trends.fit` + `score_parts.fit` | **khác thang**: GPT dùng 0-10; `trends.score` là 0-100 (tổng) |
| `repos.<x>.reason` | `config.why` | cùng ngữ nghĩa |
| `repos.<x>.fit_note_en` | `trends.fit_note` | cùng ngữ nghĩa |

**Kết luận đối chiếu:** hai bên tương thích về ngữ nghĩa; khác nhau ở tên trường và thang điểm.
`score` 0-100 là phép cộng có trọng số (xem `methodology.html`), không phải điểm curator — giữ
nguyên vì UI và `main.js` đang dùng. Không cần migrate dữ liệu.

## 4. Công thức (cố định)

`score = momentum(0-40) + activity(0-25) + fit(0-25) + docs(0-10)`
- momentum: sao/ngày từ `data/history.json` (thiếu → `null`, không đoán)
- activity: độ mới `pushed_at`, forks, số issue mở
- fit: `curator 0-10 × 2.5` (mặc định 12.5)
- docs: README + license + mô tả

## 5. Kiểm chứng (chạy thật 2026-11-16)

- 46 entry (44 repo duy nhất — `anthropics/skills` và `NousResearch/hermes-agent` xuất hiện ở 2 category) có đủ `fit_note`, `score`, `score_parts`.
- 9 entry được curate (`fit` 5,0–10,0) = 7 repo duy nhất; 36 entry giữ note mặc định
  `Not curated yet…`, gồm 34 entry chưa curate + 2 entry curated chưa chấm — hợp lệ theo mục 1.
- 3 repo chưa curate nhưng đã ghi note: `addyosmani/agent-skills`, `thedotmack/claude-mem`, `mem0ai/mem0`.
- `curated=true` mà vẫn giữ note mặc định: `0xNyk/awesome-hermes-agent`, `openai/skills`.
- `score_parts.fit == fit × 2.5` (lệch chỉ do làm tròn 1 chữ số thập phân).
- `delta_7d` đang `null` cho cả 46 entry vì `history.json` mới có 3 snapshot (14–16/11), chưa đủ 7 ngày — hợp lệ, không bịa.
