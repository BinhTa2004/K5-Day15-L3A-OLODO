# Reflection — Nguyễn Tuấn Dũng

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Tôi phụ trách hoàn thiện thẻ dữ liệu [`data/DATA_CARD.md`](../data/DATA_CARD.md), xây dựng 3 persona người mua từ số liệu thật cùng bảng giá 3 model trong [`cost/personas.yaml`](../cost/personas.yaml), chạy và phân tích 50 phiên mô phỏng thật tại [`cost/simulate-1.csv`](../cost/simulate-1.csv) và [`cost/cost-estimate.md`](../cost/cost-estimate.md) (`bf6c941`, `663ce15`). Đồng thời tôi chịu trách nhiệm lập dàn ý [`slides/outline.md`](../slides/outline.md), hoàn thiện bộ slide 8 trang [`demo-slides.pdf`](../demo-slides.pdf) kèm bản trình chiếu HTML tương tác [`slides/demo-slides.html`](../slides/demo-slides.html), và thuyết trình Trang 6–8 (Chi phí, Kết luận GO và Kế hoạch 1 tuần).

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Tôi dùng coding agent để tạo script dựng layout HTML/CSS phẳng đồng bộ với Web UI và kiểm định dạng bảng số liệu chi phí cho 3 kịch bản `15k / 50k / 200k` người dùng. Quá trình làm phải sửa lại khá nhiều sản phẩm của AI: bản slide nháp đầu tiên bị khoảng trắng lớn ở giữa trang và xuống dòng xấu ở cột tiền `₫)`, nên tôi yêu cầu chuyển sang bố cục `flex` đều tay, bỏ toàn bộ gradient/đổ bóng, sửa dòng Slide 1 theo đúng mạch "Vấn đề → Đào Data & Evidence → Pain Point", và tự đối chiếu thủ công từng con số giá token với tài liệu bảng giá K5 (ngày 25/11/2026) để bảo đảm không có con số nào không truy được về file gốc.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   Tôi chú ý nhất lỗi ở câu `D10` (`ORD-003` nồi chiên 450.000đ) ở Lượt 1 khi thiếu giải thích vỏ 6L / lòng 5L, và ngay cả khi Lượt 3 đạt `25/25` vẫn còn lỗi gõ nhầm dấu `260 000 đ > 300 000 đ` ở câu `D15`. Từ đó tôi học được hai điều thực tế khi tính bài toán kinh tế sản phẩm AI: thứ nhất, luôn phải chia chi phí mỗi phiên cho tỉ lệ đạt thật của Lượt 2 (`96%`) thay vì giả định lý tưởng `100%` (ra `$0.00081 ≈ 20 ₫/task`); thứ hai, khi Workflow cố định đã dùng code Python kiểm quy tắc cứng thì chỉ cần model tầng nhỏ (`gpt-4o-mini`, rẻ gấp `11,6×` tầng lớn) là đã đạt hiệu quả kinh tế cực tốt (`11 ₫/người/tháng`).
