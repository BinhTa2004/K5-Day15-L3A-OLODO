# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Nộp PDF, không nộp link.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Vấn đề, Data &amp; Pain | Vấn đề thực tế → Đào Data `vietnam_ecommerce` (127K dòng) + Khảo sát (`n=32`) → Chốt Pain Point &amp; trích dẫn `S14, S18` | `evidence/summary.md`, `evidence/data-mining.md`, `evidence/survey/results.csv` | ☑ |
| 2 | Vì sao chọn bài này | Bảng Impact 3 hướng + 2 hướng bị loại kèm lý do từ data thật | `spec.md` §2 | ☑ |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ workflow 5 bước · AI tự làm đến đâu, vì sao & 4 việc KHÔNG làm | `spec.md` §4, `codebase/agent.py` | ☑ |
| 4 | Demo live | Ảnh giao diện 2 góc nhìn thật (`ORD-004` sửa mô tả & `ORD-008` bảo vệ shop) + ca thử lạ + link video dự phòng 33,7s | `codebase/web_ui.py`, `eval/benchmark.csv` | ☑ |
| 5 | **Đánh giá thế nào** | 25 câu (`60%` thật) · 4 metric (chấm chéo `5/5`) · Lượt 1 (`80%`) → Lượt 2 (`96%`) → Lượt 3 (`100%`) · lỗi chính | `eval/README.md`, `eval/report.md` | ☑ |
| 6 | **Chi phí khi dùng thật** | 50 phiên đo thật (`0/50` lỗi) · `gpt-4o-mini` `$0.00081` (≈ 20 ₫)/task · 3 kịch bản (`15k / 50k / 200k`) · `11 ₫` vs Impact `20k–61k đ` | `cost/cost-estimate.md`, `cost/simulate-1-summary.md` | ☑ |
| 7 | Kết luận | GO thí điểm — dẫn số trực tiếp từ Trang 1, 5, 6 & phạm vi triển khai an toàn | `spec.md`, `eval/report.md`, `cost/cost-estimate.md` | ☑ |
| 8 | Nếu có thêm 1 tuần | 3 nâng cấp tiếp theo trỏ về lỗi nhẹ còn lại (`D15`), tối ưu cache & phản hồi người thử ngoài nhóm | `eval/report.md` §4, `cost/cost-estimate.md` §4, `validation/log.md` | ☑ |

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh (`https://drive.google.com/file/d/11hyOe3ZUYoBXLiIFM1CGLK9BMURSqhC3/view?usp=drive_link`) · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần):

| Trang | Người nói |
|---|---|
| Trang 1–2 (Người dùng, Pain & Impact chọn lát cắt) | Hoàng Hải Long |
| Trang 3–4 (Kiến trúc Workflow cố định & Demo Live 2 góc nhìn) | Tạ Công Bình *(cùng Đào Quang Huy thao tác Web UI)* |
| Trang 5 (Đánh giá 25 câu & Lượt 1 → Lượt 2 → Lượt 3) | Đào Quang Huy |
| Trang 6–8 (Chi phí 50 phiên, Kết luận GO & Kế hoạch 1 tuần) | Nguyễn Tuấn Dũng |
