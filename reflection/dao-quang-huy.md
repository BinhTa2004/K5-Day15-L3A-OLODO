# Reflection — Đào Quang Huy

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Tôi phụ trách phần đào dữ liệu thực tế `vietnam_ecommerce` (`127.546` dòng trên Xóm Dataset qua [`evidence/count_xomdata.sql`](../evidence/count_xomdata.sql) và [`evidence/data-mining.md`](../evidence/data-mining.md)), sinh tập dữ liệu giả lập sạch có seed tại [`data/generate_data.py`](../data/generate_data.py) (`16` đơn trong `orders.json` và `policies.json`), cài đặt `6` công cụ `@tool` không phụ thuộc `issue_hint` ở [`codebase/tools.py`](../codebase/tools.py) và dựng giao diện Web UI phẳng 2 góc nhìn tại [`codebase/web_ui.py`](../codebase/web_ui.py) (`2072e69`, `663ce15`). Ngoài ra, tôi tham gia thao tác demo trực tiếp và trình bày Trang 5 về kết quả đánh giá 3 lượt trên 25 câu thử.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Tôi dùng coding agent để gợi ý nhanh cấu trúc câu lệnh T-SQL tổng hợp không PII và khung HTML/CSS/JS cho Web UI `threading.HTTPServer`. Khi chạy SQL thật trên hai bảng `shopee_orders` và `tiktok_orders`, tôi phát hiện cột `order_sn`/`order_id` bị che bằng dấu `*` nên nếu `GROUP BY` theo AI gợi ý ban đầu sẽ sai mẫu số (`35`/`386`), buộc phải sửa toàn bộ truy vấn sang đếm cấp dòng (`row`) và kiểm tay khớp `100%` từng con số `x/N`. Ở Web UI, tôi cũng trực tiếp sửa lỗi ghép chuỗi lặp `"Đơn Đơn ORD-..."` khi bấm đổi đơn nhanh, bổ sung bộ lọc sàn và làm Bảng phân tích Rủi ro Shop từ số liệu `127K` dòng.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   Ở Lượt 1, câu `D09` (đơn `ORD-004` shop đã sửa mô tả áo sơ mi từ `100% cotton` sang vải pha polyester) bị trượt nặng vì model tự suy diễn theo mô tả mới sửa và bịa thêm mức phạt `20% + 2%`, đồng thời câu `D10` không trích chi tiết dung tích vỏ 6L vs lòng 5L. Tôi học được rằng dù LLM có mạnh tới đâu, nếu công cụ tra cứu không tách bạch rạch ròi `listing_at_order` khỏi `listing_current` hoặc còn lẫn trường gợi ý `issue_hint`, AI rất dễ chọn sai nguồn sự thật; chất lượng dữ liệu đầu vào và hợp đồng công cụ chỉ đọc quyết định trực tiếp độ trung thực của sản phẩm.
