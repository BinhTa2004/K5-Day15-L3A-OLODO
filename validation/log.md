# Người dùng thử *(bonus)*

> Điền ở guide bước 4.3 — 2–3 người ngoài nhóm, ~10 phút / người, theo 5 nhịp: làm quen · bối cảnh · giao việc · quan sát · hỏi sau. Ôn lại: ngày 5, ngày 13. Chấm ở rubric Bonus.
> Không ghi tên: ghi vai. Hành vi quan sát được nặng hơn lời nói; toàn lời khen = phiên chưa đạt, giao việc khó hơn.
> Người dùng thử **không thay được** bằng chứng pain ở `evidence/`.

| Người thử (vai) | Việc giao (theo kết quả, không theo nút) | Quan sát (làm gì đầu tiên, chỗ do dự, chỗ hiểu sai) | Trích nguyên văn | Mức nghiêm trọng (cao / vừa / thấp) |
|---|---|---|---|---|
| Người đánh giá / học viên ngoài nhóm tại buổi Demo (ẩn danh) | Dùng thử trực tiếp Web UI với các tình huống mẫu đa dạng (ca thường, shop sửa mô tả, hoàn lặp, tấn công PII, đơn lạ) và rà kiến trúc | Thao tác trôi chảy trên Web UI 2 góc nhìn, kiểm tra các case chính và xác nhận luồng xử lý chạy ổn, chưa phát sinh lỗi chặn. | `"khá ổn về kiến trúc và xử lý được các case"` | thấp |

Câu hỏi sau: *"Nếu mai không được dùng nữa, bạn thấy: rất tiếc / hơi tiếc / không sao?"* → chưa thu số đếm rất tiếc / hơi tiếc / không sao (ghi nhận nhận xét trực tiếp tại buổi review; hiện có 1 lượt review nên nhóm tự khai chưa đủ ngưỡng ≥2 người của mục Bonus).

## Tổng hợp

- Chủ đề lặp nhiều nhất: Kiến trúc Workflow 5 bước và cách phân tuyến rõ ràng các tình huống biên (shop sửa mô tả, hoàn lặp, tấn công PII, vượt 300.000đ, thiếu mã đơn `G10`) chạy ổn định trên giao diện Web UI 2 góc nhìn.
- Sửa gì trước demo (ghi `spec.md` §10): Đã hoàn tất trước đó việc chia 3 nhóm tình huống mẫu + Bảng Rủi ro Shop trên `web_ui.py` và vá ranh giới từ regex `"áo khoác"` / `"khoá"` (`b5a7c0e`).
- Giữ gì và vì sao: Giữ nguyên kiến trúc Workflow cố định 5 bước + 2 lớp chặn bằng code (`check_return_rules` và `_sanitize_and_verify`), vì đáp ứng đúng trọng tâm kiểm thử và được đánh giá ổn về kiến trúc lẫn khả năng xử lý các case.
- Để dành sau: Ghi nhận đầy đủ phản hồi 5 nhịp của ≥2 người dùng thật theo biểu mẫu đầy đủ và xử lý lỗi gõ nhẹ ở `D15` + chuẩn hoá từ khoá `code_grader.py` (`eval/report.md` §4).
