# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Coding agent (Claude / Antigravity) | Hỗ trợ sinh khung workflow (`codebase/agent.py`), 6 công cụ (`tools.py`), kết nối đa hãng (`ai.py`) và giao diện Web UI 2 tab (`web_ui.py`) | Chạy thử CLI & Web UI trên cả 16 đơn, sửa lỗi lặp `"Đơn Đơn"`, bỏ phụ thuộc `issue_hint`, kiểm rào chắn PII/hạn mức | Tạ Công Bình, Đào Quang Huy |
| Prompt / thiết kế lời gọi mô hình | Coding agent | Gợi ý cấu trúc `SYSTEM` prompt, ánh xạ nhãn tiếng Việt và quy tắc bảo vệ lỗi vận chuyển / hạn đổi ý | Chạy kiểm 3 lượt eval thật (`20/25 → 24/25 → 25/25`), đọc đối chiếu từng câu đầu ra (`eval/report.md`) | Tạ Công Bình |
| Đào data (viết script đếm, gợi ý nhãn) | Coding agent | Hỗ trợ viết câu lệnh T-SQL tổng hợp không PII (`evidence/count_xomdata.sql`) theo 2 bảng `vietnam_ecommerce` | Chạy trực tiếp trên SQL Server Xóm Dataset (`127.546` dòng), phát hiện lỗi mask `order_sn`/`order_id`, kiểm tay khớp `100%` toàn bộ số `x/N` | Đào Quang Huy |
| Rà câu hỏi phỏng vấn / khảo sát | Coding agent | Chỉ rà câu dẫn dắt và tính trung lập cho bộ 11 câu (`evidence/survey/questions.md`), không thu thập PII | Tự phát Form Google cho học viên ngoài nhóm (`n=32`), xuất CSV sạch (`results.csv`), lọc bỏ file thô và trích nguyên văn thật | Hoàng Hải Long |
| Viết câu thử (benchmark) | Coding agent | Gợi ý phân nhóm 4 lớp chỗ khó & chuẩn hoá định dạng 6 cột CSV | Tự chọn lọc 25 câu (`15/25 = 60%` từ `data_that` & `nguoi_dung`, 10 `tu_viet`, 0 bịa), kiểm `python run.py check` đạt 0 cảnh báo | Hoàng Hải Long, Tạ Công Bình |
| Sinh data `synthetic` (nếu có) | Coding agent | Hỗ trợ viết `data/generate_data.py` sinh dữ liệu đơn hàng & chính sách bám phân phối thật | Seed `42` · kiểm tay 16/16 đơn mẫu trong `data/orders.json` (0 PII) và hạn sàn Shopee 15d / TikTok 6d–15d trong `data/policies.json` | Đào Quang Huy, Nguyễn Tuấn Dũng |
| Chấm cột `pass` bằng LLM (nếu có) | **Không dùng LLM chấm thay** (chỉ dùng `eval/code_grader.py` bằng Python regex/keyword để hỗ trợ quét PII & từ khoá) | Tự động kiểm 0% SĐT và từ khoá từ chối/chuyển nhân viên | Kiểm tra thủ công `25/25` câu thử cả 3 lượt (`run-1..3.csv`); Hoàng Hải Long chấm chéo độc lập `5/5` câu đầu Lượt 1, khớp `5/5` | Tạ Công Bình, Hoàng Hải Long |
| Slide, văn bản | Coding agent | Hỗ trợ soạn khung trình bày HTML/PDF (`demo-slides.pdf`) và định dạng `cost-estimate.md`, `eval/report.md` | Kiểm từng con số & trích dẫn trên 8/8 trang slide truy về đúng file gốc trong repo; tự điều chỉnh lời nói & phân công demo | Nguyễn Tuấn Dũng, cả nhóm |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
