# Reflection — Hoàng Hải Long

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
   Tôi phụ trách thu thập Nguồn bằng chứng thứ 2 qua khảo sát ẩn danh ngoài nhóm (`n = 32` người mua Shopee/TikTok, 0 PII) tại [`evidence/survey/questions.md`](../evidence/survey/questions.md) và [`evidence/survey/results.csv`](../evidence/survey/results.csv), cùng nhóm tổng hợp đối chiếu 2 nguồn và 7 trích dẫn nguyên văn trong [`evidence/summary.md`](../evidence/summary.md). Về đánh giá, tôi thiết kế và mở rộng bộ [`eval/benchmark.csv`](../eval/benchmark.csv) từ 15 lên 25 câu (`b70d863`, với `15/25 = 60%` câu từ `data_that` và `nguoi_dung`), chốt 4 metric trong [`eval/metric_spec.yaml`](../eval/metric_spec.yaml), chấm chéo độc lập `D01–D05` khớp `5/5` ở [`eval/README.md`](../eval/README.md) và hoàn thiện [`eval/report.md`](../eval/report.md). Khi thuyết trình, tôi phụ trách Trang 1–2 về Pain & Impact chọn Track D3.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
   Tôi dùng coding agent để rà câu chữ trung lập cho 11 câu Google Form (tránh câu hỏi dẫn dắt kiểu "bạn có muốn dùng AI không"), chuẩn hoá 6 cột CSV cho đúng `python run.py check` và hỗ trợ viết script kiểm nhanh từ khoá `eval/code_grader.py`. Tuy vậy toàn bộ phản hồi khảo sát đều do tôi tự phát và lọc từ người mua thật, xoá sạch file Excel thô có dấu vết thừa trước khi commit CP3 (`3e63c34`), và tự đọc chấm thủ công từng output ở `run-1..3.csv` vì bản thân nhận ra `code_grader.py` chỉ khớp `7/10` câu diễn đạt tự nhiên nên không thể giao hoàn toàn cho máy chấm thay.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
   Bên cạnh câu `D18` bị trả lời hoàn toàn bằng tiếng Anh ở Lượt 1, tôi ấn tượng nhất là ca hồi quy ở câu `D21` (đơn hộp trà bị móp vỡ khi vận chuyển) sang Lượt 2: khi nhóm siết luật bảo vệ người bán khỏi hoàn oan, model lại hiểu nhầm và viết thừa *"shop không chịu trách nhiệm khi lỗi vận chuyển"*, khiến `D21` tụt `1 → 0` dù tổng điểm Lượt 2 đã lên `96%`. Bài học lớn nhất tôi rút ra là "sửa chỗ này làm vỡ chỗ kia" hoàn toàn có thật khi chỉnh prompt, nên tuyệt đối không bao giờ chấm lại mỗi câu lỗi cũ mà luôn phải chạy trọn bộ 25 câu cho mọi vòng cải tiến.
