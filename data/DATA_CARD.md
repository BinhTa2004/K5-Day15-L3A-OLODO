# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Repo công khai chỉ chứa số tổng hợp và dữ liệu giả lập sạch (không PII, không commit bảng gốc).

## Dataset 1 · `vietnam_ecommerce` (dùng đào bằng chứng & thiết kế phân phối)

| | |
|---|---|
| Dùng để làm gì | Đào bằng chứng pain (R1), tính Impact (R2), trích nguyên văn lý do hoàn thật cho ≥1/3 bộ câu thử `eval/benchmark.csv` (`data_that:`), lấy tần suất cho persona chi phí (R6) |
| Từ đâu | Bộ công khai trên Xóm Dataset (`https://dataset.xomdata.com/datasets/schema/vietnam_ecommerce`), gồm `shopee_orders` và `tiktok_orders` |
| Xử lý những bước gì | Lọc bỏ toàn bộ cột PII (`buyer_name`, `recipient_name`, `phone`, `recipient_phone`, `full_address`, `buyer_username`); chỉ chạy truy vấn tổng hợp đếm ở cấp dòng hàng (`row`) vì `order_sn`/`order_id` đã bị che bằng `*` (script: [`evidence/count_xomdata.sql`](../evidence/count_xomdata.sql)) |
| Số dòng / số đoạn | 127.546 dòng (25.546 dòng Shopee · 102.000 dòng TikTok Shop) — **không commit file gốc vào repo** |
| Phiên bản / ngày lấy | Dữ liệu đơn từ 31/10/2025 → 09/09/2026; truy vấn ngày 27/11/2026 |
| Nhãn | `thật` (đơn hàng đa gian hàng Việt Nam) |
| Giới hạn | Thiếu nội dung chat/ghi chú khách (`buyer_remark`, `buyer_message` đều 0 dòng), không có ảnh/video mở hộp và không có mô tả sản phẩm tại thời điểm đặt |

## Dataset 2 · `data/orders.json` & `data/policies.json` (dùng chạy thử & eval)

| | |
|---|---|
| Dùng để làm gì | Nguồn dữ liệu nền cho các công cụ `get_order`, `get_listing_at_order`, `get_policy`, `get_complaint_history`, `check_return_rules` trong [`codebase/tools.py`](../codebase/tools.py) và chạy [`eval/benchmark.csv`](../eval/benchmark.csv) |
| Từ đâu | Nhóm tự sinh có seed (`synthetic`, `seed=42`) bằng script [`data/generate_data.py`](generate_data.py) dựa trên các nhóm lý do trả hàng thật từ `vietnam_ecommerce` và chính sách trả hàng công khai của Shopee (15 ngày, kiểm 11/11/2026 trong tài liệu Track D) / TikTok Shop (6 ngày đổi ý shop thường, 15 ngày lỗi/Mall) |
| Xử lý những bước gì | Sinh deterministically theo `SEED = 42`; mã hoá toàn bộ ID dạng giả lập (`ORD-001`..`ORD-016`, `BUYER-01`..`BUYER-12`, `SHOP-01`..`SHOP-06`), hoàn toàn không chứa thông tin cá nhân thật |
| Số dòng / số đoạn | 16 đơn hàng mẫu trong `orders.json` + quy tắc 2 sàn trong `policies.json` |
| Phiên bản / ngày lấy | v1.0 · ngày tạo 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Chỉ mô phỏng lát cắt xử lý sau giao (không chứa luồng vận chuyển realtime hay ảnh thật — phần ảnh/video mở hộp đại diện bằng trường `evidence_status`) |

**Lưu ý kiểm định `synthetic`:** Toàn bộ 16 đơn hàng trong `data/orders.json` được sinh bởi `data/generate_data.py` với `SEED = 42`, đã được Tạ Công Bình và Đào Quang Huy kiểm tra thủ công đủ 16/16 dòng để đảm bảo phủ cả 4 lớp chỗ khó (nguồn sự thật / shop sửa mô tả lúc đặt, thiếu bằng chứng, quá hạn/ngoài thẩm quyền, serial returner/nghi hàng giả). **Dữ liệu tự dựng này không dùng làm bằng chứng pain.**
