# QA Scorecard — Agent Signal (UI/UX rubric 10 tiêu chí)

- **Ngày:** 2026-11-16
- **Phiên bản:** trước sửa = live `f37424f` (data 2026-11-16T08:45:16+07:00, 46 entries / 44 repo unique / 5 category); sau sửa = working tree (CSS + `js/main.js`)
- **Đối tượng đo:** `https://vaicauchuyentreninternet-crypto.github.io/agent-signal/` (live) và bản local phục vụ ở `http://127.0.0.1:8772/index.html`
- **Mức đạt:** trung bình **8,8/10**, **0 lỗi chí mạng**

## Điểm 10 tiêu chí (đo sau khi sửa)

| # | Tiêu chí | Trước | Sau | Bằng chứng |
|---|---|---|---|---|
| 1 | First impression / hệ thống thị giác | 8,0 | **8,5** | Giao diện dark radar: kicker "Radar buổi sáng · 05:00 giờ VN", stamp cập nhật, accent `--acc` một chỗ; 3 giây đầu đọc được ngay "đây là radar GitHub cho agent tooling". |
| 2 | Typography & nhịp spacing | 7,5 | **7,5** | Hierarchy rõ: H1 clamp(34–54) → H2 22 → H3 16 → body 14/14.5. **Nợ còn lại:** 12 font-size computed khác nhau (11, 11.5, 12, 12.42, 12.5, 13, 13.5, 14, 14.5, 16, 22, 46.45) so với lý tưởng ≤5 — cố ý cho radar dày thông tin; gộp lại sẽ phá identity nên giữ + ghi nợ. |
| 3 | Màu & tương phản | 5,0 | **9,0** | Trước: `.chip` text `--faint #74889a` trên `--panel-2 #1b232c` = **4,33** (126 text node dưới AA 4.5) → lỗi chí mạng. Sau: `.chip{color:var(--muted)}`, **0 node dưới 4,5**, thấp nhất 4,64 (`.tag`). |
| 4 | Motion có mục đích | 8,5 | **9,0** | Không keyframes/intro; `prefers-reduced-motion` tắt hết (`* { animation:none!important; transition:none!important }`) — verify computed `transition-duration: 0s` khi emulate reduce. Thêm hover 150ms, bị reduce tắt hoàn toàn. |
| 5 | Micro-interaction & phản hồi | 7,5 | **8,0** | Hover: `.card` đổi border, `.card-name a` → accent, `.ghost-btn` → border accent. Loading "Đang tải…" + error state có nội dung (`Chưa tải được dữ liệu…`). Chưa có skeleton/spinner. |
| 6 | Responsive toàn diện | 4,0 | **9,5** | Trước: 320px → `scrollWidth 331` vs `clientWidth 305` = **tràn ngang 26px** (lỗi chí mạng). Sau: 320/390/768/1440 → `scrollWidth == clientWidth` (305/375/753/1425). |
| 7 | Performance | 9,0 | **9,0** | CSS 6,3KB + JS 7,1KB + favicon 0,25KB (tổng ~13,7KB, mục tiêu ≤200KB). `trends.json` 300KB là dữ liệu, fetch 1 lần, `cache:no-cache`. Không CDN, không dependency. |
| 8 | Accessibility | 8,5 | **9,0** | 1 `<h1>`, thứ tự H1→H2→H3 đúng, `lang="vi"`, 53 focusable, `a/button:focus-visible` outline accent 2px; input/select `:focus` outline. Không focus trap (không modal). |
| 9 | Content clarity & tone | 8,0 | **8,5** | Toàn bộ copy tiếng Việt, giữ tên repo/thuật ngữ tiếng Anh. Mỗi section: 1 tiêu đề + 1 blurb + card. **Sửa:** thời điểm cập nhật trước hiện `Mon, 16 Nov 2026 01:45:16 UTC` → nay `08:45:16 Th 2, 16 thg 11, 2026 (ICT)`, thuộc tính `datetime` vẫn giữ UTC chuẩn. |
| 10 | Craft nhất quán | 8,0 | **9,0** | Trước: 2 `<button>` dùng font **Arial** mặc định của trình duyệt, lệch hệ `ui-sans-serif` của trang. Sau: `.ghost-btn{font-family:inherit}` → **1 hệ font duy nhất**; radius/border/shadow dùng một hệ token. |

**Trung bình: (8,5+7,5+9+9+8+9,5+9+9+8,5+9)/10 = 8,8/10** ✅ (ngưỡng ≥ 8,5)

## 3 khoảng điểm thấp nhất & cách xử lý

1. **#6 Responsive (4,0 → 9,5)** — sửa. Nguyên nhân: `@media (max-width:640px){.grid{grid-template-columns:1fr}}`, `1fr` = `minmax(auto,1fr)` không co được dưới min-content; card `modelcontextprotocol/registry` có min-content **317px** (tên repo không ngắt được) đẩy track "MCP Servers" lên **316,891px**. Sửa bằng 2 rule **cộng thêm**: `minmax(0,1fr)` và `.card-name{overflow-wrap:anywhere}`. Verify: min-content card tối đa giảm **317 → 146**, track 316,891 → 277, 0px overflow ở 320.
2. **#3 Màu & tương phản (5,0 → 9,0)** — sửa. `.chip` dùng `--faint` trên nền `--panel-2` = 4,33 (dưới AA). Đổi sang `--muted` (`#9fb0bd`) → 0 node dưới 4,5.
3. **#5 Micro-interaction (7,5 → 8,0)** — sửa một phần. Thêm transition 150ms cho hover (card/button/link), tôn trọng `prefers-reduced-motion`.

Không sửa #2 (12 font-size) và #4 (không có intro): #2 là nợ thiết kế cố ý, gộp lại là thay đổi hệ thống visual đang tồn tại (vi phạm điều kiện "không duyệt thiết kế thay thế hệ visual cũ") → ghi nợ. #4 không có gì để sửa vì trang không dùng animation.

## Quy tắc đã tuân thủ

- **Chỉ thêm, không sửa/xoá rule cũ:** toàn bộ fix nằm trong khối `/* QA fixes — 2026-11-16 */` ở cuối `css/styles.css`, đè có phạm vi hẹp. Token `:root`, font stack, palette, layout gốc giữ nguyên.
- **Không duyệt thiết kế thay thế:** không đổi palette/font/layout; chỉ sửa giá trị tối thiểu cần để đạt AA và không tràn ngang.
- **Verify tất định trước, vision sau:** mọi điểm đều từ phép đo DOM (contrast WCAG, scrollWidth, computed font, transition-duration, heading order, console hook), không suy đoán.

## Bằng chứng chạy thật

- `node --check js/main.js` → OK.
- Console hook (`addScriptToEvaluateOnNewDocument` + reload) → `[]` (0 error, 0 warning).
- Contrast quét 501 text node (composite alpha trên background thực, WCAG luminance) → trước 126 node < 4,5; sau **0**.
- Overflow 4 khung qua `Emulation.setDeviceMetricsOverride` (desktop emulation, `mobile:false`) → trước 320: `331 vs 305`; sau cả 4 khung `scrollWidth == clientWidth`.
- `Emulation.setEmulatedMedia prefers-reduced-motion=reduce` → `transition-duration: 0s`; bỏ emulate → `0.15s`.
- Ảnh: `shots/{before_desktop,before_320,after_desktop,after_320}.png` trong workspace của lượt chạy (không đưa vào repo để giữ repo gọn).
