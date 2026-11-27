"""Luồng chính (Workflow cố định) cho Trợ lý Trả hàng / Hoàn tiền trung lập (Track D3).

Khớp sơ đồ ở spec.md §4:
1. Kiểm tra yêu cầu PII / ngoài thẩm quyền sớm (ngay cả khi không có mã đơn) & trích mã đơn (kết hợp Session Memory nếu Web UI truyền history).
2. Tra dữ liệu nền qua tools (get_order, get_listing_at_order, get_policy, get_complaint_history).
3. Chạy bộ kiểm quy tắc bằng code (check_return_rules) và tạo phiếu escalate_to_human nếu cần.
4. Gọi AI Core (call_model) soạn phản hồi trung lập theo căn cứ đã đối chiếu.
5. Hậu kiểm chặn rủi ro (chặn 0% lộ SĐT/địa chỉ cá nhân & gắn mã phiếu chuyển nhân viên nếu thiếu).
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
2. Luôn đối chiếu theo mô tả lúc đặt (listing_at_order), KHÔNG bị đánh lừa nếu shop đã sửa mô tả sau khi bán; ngược lại nếu sản phẩm và tem nhãn khớp 100% mô tả lúc đặt thì giải thích trung lập rằng shop giao đúng mô tả, không ép shop thua oan.
3. Không tự duyệt hoàn nếu đơn > 300.000đ, quá hạn sàn, tài khoản hoàn >= 3 lần/90 ngày, nghi hàng giả, hoặc thiếu bằng chứng mở hộp.
4. Tuyệt đối KHÔNG cung cấp số điện thoại, địa chỉ cá nhân của người bán/người mua (0% PII).
5. Không hứa khoá shop hay bồi thường ngoài giá trị đơn; không nhượng bộ lời doạ 1 sao/bóc phốt.
6. Nếu thiếu mã đơn hàng, hỏi lại ngắn gọn mã đơn (ORD-XXX) thay vì tự đoán."""

_PHONE_RE = re.compile(r"(?<!\d)(?:\+84|0)(?:[\s.\-]?\d){8,10}(?!\d)")

_ACTION_BADGES = {
    "guide_return": ("ok", "✅ Đủ điều kiện hướng dẫn trả hàng"),
    "need_evidence": ("warn", "📎 Cần bổ sung bằng chứng mở hộp"),
    "escalate": ("human", "👤 Chuyển nhân viên sàn duyệt"),
    "reject_and_escalate": ("danger", "🚫 Từ chối ngoài chính sách · Chuyển nhân viên"),
    "reject_expired": ("danger", "⏰ Quá hạn trả hàng theo chính sách sàn"),
    "reject_policy_or_pii": ("danger", "🚫 Từ chối yêu cầu ngoài thẩm quyền / PII"),
    "ask_order_id": ("warn", "❓ G10 · Cần bổ sung mã đơn hàng"),
    "not_found": ("danger", "🔍 Không tìm thấy mã đơn trong hệ thống"),
}


def _extract_order_id(text: str) -> str:
    m = re.search(r"\bORD[-_ ]?(\d{3,})\b", text or "", flags=re.IGNORECASE)
    if m:
        return "ORD-%s" % m.group(1)
    return ""


def _detect_early_pii_or_scope(text: str) -> list:
    tl = (text or "").lower()
    flags = []
    if any(k in tl for k in ("số điện thoại", "sđt", "sdt", "số đt", "địa chỉ nhà", "địa chỉ shop", "địa chỉ riêng")):
        flags.append("pii_request")
    if any(k in tl for k in ("khoá", "khóa", "chặn tài khoản", "bồi thường thêm")):
        flags.append("out_of_scope_penalty_or_compensation")
    return flags


def _infer_has_evidence(text: str, history: list, order: dict) -> bool:
    combined = ((text or "") + " " + " ".join(m.get("content", "") for m in (history or []))).lower()
    ev_field = (order.get("evidence_status") or "").lower()
    if "chưa cung cấp" in ev_field:
        return any(k in combined for k in ("đã quay video", "đã chụp ảnh", "có video", "có ảnh", "gửi video", "gửi ảnh"))
    return True


def _sanitize_and_verify(reply_text: str, ticket: dict = None) -> str:
    """Hậu kiểm code: 0% lộ SĐT và luôn đảm bảo hiển thị mã phiếu chuyển người nếu có."""
    cleaned = _PHONE_RE.sub("[đã ẩn thông tin liên hệ]", reply_text or "")
    if ticket and ticket.get("ticket_id") and ticket["ticket_id"] not in cleaned:
        cleaned = "%s\n\n[Phiếu chuyển nhân viên sàn: %s · %s]" % (cleaned, ticket["ticket_id"], ticket["status"])
    return cleaned


def _format_history(history: list) -> str:
    if not history:
        return ""
    recent = history[-4:]
    lines = []
    for item in recent:
        role = "Người mua" if item.get("role") == "user" else "Trợ lý"
        lines.append("- %s: %s" % (role, (item.get("content") or "")[:300]))
    return "Ngữ cảnh các lượt trước trong phiên:\n" + "\n".join(lines) + "\n\n"


def _build_seller_view(order: dict, listing: dict, rules: dict, ticket: dict) -> dict:
    """Tổng hợp góc nhìn phía Người bán / Đối soát Shop từ cùng quyết định trung lập."""
    flags = rules.get("flags", [])
    is_serial = "serial_returner" in flags
    modified = listing.get("modified_after_order", False)
    if ticket:
        protection = "Cần shop theo dõi / chờ nhân viên sàn phân xử"
    elif rules.get("action") == "reject_expired":
        protection = "Shop được bảo vệ — đơn đã quá hạn trả hàng sàn"
    elif rules.get("action") == "need_evidence":
        protection = "Shop được tạm bảo vệ — yêu cầu khách bổ sung video mở hộp"
    else:
        protection = "Đối chiếu trung lập — nếu hàng khớp mô tả lúc đặt thì không ép hoàn lỗi shop"

    risk_notes = []
    if is_serial:
        risk_notes.append(
            "CẢNH BÁO SERIAL RETURNER: Người mua %s đã hoàn %s/%s đơn trong 90 ngày (nhóm 1,8%% hoàn lặp lại chiếm 45,6%% ca hoàn)."
            % (order["buyer_id"], order["buyer_returns_90d"], order["buyer_total_orders_90d"])
        )
    if order["platform"] == "shopee":
        risk_notes.append(
            "Rủi ro tài chính Shopee: hoàn thành công có thể phát sinh phí ship hoàn (18.300–40.000đ) và nguy cơ âm escrow_amount (873/1.305 ca trong dữ liệu thật)."
        )
    if modified:
        risk_notes.append("Lưu ý minh bạch: Mô tả sản phẩm hiện tại đã khác mô tả lúc đặt — sàn sẽ xử theo mô tả lúc đặt.")
    if not risk_notes:
        risk_notes.append("Không phát hiện dấu hiệu hoàn lặp lại; đối soát bình thường theo chính sách sàn.")

    return {
        "shop_id": order.get("shop_id", "SHOP"),
        "protection_status": protection,
        "response_sla": "Shop có 24–48h để phản hồi / cung cấp video đóng gói nếu không đồng ý khiếu nại.",
        "risk_notes": risk_notes,
        "ticket_id": ticket["ticket_id"] if ticket else None,
        "pii_blocked": "Đã chặn cung cấp SĐT/địa chỉ cá nhân giữa hai bên.",
    }


def answer(text: str, history: list = None) -> dict:
    """Hàm chính xử lý yêu cầu trả hàng/hoàn tiền. history=None giữ stateless cho eval & simulate."""
    user_text = (text or "").strip()
    hist_str = _format_history(history)
    early_flags = _detect_early_pii_or_scope(user_text)

    order_id = _extract_order_id(user_text)
    inherited_order = False
    if not order_id and history:
        for item in reversed(history):
            found_prev = _extract_order_id(item.get("content", ""))
            if found_prev:
                order_id = found_prev
                inherited_order = True
                break

    # Chặn yêu cầu xin PII / đòi khoá shop ngay cả khi người dùng không nhập mã đơn
    if early_flags and not order_id:
        note("early guard: %s" % ",".join(early_flags))
        prompt = (
            "%sNgười mua đang gửi yêu cầu bị cấm hoặc ngoài thẩm quyền (%s) và không nêu mã đơn.\n"
            "Hãy từ chối rõ ràng yêu cầu xin SĐT/địa chỉ cá nhân hoặc đòi khoá shop/bồi thường thêm, "
            "nhắc người mua thực hiện qua Trung tâm Trả hàng của sàn và hỏi mã đơn nếu cần kiểm tra đơn cụ thể.\n\n"
            "Tin nhắn người mua: %s" % (hist_str, ", ".join(early_flags), user_text)
        )
        reply = call_model(SYSTEM, prompt)
        out = _sanitize_and_verify(reply["text"])
        if reply.get("model") == "fake":
            out = "%s\n[Khung kiểm quy tắc: action=reject_policy_or_pii | flags=%s]" % (out, ",".join(early_flags))
        code, label = _ACTION_BADGES["reject_policy_or_pii"]
        return {
            "output": out,
            "meta": {
                "order_id": None,
                "decision_code": code,
                "decision_label": label,
                "action": "reject_policy_or_pii",
                "flags": early_flags,
            },
        }

    if not order_id:
        note("G10: thieu ma don, hoi lai")
        prompt = (
            "%sNgười mua chưa cung cấp mã đơn hàng (dạng ORD-XXX).\n"
            "Hãy hỏi lại lịch sự mã đơn hàng (và sàn Shopee/TikTok, bằng chứng nếu có), tuyệt đối không tự đoán đơn hàng.\n\n"
            "Tin nhắn người mua: %s" % (hist_str, user_text)
        )
        reply = call_model(SYSTEM, prompt)
        out = _sanitize_and_verify(reply["text"])
        if reply.get("model") == "fake":
            out = "%s\n[Khung kiểm quy tắc: action=ask_order_id | flags=missing_order_id]" % out
        code, label = _ACTION_BADGES["ask_order_id"]
        return {
            "output": out,
            "meta": {
                "order_id": None,
                "decision_code": code,
                "decision_label": label,
                "action": "ask_order_id",
                "flags": ["missing_order_id"],
            },
        }

    order = get_order(order_id)
    if not order.get("found"):
        note("khong tim thay ma don %s" % order_id)
        prompt = (
            "%sKhông tìm thấy mã đơn %s trong dữ liệu hệ thống.\n"
            "Hãy nói rõ không tìm thấy mã đơn này và hướng dẫn người mua kiểm tra lại mã đơn trên app, không bịa đặt.\n\n"
            "Tin nhắn người mua: %s" % (hist_str, order_id, user_text)
        )
        reply = call_model(SYSTEM, prompt)
        out = _sanitize_and_verify(reply["text"])
        if reply.get("model") == "fake":
            out = "%s\n[Khung kiểm quy tắc: %s | action=not_found | flags=order_not_found]" % (out, order_id)
        code, label = _ACTION_BADGES["not_found"]
        return {
            "output": out,
            "meta": {
                "order_id": order_id,
                "decision_code": code,
                "decision_label": label,
                "action": "not_found",
                "flags": ["order_not_found"],
            },
        }

    listing = get_listing_at_order(order_id)
    policy = get_policy(order["platform"], "")
    history_stats = get_complaint_history(order["buyer_id"])
    has_evidence = _infer_has_evidence(user_text, history if inherited_order else None, order)
    combined_claim = user_text
    if inherited_order and history:
        combined_claim = " ".join(m.get("content", "") for m in history[-3:] if m.get("role") == "user") + " " + user_text
    rules = check_return_rules(order_id, combined_claim, has_evidence)

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
        % (history_stats["buyer_id"], history_stats["total_orders_90d"], history_stats["returns_90d"], history_stats["is_serial_returner"]),
        "Kết quả kiểm quy tắc bằng code (check_return_rules): action=%s | hạn áp dụng=%s ngày | flags=%s"
        % (rules["action"], rules["max_days"], ", ".join(rules["flags"]) or "none"),
    ]
    if ticket:
        context_lines.append("Phiếu chuyển nhân viên nháp: %s (%s)" % (ticket["ticket_id"], ticket["status"]))

    prompt = (
        "%sCăn cứ đã đối chiếu:\n%s\n\n"
        "Tin nhắn người mua:\n%s\n\n"
        "Yêu cầu trả lời ngắn gọn, trung lập bằng tiếng Việt: "
        "(1) kết luận hướng xử lý theo đúng action & chính sách sàn, "
        "(2) trích dẫn đối chiếu với mô tả lúc đặt (listing_at_order) và mốc ngày giao, "
        "(3) bước tiếp theo cụ thể (nếu có phiếu chuyển nhân viên thì ghi rõ mã phiếu %s)."
        % (hist_str, "\n".join(context_lines), user_text, ticket["ticket_id"] if ticket else "không có")
    )
    reply = call_model(SYSTEM, prompt)
    out = _sanitize_and_verify(reply["text"], ticket)

    if reply.get("model") == "fake":
        out = "%s\n[Khung kiểm quy tắc: %s | action=%s | flags=%s]" % (
            out,
            order_id,
            rules["action"],
            ",".join(rules["flags"]) or "ok",
        )

    code, label = _ACTION_BADGES.get(rules["action"], ("ok", "Đã xử lý"))
    return {
        "output": out,
        "meta": {
            "order_id": order_id,
            "decision_code": code,
            "decision_label": label,
            "action": rules["action"],
            "flags": rules["flags"],
            "order": order,
            "listing": listing,
            "policy": policy,
            "history": history_stats,
            "rules": rules,
            "ticket": ticket,
            "seller_view": _build_seller_view(order, listing, rules, ticket),
        },
    }
