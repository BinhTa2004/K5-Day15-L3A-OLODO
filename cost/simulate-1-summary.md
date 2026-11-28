# Tóm tắt mô phỏng simulate-1@20261128-104631

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| mua_it | 31 | 1 | 1321 | 632 | 1.0 | 5.0 |
| mua_thuong_xuyen | 18 | 2 | 2604 | 1137 | 2.0 | 9.7 |
| hoan_lap_lai | 1 | 3 | 4068 | 1496 | 3.0 | 16.0 |

Tỉ lệ đạt dùng để tính: 24/25 (96%) — lượt run-2@20261128-100823

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (15.000 người) | Chi phí / tháng — cơ sở (50.000 người) | Chi phí / tháng — cao (200.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini (vào 0.15 · ra 0.6 $/1M) | $0.00077 (≈ 20 ₫) | $0.00081 (≈ 20 ₫) | $0.00058 (≈ 15 ₫) | $6.25 (≈ 158.748 ₫) | $20.83 (≈ 529.160 ₫) | $83.33 (≈ 2.116.641 ₫) | $0.00042 (≈ 11 ₫) |
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.0017 (≈ 43 ₫) | $0.0018 (≈ 45 ₫) | $0.0013 (≈ 32 ₫) | $13.66 (≈ 346.941 ₫) | $45.53 (≈ 1.156.469 ₫) | $182.12 (≈ 4.625.877 ₫) | $0.00091 (≈ 23 ₫) |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.0090 (≈ 228 ₫) | $0.0094 (≈ 238 ₫) | $0.0067 (≈ 170 ₫) | $72.23 (≈ 1.834.562 ₫) | $240.76 (≈ 6.115.208 ₫) | $963.02 (≈ 24.460.833 ₫) | $0.0048 (≈ 122 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-oss:20b. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 25.400 ₫ (Tỷ giá tham chiếu 25.400 VND/USD (tự ước tính tham chiếu ngày 28/11/2026)).
