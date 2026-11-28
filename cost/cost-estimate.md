# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Chấm ở rubric R6.
> Toàn bộ số liệu bên dưới được chạy mô phỏng thật từ `cost/personas.yaml` qua `python run.py simulate --rate-from eval/run-2.csv` và chép nguyên từ [`cost/simulate-1-summary.md`](simulate-1-summary.md).

## 1. Đầu vào

- **Persona ([`cost/personas.yaml`](personas.yaml)):** 3 kiểu người mua trên Shopee & TikTok Shop (tổng `share = 1.00`):
  1. `mua_it` (`share: 0.59` · `0,15 phiên/tháng` · `1 lượt/phiên` · `types: [thuong]`): nguồn khảo sát `evidence/survey/results.csv` (`n=32`, Q2: 59,4% đặt `<3` đơn/tháng; Q4: nhóm ít sự cố `~0,15` ca/tháng; số lượt/phiên *tự ước tính*).
  2. `mua_thuong_xuyen` (`share: 0.35` · `0,54 phiên/tháng` · `2 lượt/phiên` · `types: [thuong, kho]`): nguồn `evidence/survey/results.csv` (`n=32`, Q2: 37,5% đặt `3–10` đơn/tháng; Q4: nhóm từng gặp sự cố TB `0,54` lần/tháng; số lượt/phiên *tự ước tính*).
  3. `hoan_lap_lai` (`share: 0.06` · `1,8 phiên/tháng` · `3 lượt/phiên` · `types: [kho, tu_choi]`): nguồn `evidence/data-mining.md` (`vietnam_ecommerce`: `262/14.513 = 1,81%` khách Shopee hoàn `>= 2` lần tạo `45,63%` ca hoàn, tối đa 9 lần) + khảo sát Q4 (`21,9%` gặp `>= 2` lần/3 tháng); số lượt/phiên *tự ước tính*.
- **Số người dùng thật (3 kịch bản):** **thấp `15.000`** · **cơ sở `50.000`** · **cao `200.000`**.
  - *Nguồn:* `https://dataset.xomdata.com/datasets/schema/vietnam_ecommerce` (xem 27/11/2026) — riêng 10 gian hàng Shopee trong mẫu `vietnam_ecommerce` đã có **`14.513` người mua duy nhất** (`evidence/data-mining.md`); lấy `15.000` người (~quy mô ~10 shop) cho kịch bản thấp, `50.000` người (~35 shop, *tự ước tính*) cho kịch bản cơ sở và `200.000` người (~140 shop, *tự ước tính*) cho kịch bản cao.
- **Giá ≥ 2 mức model (USD / 1M token, từ bảng giá chuẩn K5 `further-reading/model-prices.md`, kiểm 25/11/2026):**
  - **`gpt-4o-mini`** *(tầng Nhỏ)*: vào `$0.15` · ra `$0.60` (`https://developers.openai.com/api/docs/pricing` · xem 25/11/2026)
  - **`gemini-3.1-flash-lite`** *(tầng Nhỏ)*: vào `$0.25` · ra `$1.50` (`https://ai.google.dev/gemini-api/docs/pricing` · xem 25/11/2026)
  - **`gemini-4-hydrogen`** *(tầng Lớn)*: vào `$1.50` · ra `$7.50` (`https://ai.google.dev/gemini-api/docs/pricing` · xem 25/11/2026)
  - *Tỷ giá quy đổi tham chiếu:* `1 USD = 25.400 ₫` *(tự ước tính tham chiếu 28/11/2026)*.
- **Tỉ lệ đạt dùng để tính:** **`24/25 (96%)`** — lượt `run-2@20261128-100823` (`--rate-from eval/run-2.csv`, dùng đúng tỉ lệ đạt thật của lượt 2 theo rubric R6, không lấy `100%`; *ghi chú: ở lượt 3 bổ sung `run-3@20261128-103212` sau đó nhóm đạt `25/25 = 100%`*).
- **Ghi chú tách token:** **Đo token thật trên model `gpt-oss:20b` (Ollama Cloud), tính giá theo `gpt-4o-mini`, `gemini-3.1-flash-lite` và `gemini-4-hydrogen`.** Model khác bộ tách token thì số token thực tế có thể chênh lệch nhẹ.

## 2. Kết quả mô phỏng

Lượt mô phỏng: [`cost/simulate-1.csv`](simulate-1.csv) · Run ID: **`simulate-1@20261128-104631`** · **`50` phiên (`0/50` lỗi)** · `seed = 42` · trace `traces/simulate-1.jsonl`.

**Token đo thật theo từng persona:**

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| `mua_it` | 31 | 1 | 1.321 | 632 | 1,0 | 5,0 |
| `mua_thuong_xuyen` | 18 | 2 | 2.604 | 1.137 | 2,0 | 9,7 |
| `hoan_lap_lai` | 1 | 3 | 4.068 | 1.496 | 3,0 | 16,0 |

**Chi phí theo 3 kịch bản quy mô & 3 mức giá model:**

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (15.000 người) | Chi phí / tháng — cơ sở (50.000 người) | Chi phí / tháng — cao (200.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` (vào 0.15 · ra 0.6 $/1M) | `$0.00077` (≈ 20 ₫) | `$0.00081` (≈ 20 ₫) | `$0.00058` (≈ 15 ₫) | `$6.25` (≈ 158.748 ₫) | `$20.83` (≈ 529.160 ₫) | `$83.33` (≈ 2.116.641 ₫) | **`$0.00042` (≈ 11 ₫)** |
| `gemini-3.1-flash-lite` (vào 0.25 · ra 1.5 $/1M) | `$0.0017` (≈ 43 ₫) | `$0.0018` (≈ 45 ₫) | `$0.0013` (≈ 32 ₫) | `$13.66` (≈ 346.941 ₫) | `$45.53` (≈ 1.156.469 ₫) | `$182.12` (≈ 4.625.877 ₫) | **`$0.00091` (≈ 23 ₫)** |
| `gemini-4-hydrogen` (vào 1.5 · ra 7.5 $/1M) | `$0.0090` (≈ 228 ₫) | `$0.0094` (≈ 238 ₫) | `$0.0067` (≈ 170 ₫) | `$72.23` (≈ 1.834.562 ₫) | `$240.76` (≈ 6.115.208 ₫) | `$963.02` (≈ 24.460.833 ₫) | **`$0.0048` (≈ 122 ₫)** |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ `0,96` (tỉ lệ đạt Lượt 2).

## 3. So với impact

- **Impact / người / tháng (`spec.md` §2):** Với 1 người mua gặp sự cố (`0,54` ca/tháng), tổng chi phí thời gian + rủi ro thiệt hại kỳ vọng là **`~34.000đ–61.000đ/người/tháng`** (`~5,8 phút` + `28%` rủi ro giữ hàng lỗi/từ bỏ); tính bình quân toàn tập người mua (nhiều mức độ từ `mua_it` đến `hoan_lap_lai`, TB ~`0,39` phiên/tháng) vẫn tương đương **`~20.000đ–36.000đ/người/tháng`** và bảo vệ dòng tiền tránh âm `escrow_amount` (`873/1.305` ca hoàn Shopee trong `vietnam_ecommerce`).
- **Chi phí / người / tháng (cơ sở, model khuyến nghị `gpt-4o-mini`):** **`$0.00042` (`≈ 11 ₫`/người/tháng)** — hay chỉ **`20 ₫`/task thành công** (`$0.00081`); ngay cả với model lớn `gemini-4-hydrogen` cũng chỉ **`122 ₫`/người/tháng**.
- **Kết luận một dòng — đáng làm không:** **RẤT ĐÁNG LÀM** — chi phí AI ở tầng nhỏ (`gpt-4o-mini`: `~11 ₫`/người/tháng, `529.160 ₫`/tháng cho `50.000` người dùng) chỉ bằng **< 0,1%** giá trị thời gian & rủi ro giữ hàng lỗi mà hệ thống giúp người mua và gian hàng tiết kiệm được (`~20.000đ–61.000đ`/người/tháng).

## 4. Phân tích sâu thêm

- **Bảng độ nhạy — các cần gạt giảm chi phí AI:**

| Cần gạt tối ưu | Tác động ước lượng lên chi phí | Lý do |
|---|---|---|
| Chọn model tầng Nhỏ (`gpt-4o-mini` thay vì `gemini-4-hydrogen`) | **Giảm ~11,6× chi phí** (`$240.76 → $20.83/tháng` cơ sở) | Luồng là **workflow cố định** (code Python đã làm hết bước tra đơn, tính hạn ngày & hạn mức 300k), AI chỉ cần soạn đối chiếu nên model nhỏ làm tốt. |
| Bật Prompt Caching cho `SYSTEM` prompt (~600 token vào lặp lại) | **Giảm ~35–45% tiền token vào** | `SYSTEM` prompt giữ nguyên 100% qua mọi phiên; giá cache của `gpt-4o-mini` chỉ bằng 50% (`$0.075` vs `$0.15/1M`), `gemini-3.1-flash-lite` giảm 90% (`$0.025/1M`). |
| Siết giới hạn trả lời `≤ 180` từ thay vì dài tự do | **Giảm ~20–25% token ra** | Token ra đắt gấp **4–6×** token vào; câu trả lời gọn rõ theo mẫu cố định vừa rẻ hơn vừa đỡ lỗi gõ từ. |
| Chặn sớm hoàn toàn bằng code với ca thiếu `ORD-XXX` / `not_found` | **Giảm ~15% số lần gọi model** | Tránh gọi LLM ở các lượt hỏi lại mã đơn đơn giản (`D07`, `D16`). |

- **Chi phí ngoài model (ước tính vận hành thực tế quy mô cơ sở `50.000` người):**
  - *Hosting backend Python + DB đơn hàng:* ~$10–$20/tháng (~250k–500k đ/tháng) do hệ thống stateless nhẹ, chỉ tra JSON/SQL.
  - *Giờ công nhân viên sàn duyệt phiếu chuyển `ESC-ORD-...`:* Chỉ những ca rủi ro cao (`>300k`, quá hạn, serial returner ≥3, nghi giả) mới tạo phiếu; các ca thường ≤300k được AI hướng dẫn trọn vẹn, giúp giảm tải trực tiếp cho CSKH mà không làm tăng chi phí duyệt thêm.
- **Quy mô nào thì bài toán còn đáng làm:** Ngay cả ở kịch bản nhỏ nhất (`15.000` người dùng, `158.748 ₫`/tháng tiền AI `gpt-4o-mini`) hay chỉ phục vụ riêng 1 cụm ~20 shop (`262` ca hoàn/tháng → **~5.240 ₫ tiền AI/tháng** để bảo vệ ~73,5 triệu GMV và ~2,78 triệu ship hoàn), bài toán đều hoàn vốn ngay lập tức.
