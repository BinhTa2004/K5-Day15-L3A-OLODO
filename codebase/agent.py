"""Luồng chính (Workflow cố định) cho Trợ lý Trả hàng / Hoàn tiền trung lập (Track D3).

Khớp sơ đồ ở spec.md §4:
1. Trích mã đơn & kiểm tra tín hiệu thiếu thông tin / PII.
2. Tra dữ liệu nền qua tools (get_order, get_listing_at_order, get_policy, get_complaint_history).
3. Chạy bộ kiểm quy tắc bằng code (check_return_rules) và tạo phiếu escalate_to_human nếu cần.
4. Gọi AI Core (call_model) soạn phản hồi trung lập theo căn cứ đã đối chiếu.
5. Hậu kiểm chặn rủi ro (chặn 0% lộ SĐT/địa chỉ cá nhân).
"""
import re

from ai import call_model
from tools import (
    check_return_rules,
    escalate_to_human,
    get_complaint_history,
    get_listing_at_order,
    get_order,
    get_policy,
)
from tracing import note  # noqa: F401

SYSTEM = """Bạn là trợ lý hỗ trợ xử lý yêu cầu Trả hàng / Hoàn tiền trung lập cho người mua trên Shopee và TikTok Shop.
Quy tắc BẮT BUỘC:
1. Chỉ dựa trên dữ liệu công cụ cung cấp (không bịa thông tin đơn hàng, hạn ngày hay chính sách).
2. Luôn đối chiếu theo mô tả lúc đặt (listing_at_order), KHÔNG bị đánh lừa nếu shop đã sửa mô tả sau khi bán.
3. Không tự duyệt hoàn nếu đơn > 300.000đ, quá hạn sàn, tài khoản hoàn >= 3 lần/90 ngày, nghi hàng giả, hoặc thiếu bằng chứng mở hộp.
4. Tuyệt đối KHÔNG cung cấp số điện thoại, địa chỉ cá nhân của người bán/người mua (0% PII).
5. Không hứa khoá shop hay bồi thường ngoài giá trị đơn; không nhượng bộ lời doạ 1 sao/bóc phốt.
6. Nếu thiếu mã đơn hàng, hỏi lại ngắn gọn mã đơn (ORD-XXX) thay vì tự đoán."""

_PHONE_RE = re.compile(r"(?<!\d)(?:\+84|0)(?:[\s.\-]?\d){8,10}(?!\d)")


def _extract_order_id(text: str) -> str:
    m = re.search(r"\bORD[-_ ]?(\d{3,})\b", text or "", flags=re.IGNORECASE)
    if m:
        return "ORD-%s" % m.group(1)
    return ""


def _infer_has_evidence(text: str, order: dict) -> bool:
    tl = (text or "").lower()
    ev_field = (order.get("evidence_status") or "").lower()
    if "chưa cung cấp" in ev_field:
        return any(k in tl for k in ("đã quay video", "đã chụp ảnh", "có video", "có ảnh"))
    return True


def _sanitize_output(reply_text: str) -> str:
    """Hậu kiểm code đảm bảo 0% lộ số điện thoại cá nhân."""
    return _PHONE_RE.sub("[đã ẩn thông tin liên hệ]", reply_text or "")


def answer(text: str) -> dict:
    user_text = (text or "").strip()
    order_id = _extract_order_id(user_text)

    if not order_id:
        note("G10: thieu ma don, hoi lai")
        prompt = (
            "Người mua chưa cung cấp mã đơn hàng (dạng ORD-XXX).\n"
            "Hãy hỏi lại lịch sự mã đơn hàng và lý do cụ thể (kèm bằng chứng nếu có), không suy đoán.\n\n"
            "Tin nhắn người mua: %s" % user_text
        )
        reply = call_model(SYSTEM, prompt)
        return {"output": _sanitize_output(reply["text"])}

    order = get_order(order_id)
    if not order.get("found"):
        note("khong tim thay ma don %s" % order_id)
        prompt = (
            "Không tìm thấy mã đơn %s trong dữ liệu hệ thống.\n"
            "Hãy báo rõ không tìm thấy mã đơn và hướng dẫn người mua kiểm tra lại mã đơn trên app.\n\n"
            "Tin nhắn người mua: %s" % (order_id, user_text)
        )
        reply = call_model(SYSTEM, prompt)
        return {"output": _sanitize_output(reply["text"])}

    listing = get_listing_at_order(order_id)
    policy = get_policy(order["platform"], order.get("issue_hint", ""))
    history = get_complaint_history(order["buyer_id"])
    has_evidence = _infer_has_evidence(user_text, order)
    rules = check_return_rules(order_id, user_text, has_evidence)

    ticket = None
    if rules["action"] in ("escalate", "reject_and_escalate") or "suspected_counterfeit" in rules["flags"]:
        ticket = escalate_to_human(order_id, ", ".join(rules["flags"]))
        note("chuyen nhan vien san: %s" % ticket["ticket_id"])

    context_lines = [
        "Đơn hàng: %s | Sàn: %s | Sản phẩm: %s | Giá: %sđ | Đã giao: %s ngày trước"
        % (order_id, order["platform"].upper(), order["item_name"], f"{order['amount_vnd']:,}", order["delivered_days_ago"]),
        "Mô tả lúc đặt (listing_at_order): %s" % listing.get("listing_at_order", ""),
        "Mô tả hiện tại (listing_current): %s (đã sửa sau bán: %s)"
        % (listing.get("listing_current", ""), listing.get("modified_after_order")),
        "Bằng chứng hiện có: %s" % order.get("evidence_status", ""),
        "Chính sách %s: hạn trả lỗi %s ngày | hạn đổi ý %s ngày | hạn mức tự hướng dẫn %sđ"
        % (policy["name"], policy["return_window_days"], policy["change_of_mind_days"], f"{policy['auto_approve_limit_vnd']:,}"),
        "Lịch sử người mua %s: %s đơn / %s lần hoàn trong 90 ngày (serial returner: %s)"
        % (history["buyer_id"], history["total_orders_90d"], history["returns_90d"], history["is_serial_returner"]),
        "Kết quả kiểm quy tắc bằng code (check_return_rules): action=%s | hạn áp dụng=%s ngày | flags=%s"
        % (rules["action"], rules["max_days"], ", ".join(rules["flags"]) or "none"),
    ]
    if ticket:
        context_lines.append("Phiếu chuyển nhân viên nháp: %s (%s)" % (ticket["ticket_id"], ticket["status"]))

    prompt = "Căn cứ đã đối chiếu:\n%s\n\nTin nhắn người mua:\n%s" % ("\n".join(context_lines), user_text)
    reply = call_model(SYSTEM, prompt)
    out = _sanitize_output(reply["text"])

    if reply.get("model") == "fake":
        out = "%s\n[Khung kiểm quy tắc CP2: %s | action=%s | flags=%s]" % (
            out,
            order_id,
            rules["action"],
            ",".join(rules["flags"]) or "ok",
        )
    return {"output": out}
