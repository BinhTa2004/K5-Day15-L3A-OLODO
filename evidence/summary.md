# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, hoàn tất trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1 (14 điểm).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---:|---|
| Đào data (`x/N`, `%`, script chạy lại được, ≥5 ví dụ) | ☑ Đạt | [`evidence/data-mining.md`](data-mining.md) · [`evidence/count_xomdata.sql`](count_xomdata.sql) |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ Không dùng | *(Thay bằng Khảo sát đạt ngưỡng `n=32` làm nguồn đối chứng thứ 2)* |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☑ Đạt (`n = 32`) | [`evidence/survey/results.csv`](survey/results.csv) · [`evidence/survey/questions.md`](survey/questions.md) |

---

## 2. Số chính

- **Đào data (`vietnam_ecommerce` — 127.546 dòng: 25.546 Shopee + 102.000 TikTok Shop):**
  - Tổng **2.471 dòng trả hàng sau giao**: `1.305 / 20.499` dòng `COMPLETED` Shopee (**6,37%**; cộng 34 `TO_RETURN` = `1.339 / 25.546` = **5,24%**) và `1.132 / 83.621` dòng đã giao TikTok (**1,35%**), ảnh hưởng **~703,2 triệu đồng GMV** (`476,54 triệu` Shopee + `226,68 triệu` TikTok; TB ~262 ca/tháng trên ~21 gian hàng).
  - Thiệt hại hai chiều phía shop (Shopee): mất thêm **24.502.900đ** `return_shipping_fee`; **873 / 1.305 dòng hoàn (66,90%)** bị âm `escrow_amount` (tổng `-1.918.028đ`).
  - Phân nhóm lý do trên TikTok (`1.132` ca sau giao): **505 / 1.132 (44,61%)** do sai size (`320 = 28,27%`) và không khớp mô tả (`185 = 16,34%`); **432 / 1.132 (38,16%)** đổi ý/không còn nhu cầu; **152 / 1.132 (13,43%)** gửi sai, thiếu hàng, hư hỏng, lỗi, nghi hàng giả. Ngành thời trang có tỷ lệ hoàn **5,06%** (TikTok `Th***AGO`, chiếm 51,68% toàn bộ ca hoàn TikTok) và **11,93%** (Shopee `Thờ***GO`).
  - Giá trị đơn & hành vi lặp lại: AOV đơn hoàn TikTok **200.244đ** vs đơn thường **120.145đ** (**+66,7%**); Shopee **377.006đ** vs **343.699đ** (**+9,7%**). Chỉ **262 / 14.513 khách Shopee (1,81%)** hoàn ≥2 lần nhưng tạo **605 / 1.326 dòng trả hàng (45,63%)** (tối đa **9 lần**/người).
  - Bác bỏ hướng phụ: lệch phí ship Shopee `0 / 25.546` (**0%**); trễ `rts_sla_time` TikTok `85 / 88.815` (**0,10%**).

- **Khảo sát (`n = 32` người mua Shopee/TikTok ngoài nhóm, ngày 27/11/2026 · 17:05 → 23:31):**
  - Tần suất: `19 / 32` (**59,4%**) từng muốn trả hàng/hoàn tiền trong 3 tháng gần đây (`7 / 32 = 21,9%` gặp ≥2 lần; TB **0,32 lần/tháng** trên toàn mẫu, hay **0,54 lần/tháng** trong nhóm từng gặp sự cố).
  - Nguyên nhân chính (trên `n = 24` phản hồi có nêu nguyên nhân sự cố): **12 / 24 (50,0%)** do sai size (`8/24 = 33,3%`) và không khớp mô tả (`4/24 = 16,7%`); `7/24 (29,2%)` đổi ý; `3/24 (12,5%)` gửi sai/thiếu; `2/24 (8,3%)` nghi hàng giả/kém chất lượng.
  - Giá trị đơn (`n = 26` người nêu giá trị): **20 / 26 (76,9%)** từ `100.000đ` trở lên, trong đó **10 / 26 (38,5%)** trên `300.000đ` (vượt hạn mức tự duyệt).
  - Điểm nghẽn (Câu 9, chọn nhiều): **20 / 32 (62,5% tổng mẫu · 20 / 24 = 83,3% nhóm từng gặp sự cố)** gặp ít nhất 1 trong 4 vướng mắc: không rõ hạn trả hai sàn (`10/32 = 31,2%`), quên quay video mở hộp / không biết cần bằng chứng gì (`9/32 = 28,1%`), shop sửa hoặc giải thích mô tả khác lúc đặt (`7/32 = 21,9%`), shop phản hồi chậm hoặc từ chối không rõ lý do (`7/32 = 21,9%`).
  - Thời gian & kết quả xử lý: **13 / 24 (54,2%)** mất từ `5 phút` trở lên (`5 / 24 = 20,8%` mất `≥15 phút`, thêm `1` người bỏ giữa chừng; trung bình có trọng số qua điểm giữa các khoảng thời gian trên 23 người hoàn tất = **10,76 phút/ca**). **7 / 25 (28,0%)** chịu kết quả tiêu cực (`3` tự bỏ qua vì ngại rắc rối · `2` bị từ chối giữ hàng lỗi · `2` được hoàn nhưng phải đối chất/bổ sung nhiều lần).

---

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. `"shop đọc nhưng đổ lỗi là do mình"` — phiếu khảo sát `S14` (`evidence/survey/results.csv`)
2. `"Đổ lỗi cho bên vận chuyển"` — phiếu khảo sát `S18` (`evidence/survey/results.csv`)
3. `"Vì chất lượng sản phẩm kém nhưng lại ngại lười đổi sản phẩm và cũng đã quá hạn nên ngậm ngùi đánh giá 1*"` — phiếu khảo sát `S22` (`evidence/survey/results.csv`)
4. Lý do nguyên văn từ data thật: `"Mặt hàng quá lớn hoặc quá nhỏ"` (`319 dòng`, `72,15 triệu` GMV) và `"Sản phẩm không khớp với mô tả"` (`185 dòng`, `27,88 triệu` GMV) — `vietnam_ecommerce.tiktok_orders` (`evidence/data-mining.md`)
5. Lý do nguyên văn từ data thật: `"Gửi sai sản phẩm"` (`65 dòng`) và `"Đã nhận được kiện hàng nhưng thiếu một số mặt hàng"` (`29 dòng`) — `vietnam_ecommerce.tiktok_orders` (`evidence/data-mining.md`)
6. Lý do nguyên văn rủi ro cao: `"Nghi ngờ hàng giả"` (`5 dòng`, `1,09 triệu` GMV) — `vietnam_ecommerce.tiktok_orders` (`evidence/data-mining.md`)
7. Dòng hoàn hàng thực tế Shopee bị âm tiền về: `quantity=1`, `returned_quantity=1`, `buyer_total_amount=231.500đ`, `escrow_amount=-1.620đ`, `return_shipping_fee=40.000đ` — `vietnam_ecommerce.shopee_orders` (`evidence/data-mining.md`)

---

## 4. Các nguồn có khớp nhau không

- **Khớp rất chặt ở 3 điểm cốt lõi:**
  1. *Nguyên nhân hàng đầu:* Trên data thật TikTok, sai size + không khớp mô tả chiếm **44,6%** (`505/1.132`); trong khảo sát người mua cũng chiếm đúng **50,0%** (`12/24`).
  2. *Giá trị đơn rủi ro:* Data thật cho thấy đơn hoàn đắt hơn đơn thường (`200k–377k`); khảo sát xác nhận **76,9%** (`20/26`) ca gặp sự cố có giá trị `≥100k` và **38,5%** (`10/26`) vượt `300k` (cần chuyển nhân viên sàn).
  3. *Tính chất hai chiều / lặp lại:* Data Shopee phát hiện `1,81%` người mua hoàn ≥2 lần tạo `45,63%` ca hoàn; khảo sát ghi nhận `21,9%` (`7/32`) từng muốn trả ≥2 lần trong 3 tháng, đồng thời **21,9%** (`7/32`) gặp tình huống shop sửa hoặc giải thích mô tả khác lúc đặt.
- **Chỗ lệch và lý do hợp lý:**
  - Trong khảo sát, `17 / 25 (68,0%)` người có trải nghiệm cho biết cuối cùng *"được duyệt hoàn nhanh"* và `10 / 24 (41,7%)` chỉ mất `<5 phút`. Khảo sát cho thấy các ca đơn giản, đủ bằng chứng thường trôi chảy; **nhưng nhóm `28,0%` (`7/25`) còn lại chịu thiệt hại trực tiếp (tự bỏ cuộc, giữ hàng lỗi hoặc đối chất kéo dài) và `83,3%` (`20/24`) từng vướng rào cản luật sàn / bằng chứng / shop đổi mô tả** — khớp với lý do nhóm thiết kế mức tự động `AI tự làm khi chắc (≤300k, đủ bằng chứng), chuyển nhân viên khi có tranh chấp / vượt hạn mức / quá hạn / hoàn lặp lại`.

---

## 5. Kết luận

Giả thuyết ở [`evidence/hypothesis.md`](hypothesis.md): **Đúng (và được tinh chỉnh sắc hơn)** — vượt cả hai ngưỡng đặt ra: `59,4%` người khảo sát từng cần trả hàng trong 3 tháng (`≥30%`), `83,3%` nhóm từng gặp sự cố vướng ≥1 trong 4 điểm nghẽn thông tin/bằng chứng và `28,0%` chịu kết quả tiêu cực (`54,2%` mất từ 5 phút trở lên, trung bình `10,76 phút/ca`). Điều còn lại chưa đo tự động từ hệ thống thật là ảnh/video mở hộp (bản chạy thử mô phỏng bằng trường `evidence_status` có kiểm soát).
