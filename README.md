# Agent Signal

Radar buổi sáng về công cụ GitHub cho AI agent — tự động làm mới **05:00 giờ VN** (22:00 UTC)
bằng GitHub Actions và đưa lên GitHub Pages.

Các mục: Agent Skills · Agent Frameworks · Context & Memory · MCP Servers · Hermes Ecosystem.

Mỗi repo có:
- sao trực tiếp + delta 7 ngày (từ snapshot trong `data/history.json`)
- điểm tự động 0–100 kèm công thức minh bạch
- ghi chú "Vì sao phù hợp" khi repo được curate trong `config/fit_scores.yaml`

## Chạy cục bộ

```bash
python3 -m http.server 8080 --bind 127.0.0.1   # từ thư mục này
python3 scripts/fetch_trends.py                # ghi data/trends.json + history
```

Mở http://127.0.0.1:8080/index.html

Tùy chọn: đặt `GITHUB_TOKEN` (hoặc giữ `gh auth token`) để API limit cao hơn.

## Đường lệnh cho Hermes (inbox)

Trang chủ có ô **“＋ Lệnh cho Hermes”**: bạn nhập repo/tool + hành động + chi tiết.
Hai cách gửi:
1. **Tạo GitHub Issue** — nút mở sẵn form issue của repo `agent-signal` với nội dung đã điền.
   Hermes quét issue nhãn `hermes-command` mỗi sáng, tải repo về cài đặt/tích hợp,
   rồi gửi kết quả + bản ghi cho ChatGPT để cập nhật nguồn dữ liệu của nó.
2. **Copy lệnh** — dán thẳng vào chat Discord cho Hermes nếu bạn đang ngồi máy.

## Cách chấm điểm

`momentum 0–40 (delta 7 ngày)` + `activity 0–25 (độ mới, forks, issues)`
+ `fit 0–25 (curator 0–10 × 2.5, mặc định 5.0)` + `docs 0–10 (license, mô tả)`.

Tự động sinh; không phải lời cậy nhận. Xem [phương pháp](methodology.html).

## Job mỗi đêm

`.github/workflows/daily.yml` chạy `scripts/fetch_trends.py`, commit data nếu đổi,
Pages tự deploy từ nhánh `main`. Chạy tay được qua `workflow_dispatch`.
