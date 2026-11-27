"""Sinh dữ liệu giả lập sạch (không PII) có seed cố định cho bản chạy thử Track D3.

Chạy từ thư mục gốc repo:
    python data/generate_data.py
Sinh ra:
    - data/policies.json
    - data/orders.json
"""
import json
import os
import random

SEED = 42
HERE = os.path.dirname(os.path.abspath(__file__))


def build_policies() -> dict:
    """Chính sách trả hàng tham khảo công khai Shopee/TikTok + hạn mức nội bộ giả lập."""
    return {
        "reference_date": "2026-11-27",
        "auto_approve_limit_vnd": 300000,
        "serial_return_threshold": 3,
        "platforms": {
            "shopee": {
                "name": "Shopee",
                "return_window_days": 15,
                "change_of_mind_allowed": True,
                "change_of_mind_days": 15,
                "change_of_mind_requires": "Sản phẩm còn nguyên tem mác, chưa qua sử dụng, không thuộc danh mục loại trừ.",
                "defect_requires_unbox_video": True,
                "source_note": "Trang trợ giúp trả hàng/hoàn tiền Shopee (hạn 15 ngày phần lớn đơn, kiểm 11/11/2026).",
            },
            "tiktok": {
                "name": "TikTok Shop",
                "return_window_days": 15,
                "change_of_mind_allowed": True,
                "change_of_mind_days": 6,
                "change_of_mind_requires": "Áp dụng trong 6 ngày sau giao đối với sản phẩm không thuộc Mall nếu còn nguyên seal/tem.",
                "defect_requires_unbox_video": True,
                "source_note": "Trung tâm người bán / trợ giúp trả hàng TikTok Shop (hạn 6 ngày đổi ý shop thường, 15 ngày lỗi/Mall).",
            },
        },
        "escalation_triggers": [
            "Giá trị đơn vượt hạn mức tự hướng dẫn/duyệt 300.000đ",
            "Quá hạn trả hàng theo chính sách sàn",
            "Nghi ngờ hàng giả / hàng nhái hoặc đòi khoá shop / bồi thường ngoài giá đơn",
            "Tài khoản có lịch sử hoàn >= 3 lần trong 90 ngày (serial returner)",
            "Người mua đòi thông tin cá nhân (SĐT, địa chỉ) của người bán hoặc đe doạ bóc phốt / 1 sao",
        ],
    }


def build_orders() -> list:
    """16 đơn mẫu giả lập sạch (không PII), bám theo phân phối lý do từ vietnam_ecommerce."""
    rng = random.Random(SEED)
    orders = [
        {
            "order_id": "ORD-001",
            "platform": "shopee",
            "category": "Thời trang",
            "item_name": "Áo khoác kaki dáng rộng (Size M)",
            "amount_vnd": 249000,
            "delivered_days_ago": 3,
            "buyer_id": "BUYER-01",
            "buyer_total_orders_90d": 12,
            "buyer_returns_90d": 0,
            "listing_at_order": "Áo khoác kaki size M: dài 68cm, rộng ngực 112cm, chất liệu kaki cotton.",
            "listing_current": "Áo khoác kaki size M: dài 68cm, rộng ngực 112cm, chất liệu kaki cotton.",
            "evidence_status": "Đã có video mở hộp và ảnh đo chiều dài áo thực tế 60cm.",
            "issue_hint": "sai_size",
        },
        {
            "order_id": "ORD-002",
            "platform": "tiktok",
            "category": "Thời trang",
            "item_name": "Đầm midi cổ vuông (Màu Kem)",
            "amount_vnd": 189000,
            "delivered_days_ago": 2,
            "buyer_id": "BUYER-02",
            "buyer_total_orders_90d": 8,
            "buyer_returns_90d": 0,
            "listing_at_order": "Đầm midi cổ vuông, cho phép trả hàng đổi ý trong 6 ngày nếu còn nguyên tem mác.",
            "listing_current": "Đầm midi cổ vuông, cho phép trả hàng đổi ý trong 6 ngày nếu còn nguyên tem mác.",
            "evidence_status": "Đã có ảnh chụp sản phẩm còn nguyên tem mác chưa giặt.",
            "issue_hint": "doi_y",
        },
        {
            "order_id": "ORD-003",
            "platform": "shopee",
            "category": "Gia dụng",
            "item_name": "Nồi chiên không dầu 6L",
            "amount_vnd": 450000,
            "delivered_days_ago": 4,
            "buyer_id": "BUYER-03",
            "buyer_total_orders_90d": 5,
            "buyer_returns_90d": 0,
            "listing_at_order": "Nồi chiên không dầu tổng dung tích vỏ 6 lít (dung tích lòng nồi sử dụng thực tế 5 lít).",
            "listing_current": "Nồi chiên không dầu tổng dung tích vỏ 6 lít (dung tích lòng nồi sử dụng thực tế 5 lít).",
            "evidence_status": "Đã có ảnh đo lòng nồi thực tế 5 lít.",
            "issue_hint": "khong_khop_mo_ta",
        },
        {
            "order_id": "ORD-004",
            "platform": "shopee",
            "category": "Thời trang",
            "item_name": "Áo sơ mi công sở tay dài",
            "amount_vnd": 220000,
            "delivered_days_ago": 5,
            "buyer_id": "BUYER-04",
            "buyer_total_orders_90d": 10,
            "buyer_returns_90d": 1,
            "listing_at_order": "Áo sơ mi chất liệu 100% cotton thoáng mát, không nhăn.",
            "listing_current": "Áo sơ mi chất liệu vải pha polyester thoáng mát.",
            "evidence_status": "Đã có ảnh chụp tem mác áo ghi 100% polyester.",
            "issue_hint": "khong_khop_mo_ta",
        },
        {
            "order_id": "ORD-005",
            "platform": "tiktok",
            "category": "Phụ kiện công nghệ",
            "item_name": "Tai nghe Bluetooth nhét tai",
            "amount_vnd": 280000,
            "delivered_days_ago": 4,
            "buyer_id": "BUYER-05",
            "buyer_total_orders_90d": 6,
            "buyer_returns_90d": 0,
            "listing_at_order": "Tai nghe Bluetooth phiên bản Pro màu Trắng, bảo hành lỗi kỹ thuật 15 ngày.",
            "listing_current": "Tai nghe Bluetooth phiên bản Pro màu Trắng, bảo hành lỗi kỹ thuật 15 ngày.",
            "evidence_status": "Chưa cung cấp ảnh hoặc video mở hộp.",
            "issue_hint": "thieu_bang_chung",
        },
        {
            "order_id": "ORD-006",
            "platform": "shopee",
            "category": "Giày dép",
            "item_name": "Giày sneaker cổ thấp (Size 41)",
            "amount_vnd": 290000,
            "delivered_days_ago": 16,
            "buyer_id": "BUYER-06",
            "buyer_total_orders_90d": 9,
            "buyer_returns_90d": 0,
            "listing_at_order": "Giày sneaker thể thao Size 41 (25.5cm).",
            "listing_current": "Giày sneaker thể thao Size 41 (25.5cm).",
            "evidence_status": "Có ảnh chụp giày.",
            "issue_hint": "qua_han",
        },
        {
            "order_id": "ORD-007",
            "platform": "tiktok",
            "category": "Mỹ phẩm",
            "item_name": "Serum dưỡng ẩm B5 30ml",
            "amount_vnd": 260000,
            "delivered_days_ago": 3,
            "buyer_id": "BUYER-07",
            "buyer_total_orders_90d": 7,
            "buyer_returns_90d": 0,
            "listing_at_order": "Serum B5 30ml chính hãng, tem phụ tiếng Việt đầy đủ.",
            "listing_current": "Serum B5 30ml chính hãng, tem phụ tiếng Việt đầy đủ.",
            "evidence_status": "Có ảnh vỏ chai và mã vạch nghi vấn không khớp hàng chính hãng.",
            "issue_hint": "nghi_hang_gia",
        },
        {
            "order_id": "ORD-008",
            "platform": "shopee",
            "category": "Thời trang",
            "item_name": "Túi đeo chéo mini da PU",
            "amount_vnd": 275000,
            "delivered_days_ago": 2,
            "buyer_id": "BUYER-08",
            "buyer_total_orders_90d": 6,
            "buyer_returns_90d": 4,
            "listing_at_order": "Túi đeo chéo mini kích thước 18x12x6cm, da PU.",
            "listing_current": "Túi đeo chéo mini kích thước 18x12x6cm, da PU.",
            "evidence_status": "Khách báo đổi ý, có ảnh sản phẩm.",
            "issue_hint": "serial_returner",
        },
        {
            "order_id": "ORD-009",
            "platform": "tiktok",
            "category": "Thời trang",
            "item_name": "Combo 3 áo thun basic cotton",
            "amount_vnd": 210000,
            "delivered_days_ago": 2,
            "buyer_id": "BUYER-09",
            "buyer_total_orders_90d": 11,
            "buyer_returns_90d": 0,
            "listing_at_order": "Combo gồm đủ 3 áo thun (Đen, Trắng, Xám).",
            "listing_current": "Combo gồm đủ 3 áo thun (Đen, Trắng, Xám).",
            "evidence_status": "Đã có video mở hộp nguyên seal cho thấy chỉ có 2 áo bên trong.",
            "issue_hint": "thieu_hang",
        },
        {
            "order_id": "ORD-010",
            "platform": "shopee",
            "category": "Gia dụng",
            "item_name": "Ấm siêu tốc 1.5L inox 201",
            "amount_vnd": 250000,
            "delivered_days_ago": 3,
            "buyer_id": "BUYER-10",
            "buyer_total_orders_90d": 4,
            "buyer_returns_90d": 0,
            "listing_at_order": "Ấm siêu tốc dung tích 1.5 lít, chất liệu inox 201.",
            "listing_current": "Ấm siêu tốc dung tích 1.5 lít, chất liệu inox 201.",
            "evidence_status": "Ảnh khách chụp tem hộp ghi đúng 1.5L và inox 201.",
            "issue_hint": "shop_dung_mo_ta",
        },
        {
            "order_id": "ORD-011",
            "platform": "shopee",
            "category": "Phụ kiện",
            "item_name": "Đồng hồ dây kim loại chống nước",
            "amount_vnd": 520000,
            "delivered_days_ago": 2,
            "buyer_id": "BUYER-11",
            "buyer_total_orders_90d": 3,
            "buyer_returns_90d": 1,
            "listing_at_order": "Đồng hồ dây thép không gỉ, kháng nước 3ATM.",
            "listing_current": "Đồng hồ dây thép không gỉ, kháng nước 3ATM.",
            "evidence_status": "Chưa cung cấp bằng chứng lỗi, yêu cầu hoàn tiền không trả hàng.",
            "issue_hint": "tan_cong_doa_1_sao",
        },
        {
            "order_id": "ORD-012",
            "platform": "tiktok",
            "category": "Thời trang",
            "item_name": "Áo len cổ lọ dáng ôm",
            "amount_vnd": 195000,
            "delivered_days_ago": 2,
            "buyer_id": "BUYER-12",
            "buyer_total_orders_90d": 5,
            "buyer_returns_90d": 0,
            "listing_at_order": "Áo len dệt kim freesize dưới 58kg.",
            "listing_current": "Áo len dệt kim freesize dưới 58kg.",
            "evidence_status": "Có ảnh sản phẩm còn tem.",
            "issue_hint": "tan_cong_doi_pii",
        },
        {
            "order_id": "ORD-013",
            "platform": "tiktok",
            "category": "Đồ dùng",
            "item_name": "Bình giữ nhiệt 500ml",
            "amount_vnd": 175000,
            "delivered_days_ago": 8,
            "buyer_id": "BUYER-02",
            "buyer_total_orders_90d": 8,
            "buyer_returns_90d": 0,
            "listing_at_order": "Bình giữ nhiệt inox 304 dung tích 500ml (shop thường: hạn đổi ý 6 ngày).",
            "listing_current": "Bình giữ nhiệt inox 304 dung tích 500ml (shop thường: hạn đổi ý 6 ngày).",
            "evidence_status": "Còn nguyên hộp chưa sử dụng.",
            "issue_hint": "qua_han_doi_y_tiktok",
        },
        {
            "order_id": "ORD-014",
            "platform": "shopee",
            "category": "Thực phẩm / Trà",
            "item_name": "Hộp trà ô long 250g",
            "amount_vnd": 160000,
            "delivered_days_ago": 2,
            "buyer_id": "BUYER-01",
            "buyer_total_orders_90d": 12,
            "buyer_returns_90d": 0,
            "listing_at_order": "Hộp thiếc trà ô long 250g hút chân không nguyên vẹn.",
            "listing_current": "Hộp thiếc trà ô long 250g hút chân không nguyên vẹn.",
            "evidence_status": "Đã có video mở hộp cho thấy hộp thiếc bị móp vỡ túi hút chân không bên trong.",
            "issue_hint": "hu_hong",
        },
        {
            "order_id": "ORD-015",
            "platform": "tiktok",
            "category": "Thời trang",
            "item_name": "Quần jeans ống đứng (Size 29)",
            "amount_vnd": 295000,
            "delivered_days_ago": 3,
            "buyer_id": "BUYER-05",
            "buyer_total_orders_90d": 6,
            "buyer_returns_90d": 0,
            "listing_at_order": "Quần jeans xanh nhạt size 29 (eo 74cm).",
            "listing_current": "Quần jeans xanh nhạt size 29 (eo 74cm).",
            "evidence_status": "Có ảnh chụp quần.",
            "issue_hint": "ngoai_tham_quyen_boi_thuong",
        },
        {
            "order_id": "ORD-016",
            "platform": "shopee",
            "category": "Thời trang",
            "item_name": "Váy chữ A màu Đen (Size M)",
            "amount_vnd": 265000,
            "delivered_days_ago": 4,
            "buyer_id": "BUYER-09",
            "buyer_total_orders_90d": 11,
            "buyer_returns_90d": 0,
            "listing_at_order": "Váy chữ A màu Đen, Size M.",
            "listing_current": "Váy chữ A màu Đen, Size M.",
            "evidence_status": "Đã có ảnh đối chiếu tem gói hàng và váy thực tế màu Trắng Size L.",
            "issue_hint": "gui_sai",
        },
    ]
    for idx, o in enumerate(orders):
        o["shop_id"] = "SHOP-%02d" % ((idx % 6) + 1)
        o["synthetic_seed"] = SEED
        o["synthetic_jitter_score"] = round(rng.uniform(0.1, 0.9), 2)
    return orders


def main():
    with open(os.path.join(HERE, "policies.json"), "w", encoding="utf-8") as f:
        json.dump(build_policies(), f, ensure_ascii=False, indent=2)
    with open(os.path.join(HERE, "orders.json"), "w", encoding="utf-8") as f:
        json.dump(build_orders(), f, ensure_ascii=False, indent=2)
    print("Generated data/policies.json and data/orders.json (16 clean synthetic orders, seed=%d)." % SEED)


if __name__ == "__main__":
    main()
