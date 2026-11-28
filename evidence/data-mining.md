# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Script đếm để tại [`evidence/count_xomdata.sql`](count_xomdata.sql), không chứa thông tin cá nhân (PII) và không chứa mật khẩu kết nối.
> Repo chỉ chứa số đã tổng hợp và ví dụ ẩn danh — không chép lại nguyên bảng dữ liệu gốc.

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** Bộ `vietnam_ecommerce` trên Xóm Dataset (`https://dataset.xomdata.com/datasets/schema/vietnam_ecommerce`), gồm 2 bảng thật của các gian hàng Việt Nam:
  - `vietnam_ecommerce.shopee_orders`: **25.546 dòng hàng** (13/12/2025 → 07/09/2026, 269 ngày ≈ 8,8 tháng), 9 gian hàng.
  - `vietnam_ecommerce.tiktok_orders`: **102.000 dòng hàng** (31/10/2025 → 09/09/2026, 314 ngày ≈ 10,3 tháng), 12 gian hàng.
- **Đếm gì · trên tập nào · lọc gì:**
  1. Đếm số dòng trả hàng sau giao trên Shopee: lọc `order_status = 'COMPLETED'` có `returned_quantity > 0 OR return_requested_qty > 0`, cộng trạng thái `TO_RETURN`; kiểm tra nhóm hoàn hàng có `escrow_amount < 0` và tổng `return_shipping_fee`.
  2. Đếm số dòng trả hàng sau giao trên TikTok Shop: lọc `order_status IN ('COMPLETED', 'DELIVERED')` có `item_cancel_reason` không trống; phân nhóm nguyên nhân và so sánh AOV (`item_sale_price * quantity`).
  3. Kiểm tra hành vi lặp lại theo `buyer_user_id` trên Shopee và tỷ lệ hoàn theo gian hàng (`shop_name`) trên cả hai sàn.
  4. Kiểm chứng (đối chứng) hai hướng ứng viên khác: huỷ trước giao (`CANCELLED`), trễ SLA (`rts_sla_time`, `delivery_sla_time`, `ship_by_date`), và lệch phí ship (`actual_shipping_fee > estimated_shipping_fee`).
- **Mẫu số là gì:** **Cấp dòng hàng (`row`)** trên toàn bảng hoặc trên tập con đã giao (`COMPLETED` / `DELIVERED`). Lý do kỹ thuật quan trọng: `order_sn` (Shopee) và `order_id` (TikTok) đã bị Xóm Dataset che bằng dấu `*` nên chỉ còn 35 và 386 giá trị distinct; không được `GROUP BY order_sn / order_id`.
- **Script:** [`evidence/count_xomdata.sql`](count_xomdata.sql) (truy vấn SQL Server, ngày chạy 27/11/2026).

## 2. Đọc trước, đếm sau

Đã kiểm tra schema và mẫu dữ liệu trước khi tổng hợp. 4 phát hiện cấu trúc quan trọng:
1. **`order_sn` / `order_id` bị mask bằng dấu `*`:** Chỉ giữ 5 ký tự đầu nên `GROUP BY order_sn` cho kết quả sai (chỉ 35 đơn Shopee); bắt buộc đếm ở cấp dòng hàng (`row`).
2. **Cột ghi chú khách trống 100%:** `shopee_orders.buyer_remark` = **0 dòng** và `tiktok_orders.buyer_message` = **0 dòng** có nội dung.
3. **Hai hướng tưởng là đau nhưng bằng 0 / rất thấp:** `actual_shipping_fee > estimated_shipping_fee` trên Shopee = **0 dòng**; trễ `rts_sla_time` trên TikTok = **85 / 88.815 (0,10%)** và trễ `delivery_sla_time` = **0 / 3.124 (0%)**.
4. **Hoàn hàng Shopee nằm ngay trong `COMPLETED`:** `1.305` dòng có `returned_quantity > 0` mang trạng thái `COMPLETED`, nhiều dòng bị trừ `return_shipping_fee` khiến `escrow_amount` bị âm (`-1.620đ`).

## 3. Kết quả

| Đếm gì | x / N | % | Ghi chú |
|---|---:|---:|---|
| Trả hàng sau giao (Shopee `COMPLETED`) | 1.305 / 20.499 | 6,37% | Cộng 34 `TO_RETURN` = **1.339 / 25.546 (5,24%)**; `buyer_total_amount` 476.535.468đ, `escrow_amount` 126.396.703đ, `return_shipping_fee` **24.502.900đ** |
| Hoàn hàng Shopee bị âm `escrow_amount` | 873 / 1.305 | 66,90% | Tổng âm **-1.918.028đ**, kèm `return_shipping_fee` **21.425.100đ** trên 307.229.172đ `buyer_total_amount` |
| Trả hàng sau giao (TikTok `COMPLETED`+`DELIVERED`) | 1.132 / 83.621 | 1,35% | 999 `COMPLETED` + 133 `DELIVERED`, ảnh hưởng **226.676.409đ** `sale_gmv` (tổng 2 sàn: **2.471 dòng**, ~**703 triệu GMV**) |
| TikTok hoàn do sai size / không khớp mô tả | 505 / 1.132 | 44,61% | `Mặt hàng quá lớn/nhỏ` 319+1 (28,27%), `Không khớp mô tả` 185 (16,34%) |
| TikTok hoàn do đổi ý / không còn nhu cầu | 432 / 1.132 | 38,16% | `Đổi ý` 351 (31,01%), `Không còn nhu cầu` 65+14+2 |
| TikTok hoàn do lỗi đóng gói / chất lượng / nghi giả | 152 / 1.132 | 13,43% | Gửi sai (66), thiếu hàng (29), kém (20), hư hỏng (19), lỗi (10), nghi hàng giả (5), chưa nhận (3) |
| Hiệu ứng thời trang (TikTok `Th***AGO` vs `Co***Tea`) | 585 / 1.132 | 51,68% | `Th***AGO` tỷ lệ hoàn **5,06%** (cao gần 10x shop trà **0,52%**); Shopee `Thờ***GO` tỷ lệ hoàn **11,93%** |
| Serial returners Shopee (hoàn ≥2 lần) | 262 / 14.513 khách | 1,81% | Chỉ 1,8% khách nhưng tạo **605 / 1.326 dòng trả hàng (45,63%)**; 49 người hoàn ≥3 lần (tối đa **9 lần**) |
| Giá trị TB đơn hoàn vs đơn thường (TikTok) | 200.244đ vs 120.145đ | +66,67% | Shopee: đơn hoàn **377.006đ** vs đơn thường **343.699đ** (**+9,69%**) |
| Huỷ đơn trước giao (Shopee / TikTok) | 4.658 / 25.546 · 16.267 / 102.000 | 18,23% · 15,95% | 56,48% huỷ Shopee muốn sửa đơn/địa chỉ/voucher; 49,2% Shopee & 48,4% TikTok huỷ trong ≤10 phút |
| Đối chứng: Lệch phí ship Shopee / Trễ RTS TikTok | 0 / 25.546 · 85 / 88.815 | 0,00% · 0,10% | Bác bỏ giả thuyết lệch phí ship ĐVVC và trễ SLA TikTok |

## 4. ≥5 ví dụ cụ thể (đã ẩn danh từ `vietnam_ecommerce`, không PII)

1. **Shopee · Hoàn hàng âm `escrow_amount` kèm phí ship hoàn 40.000đ:** dòng `COMPLETED` có `quantity=1`, `returned_quantity=1`, `buyer_total_amount=231.500đ`, nhưng `escrow_amount=-1.620đ` và `return_shipping_fee=40.000đ` (tương tự với đơn `403.500đ` cũng ghi `escrow_amount=-1.620đ`, `return_shipping_fee=40.000đ`).
2. **TikTok · Lý do nguyên văn `"Mặt hàng quá lớn hoặc quá nhỏ"`:** xuất hiện **319 dòng** (`72.148.360đ` `sale_gmv`, chiếm 28,18% ca hoàn sau giao TikTok).
3. **TikTok · Lý do nguyên văn `"Sản phẩm không khớp với mô tả"`:** xuất hiện **185 dòng** (`27.879.580đ` `sale_gmv`, chiếm 16,34% ca hoàn sau giao TikTok).
4. **TikTok · Lý do nguyên văn `"Gửi sai sản phẩm"` và `"Đã nhận được kiện hàng nhưng thiếu một số mặt hàng"`:** lần lượt **65 dòng** (`8.093.054đ`) và **29 dòng** (`5.057.612đ`) — ca đòi hỏi bằng chứng video mở hộp rõ ràng.
5. **TikTok · Lý do nguyên văn `"Nghi ngờ hàng giả"`:** **5 dòng** (`1.086.831đ`) — ca rủi ro cao bắt buộc chuyển nhân viên sàn chuyên trách.
6. **TikTok · Lý do nguyên văn `"Đổi ý"`:** **351 dòng** (`72.783.333đ`, chiếm 31,01%) — phản ánh nhóm cần phân biệt rõ hạn đổi ý và tình trạng tem mác, tránh lạm dụng hoàn lặp lại.

## 5. Giới hạn của data

Data `vietnam_ecommerce` cho biết **chuyện gì xảy ra ở mức đơn/dòng hàng** (tần suất hoàn, lý do chuẩn hoá trên sàn, thiệt hại tiền về, hành vi hoàn lặp lại), nhưng **không cho biết vì sao người mua lúng túng khi gửi yêu cầu/bằng chứng** (cột `buyer_remark` và `buyer_message` đều trống 0 dòng, không có transcript chat hay ảnh mở hộp).
→ **Kiểm lại bằng nguồn thứ 2:** Phỏng vấn **≥3 người mua** và khảo sát **≥20 người mua Shopee/TikTok ngoài nhóm** trong lớp L3 (bộ câu hỏi tại [`evidence/survey/questions.md`](survey/questions.md), tổng hợp hoàn tất trước CP3).
