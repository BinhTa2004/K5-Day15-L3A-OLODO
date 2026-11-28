"""Công cụ cho Trợ lý Trả hàng / Hoàn tiền trung lập Shopee & TikTok Shop (Track D3).

Mỗi công cụ gắn @tool để tracing.py tự ghi trace (tên, input, output, thời gian, lỗi).
Dữ liệu nền đọc từ data/orders.json và data/policies.json (synthetic, seed=42, không PII).
Mọi quyết định kiểm quy tắc dùng hoàn toàn dữ liệu khách quan (không đọc nhãn gợi ý issue_hint).
"""
import json
import os
from tracing import tool, TOOLS  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


def _load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_orders() -> list:
    """Trả về danh sách đơn hàng sạch để hiển thị trên Web UI (không gắn @tool để khỏi nhiễu trace)."""
    orders = _load_json("orders.json")
    return [
        {
            "order_id": o["order_id"],
            "platform": o["platform"],
            "category": o["category"],
            "item_name": o["item_name"],
            "amount_vnd": o["amount_vnd"],
            "delivered_days_ago": o["delivered_days_ago"],
            "buyer_id": o["buyer_id"],
            "buyer_total_orders_90d": o.get("buyer_total_orders_90d", 0),
            "buyer_returns_90d": o["buyer_returns_90d"],
            "shop_id": o.get("shop_id", "SHOP"),
            "evidence_status": o.get("evidence_status", ""),
            "missing_evidence": "chưa cung cấp" in (o.get("evidence_status") or "").lower(),
            "over_limit_300k": int(o["amount_vnd"]) > 300000,
            "over_15d": int(o["delivered_days_ago"]) > 15,
            "modified_after_order": o.get("listing_at_order") != o.get("listing_current"),
        }
        for o in orders
    ]


@tool
def get_order(order_id: str) -> dict:
    """Tra cứu thông tin đơn hàng theo mã đơn sạch (ORD-XXX).
    Input: order_id (str). Output: dict thông tin đơn hàng hoặc {"found": False}. Không tác động ra ngoài."""
    oid = (order_id or "").strip().upper()
    orders = _load_json("orders.json")
    for o in orders:
        if o["order_id"].upper() == oid:
            clean = dict(o)
            clean.pop("issue_hint", None)
            return {"found": True, **clean}
    return {"found": False, "order_id": oid}


@tool
def get_listing_at_order(order_id: str) -> dict:
    """Lấy mô tả sản phẩm tại thời điểm người mua đặt hàng (listing_at_order) và hiện tại.
    Input: order_id (str). Output: dict gồm listing_at_order, listing_current, modified_after_order. Không tác động ra ngoài."""
    oid = (order_id or "").strip().upper()
    orders = _load_json("orders.json")
    for o in orders:
        if o["order_id"].upper() == oid:
            at_order = o.get("listing_at_order", "")
            current = o.get("listing_current", "")
            return {
                "found": True,
                "order_id": oid,
                "listing_at_order": at_order,
                "listing_current": current,
                "modified_after_order": at_order != current,
            }
    return {"found": False, "order_id": oid}


@tool
def get_policy(platform: str, issue_type: str = "") -> dict:
    """Tra cứu chính sách trả hàng theo sàn (shopee / tiktok) và hạn mức duyệt nội bộ.
    Input: platform (str), issue_type (str). Output: dict quy định thời hạn, bằng chứng và hạn mức 300.000đ. Không tác động ra ngoài."""
    policies = _load_json("policies.json")
    plat_key = "tiktok" if "tiktok" in (platform or "").lower() else "shopee"
    plat_info = policies["platforms"].get(plat_key, {})
    return {
        "platform": plat_key,
        "issue_type": issue_type,
        "auto_approve_limit_vnd": policies.get("auto_approve_limit_vnd", 300000),
        "serial_return_threshold": policies.get("serial_return_threshold", 3),
        **plat_info,
    }


@tool
def get_complaint_history(buyer_id: str) -> dict:
    """Kiểm tra lịch sử đơn và số lần trả hàng trong 90 ngày gần đây của người mua.
    Input: buyer_id (str). Output: dict total_orders_90d, returns_90d, is_serial_returner. Không tác động ra ngoài."""
    bid = (buyer_id or "").strip().upper()
    orders = _load_json("orders.json")
    policies = _load_json("policies.json")
    threshold = policies.get("serial_return_threshold", 3)
    for o in orders:
        if o["buyer_id"].upper() == bid:
            ret_cnt = int(o.get("buyer_returns_90d", 0))
            return {
                "found": True,
                "buyer_id": bid,
                "total_orders_90d": int(o.get("buyer_total_orders_90d", 0)),
                "returns_90d": ret_cnt,
                "is_serial_returner": ret_cnt >= threshold,
                "threshold": threshold,
            }
    return {"found": False, "buyer_id": bid, "returns_90d": 0, "is_serial_returner": False}


@tool
def check_return_rules(order_id: str, claimed_reason: str, has_evidence: bool) -> dict:
    """Bộ kiểm quy tắc cứng bằng code (không dùng AI tính toán, không đọc trường issue_hint).
    Input: order_id (str), claimed_reason (str), has_evidence (bool).
    Output: dict gồm action (guide_return | need_evidence | escalate | reject_expired | reject_policy_or_pii | reject_and_escalate) và flags chi tiết. Không tác động ra ngoài."""
    oid = (order_id or "").strip().upper()
    orders = _load_json("orders.json")
    policies = _load_json("policies.json")
    order = next((o for o in orders if o["order_id"].upper() == oid), None)
    if not order:
        return {"found": False, "action": "not_found", "flags": ["order_not_found"]}

    text_l = (claimed_reason or "").lower()
    plat = order["platform"]
    plat_pol = policies["platforms"][plat]
    limit_vnd = policies["auto_approve_limit_vnd"]
    serial_thresh = policies["serial_return_threshold"]
    days = int(order["delivered_days_ago"])

    is_change_mind = any(k in text_l for k in ("đổi ý", "không thích", "không hợp", "không còn nhu cầu"))
    max_days = plat_pol["change_of_mind_days"] if is_change_mind else plat_pol["return_window_days"]

    flags = []
    if any(k in text_l for k in ("số điện thoại", "sđt", "sdt", "số đt", "địa chỉ nhà", "địa chỉ shop", "địa chỉ riêng")):
        flags.append("pii_request")
    if any(k in text_l for k in ("bóc phốt", "không cần trả hàng", "không trả hàng", "nếu không duyệt")):
        flags.append("threat_or_refund_without_return")
    if any(k in text_l for k in ("hàng giả", "nhái", "fake", "nghi giả")):
        flags.append("suspected_counterfeit")
    if any(k in text_l for k in ("khoá", "khóa", "chặn tài khoản", "bồi thường thêm")):
        flags.append("out_of_scope_penalty_or_compensation")
    if days > max_days:
        flags.append("expired_return_window")
    if order["amount_vnd"] > limit_vnd:
        flags.append("over_auto_limit_300k")
    if int(order.get("buyer_returns_90d", 0)) >= serial_thresh:
        flags.append("serial_returner")
    if order.get("listing_at_order") != order.get("listing_current"):
        flags.append("listing_modified_after_order")
    if not has_evidence:
        flags.append("missing_evidence")

    if "pii_request" in flags or "out_of_scope_penalty_or_compensation" in flags or "threat_or_refund_without_return" in flags:
        action = "reject_and_escalate" if ("over_auto_limit_300k" in flags or "suspected_counterfeit" in flags) else "reject_policy_or_pii"
    elif "suspected_counterfeit" in flags:
        action = "escalate"
    elif "expired_return_window" in flags:
        action = "reject_expired"
    elif "serial_returner" in flags or "over_auto_limit_300k" in flags:
        action = "escalate"
    elif "missing_evidence" in flags:
        action = "need_evidence"
    else:
        action = "guide_return"

    return {
        "found": True,
        "order_id": oid,
        "platform": plat,
        "amount_vnd": order["amount_vnd"],
        "auto_limit_vnd": limit_vnd,
        "days_since_delivery": days,
        "max_days": max_days,
        "action": action,
        "flags": flags,
    }


@tool
def escalate_to_human(order_id: str, reason: str) -> dict:
    """Tạo phiếu chuyển trường hợp sang nhân viên sàn duyệt (chỉ trả về bản nháp, không gửi thật).
    Input: order_id (str), reason (str). Output: dict phiếu chuyển nhân viên trạng thái pending_human_review. Không tác động ra ngoài thật."""
    oid = (order_id or "").strip().upper()
    return {
        "ticket_id": "ESC-%s" % oid,
        "order_id": oid,
        "status": "pending_human_review",
        "reason": reason,
    }
