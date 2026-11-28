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
1. Chỉ dựa trên dữ liệu công cụ cung cấp: tuyệt đối KHÔNG bịa thông tin đơn hàng, KHÔNG bịa phần trăm phí vận chuyển/phí xử lý, KHÔNG bịa số hotline (như 1900...), KHÔNG yêu cầu người mua gửi email hay số điện thoại cá nhân.
2. Luôn trích dẫn NGUYÊN VĂN các thông số/chất liệu quan trọng từ mô tả lúc đặt (như chất liệu 100% cotton, tổng dung tích vỏ 6 lít / lòng nồi 5 lít, 1.5L inox 201, dài 68cm...). Nếu shop đã sửa mô tả sau khi bán, phải khẳng định rõ quyền trả hàng được xét theo đúng mô tả lúc đặt (KHÔNG lấy mô tả mới sửa). CHỈ giải thích trung lập rằng shop giao đúng mô tả khi sản phẩm thực nhận nguyên vẹn và khớp thông số/tem nhãn; ngược lại với hàng bị hư hỏng/móp vỡ do vận chuyển, giao thiếu món hoặc sai mẫu mà có video mở hộp trong hạn sàn, KHÔNG được viết "shop không chịu trách nhiệm", phải khẳng định người mua vẫn thuộc phạm vi bảo vệ trả hàng/hoàn tiền của sàn.
3. Không tự duyệt hoàn nếu đơn > 300.000đ, quá hạn sàn, tài khoản hoàn >= 3 lần/90 ngày, nghi hàng giả, hoặc thiếu bằng chứng mở hộp. Khi quá hạn sàn, phải dùng rõ cụm "từ chối tự duyệt hoàn" và hướng dẫn liên hệ CSKH sàn; đồng thời luôn tách bạch rõ hạn TikTok Shop (đổi ý 6 ngày riêng với trả lỗi 15 ngày — không gộp chung hai mốc).
4. Tuyệt đối KHÔNG cung cấp số điện thoại, địa chỉ cá nhân của người bán/người mua (0% PII).
5. Không hứa khoá shop hay bồi thường ngoài giá trị đơn; không nhượng bộ lời doạ 1 sao/bóc phốt.
6. Nếu thiếu mã đơn hàng, hỏi lại ngắn gọn mã đơn (ORD-XXX) thay vì tự đoán.
7. Luôn trả lời 100% bằng tiếng Việt tự nhiên (tuyệt đối không viết tiêu đề hay câu tiếng Anh, không trộn từ tiếng Pháp/nước ngoài). Chỉ nêu câu từ chối xin PII hoặc khoá shop/bồi thường thêm khi người mua thực sự gửi yêu cầu đó, không chèn thừa vào các đơn trả hàng thông thường. KHÔNG in tên biến hay mã flag kỹ thuật nội bộ (như action=, guide_return, need_evidence, expired_return_window, suspected_counterfeit, listing_at_order, listing_current). Trả lời súc tích, rõ ý (khoảng 120–220 từ)."""

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
    if re.search(r"(?<!\w)(?:khoá|khóa)(?!\w)", tl) or any(k in tl for k in ("chặn tài khoản", "bồi thường thêm")):
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


def _fmt_vnd(amount: int) -> str:
    return f"{int(amount):,}".replace(",", ".") + "đ"


def _build_seller_view(order: dict, listing: dict, rules: dict, ticket: dict) -> dict:
    """Tổng hợp góc nhìn phía Người bán & Bảng phân tích rủi ro Shop từ phân phối 127.546 dòng vietnam_ecommerce."""
    flags = rules.get("flags", [])
    action = rules.get("action", "")
    is_serial = "serial_returner" in flags
    modified = bool(listing.get("modified_after_order", False))
    plat = order.get("platform", "shopee")
    amt = int(order.get("amount_vnd", 0))
    cat = order.get("category", "")
    cat_l = cat.lower()

    if ticket:
        protection = "Cần shop theo dõi / chờ nhân viên sàn phân xử"
    elif action == "reject_expired":
        protection = "Shop được bảo vệ — đơn đã quá hạn trả hàng sàn"
    elif action == "need_evidence":
        protection = "Shop được tạm bảo vệ — yêu cầu khách bổ sung video mở hộp"
    else:
        protection = "Đối chiếu trung lập — nếu hàng khớp mô tả lúc đặt thì không ép hoàn lỗi shop"

    buyer_total = int(order.get("buyer_total_orders_90d", 0))
    buyer_ret = int(order.get("buyer_returns_90d", 0))
    buyer_rate_pct = round(buyer_ret * 100.0 / buyer_total, 1) if buyer_total > 0 else 0.0
    platform_avg_pct = 6.37 if plat == "shopee" else 1.35
    ratio_vs_platform = round(buyer_rate_pct / platform_avg_pct, 1) if platform_avg_pct > 0 else 0.0

    if "thời trang" in cat_l or "giày" in cat_l:
        category_risk = "Cao (5,06%–11,93% ở data thật, ~10× nhóm trà)"
        cat_pts = 10
    elif "thực phẩm" in cat_l or "trà" in cat_l:
        category_risk = "Thấp (0,52% ở nhóm trà data thật)"
        cat_pts = 0
    else:
        category_risk = "Trung bình (1,35%–6,37% theo sàn)"
        cat_pts = 5

    score = cat_pts
    if is_serial:
        score += 35
    if modified:
        score += 30
    if "suspected_counterfeit" in flags:
        score += 25
    if "over_auto_limit_300k" in flags:
        score += 20
    if "threat_or_refund_without_return" in flags:
        score += 20
    if plat == "shopee":
        score += 15
    risk_score = min(100, score)

    if risk_score >= 55:
        risk_level, risk_code = "CAO", "danger"
    elif risk_score >= 25:
        risk_level, risk_code = "TRUNG BÌNH", "warn"
    else:
        risk_level, risk_code = "THẤP", "ok"

    amt_str = _fmt_vnd(amt)
    if plat == "shopee":
        financial_exposure_label = f"{amt_str} + 18.300–40.000đ ship hoàn"
        financial_note = "66,9% ca hoàn Shopee âm escrow_amount (873/1.305 dòng thật)"
    else:
        financial_exposure_label = f"{amt_str} GMV đơn"
        financial_note = "44,6% sai size/mô tả · 38,2% đổi ý · 13,4% lỗi/hư hỏng (1.132 ca thật)"

    risk_notes = []
    if is_serial:
        risk_notes.append(
            "CẢNH BÁO SERIAL RETURNER: Người mua %s đã hoàn %s/%s đơn trong 90 ngày (%.1f%% — gấp %.1f× TB sàn; nhóm 1,81%% hoàn lặp tạo 45,63%% tổng ca hoàn)."
            % (order["buyer_id"], buyer_ret, buyer_total, buyer_rate_pct, ratio_vs_platform)
        )
    if plat == "shopee":
        risk_notes.append(
            "Rủi ro tài chính Shopee: hoàn thành công có thể phát sinh phí ship hoàn (18.300–40.000đ) và nguy cơ âm escrow_amount (873/1.305 ca trong dữ liệu thật)."
        )
    else:
        risk_notes.append(
            "Phân bố TikTok thật (1.132 ca): 44,61%% sai size/mô tả · 38,16%% đổi ý (hạn 6 ngày) · 13,43%% gửi sai/thiếu/hư hỏng/nghi giả."
        )
    if modified:
        risk_notes.append("Lưu ý minh bạch: Mô tả sản phẩm hiện tại đã khác mô tả lúc đặt — sàn sẽ xử theo mô tả lúc đặt (rủi ro thua tranh chấp cao).")
    if "suspected_counterfeit" in flags:
        risk_notes.append("Cảnh báo nghi hàng giả: Bắt buộc chuẩn bị hoá đơn/chứng từ nguồn gốc hàng chính hãng cho bộ phận chuyên trách sàn.")
    if "threat_or_refund_without_return" in flags:
        risk_notes.append("Khách đe doạ 1 sao / đòi hoàn không trả hàng: Sàn không ép hoàn không trả hàng khi chưa có đồng ý của shop.")
    if action == "reject_expired":
        risk_notes.append("Đơn đã quá hạn %s ngày của sàn (%s ngày sau giao) — shop có căn cứ từ chối tự động." % (rules.get("max_days"), order.get("delivered_days_ago")))

    checklist = [
        "1. Xuất video đóng gói có mã vận đơn & cân nặng kiện hàng tại thời điểm gửi đi.",
        "2. Đối chiếu tem mác/thông số hàng giao với bản mô tả lúc đặt (\"%s\")." % listing.get("listing_at_order", ""),
    ]
    if ticket:
        checklist.append("3. Theo dõi phiếu %s trên Trung tâm Người bán và gửi phản hồi trong vòng 24–48h." % ticket["ticket_id"])
    elif action == "need_evidence":
        checklist.append("3. Tạm chờ người mua bổ sung video mở hộp nguyên seal; chưa bấm hoàn tiền khi chưa đủ bằng chứng.")
    elif action == "reject_expired":
        checklist.append("3. Lưu ảnh mốc ngày giao (%s ngày > hạn %s ngày) để đóng khiếu nại đúng hạn sàn." % (order.get("delivered_days_ago"), rules.get("max_days")))
    else:
        checklist.append("3. Xác nhận nhận lại hàng nguyên vẹn tem mác trước khi sàn giải ngân hoàn tiền (trong 24–48h).")

    ticket_str = ticket["ticket_id"] if ticket else "Chưa tạo phiếu chuyển"
    dispute_template = (
        "BIÊN BẢN ĐỐI SOÁT ĐƠN %s (%s · %s)\n"
        "- Đơn vị bán: %s | Giá trị đơn: %s | Trạng thái: %s\n"
        "- Căn cứ mô tả lúc đặt: \"%s\" (%s)\n"
        "- Lịch sử người mua 90d: %s/%s đơn hoàn (%.1f%%)\n"
        "- Đề nghị phía Shop trong hạn 24–48h: Cung cấp video đóng gói đối chiếu tem mác và xác nhận hướng xử lý theo phiếu [%s]."
    ) % (
        order.get("order_id", ""),
        plat.upper(),
        cat,
        order.get("shop_id", "SHOP"),
        amt_str,
        protection,
        listing.get("listing_at_order", ""),
        "Cảnh báo: đã sửa mô tả sau khi bán" if modified else "Mô tả nhất quán với bản gốc",
        buyer_ret,
        buyer_total,
        buyer_rate_pct,
        ticket_str,
    )

    return {
        "order_id": order.get("order_id", ""),
        "platform": plat,
        "amount_vnd": amt,
        "category": cat,
        "shop_id": order.get("shop_id", "SHOP"),
        "protection_status": protection,
        "response_sla": "Shop có 24–48h để phản hồi / cung cấp video đóng gói nếu không đồng ý khiếu nại.",
        "risk_level": risk_level,
        "risk_code": risk_code,
        "risk_score": risk_score,
        "buyer_ret": buyer_ret,
        "buyer_total": buyer_total,
        "buyer_rate_pct": buyer_rate_pct,
        "platform_avg_pct": platform_avg_pct,
        "ratio_vs_platform": ratio_vs_platform,
        "category_risk": category_risk,
        "listing_modified": modified,
        "financial_exposure_label": financial_exposure_label,
        "financial_note": financial_note,
        "risk_notes": risk_notes,
        "dispute_checklist": checklist,
        "dispute_template": dispute_template,
        "ticket_id": ticket["ticket_id"] if ticket else None,
        "ticket_reason": ticket.get("reason", "") if ticket else "",
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
            "%sNgười mua đang gửi yêu cầu ngoài phạm vi được phép (xin số điện thoại/địa chỉ cá nhân hoặc đòi khoá shop/bồi thường thêm) và chưa nêu mã đơn.\n"
            "Yêu cầu trả lời 100%% bằng tiếng Việt, ngắn gọn (tối đa 160 từ), không in mã kỹ thuật:\n"
            "(1) Từ chối rõ ràng yêu cầu cung cấp số điện thoại/địa chỉ cá nhân (bảo mật thông tin) và/hoặc từ chối yêu cầu khoá shop, bồi thường ngoài đơn,\n"
            "(2) Hướng dẫn thực hiện qua Trung tâm Trả hàng / Hoàn tiền chính thức trên ứng dụng Shopee hoặc TikTok Shop,\n"
            "(3) Hỏi thêm mã đơn hàng (dạng ORD-XXX) nếu người mua muốn kiểm tra điều kiện trả hàng cụ thể.\n\n"
            "Tin nhắn người mua: %s" % (hist_str, user_text)
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
            "Hãy trả lời 100%% bằng tiếng Việt, ngắn gọn (tối đa 120 từ): hỏi lịch sự mã đơn hàng (dạng ORD-XXX), tên sàn (Shopee/TikTok Shop) và ảnh/video nếu có; tuyệt đối không tự đoán đơn hàng hay bịa thông tin.\n\n"
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
            "Hãy trả lời 100%% bằng tiếng Việt, ngắn gọn (tối đa 140 từ): nói rõ hệ thống không tìm thấy mã đơn %s và hướng dẫn người mua kiểm tra lại mã đơn trong mục Đơn hàng trên app, tuyệt đối không bịa thông tin đơn.\n\n"
            "Tin nhắn người mua: %s" % (hist_str, order_id, order_id, user_text)
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

    action_text_map = {
        "guide_return": "Đủ điều kiện hướng dẫn trả hàng hợp lệ",
        "need_evidence": "Chưa duyệt ngay — yêu cầu người mua bổ sung ảnh/video mở hộp",
        "escalate": "Không tự duyệt hoàn — chuyển nhân viên sàn xem xét trung lập",
        "reject_and_escalate": "Từ chối yêu cầu ngoài chính sách/ngoài thẩm quyền và chuyển nhân viên sàn",
        "reject_expired": "Từ chối tự duyệt vì đã quá thời hạn trả hàng của sàn",
        "reject_policy_or_pii": "Từ chối yêu cầu xin thông tin cá nhân (PII) / ngoài thẩm quyền",
    }
    flag_text_map = {
        "pii_request": "người mua xin số điện thoại/địa chỉ cá nhân (bắt buộc từ chối)",
        "out_of_scope_penalty_or_compensation": "đòi khoá shop hoặc bồi thường thêm ngoài đơn (bắt buộc từ chối)",
        "threat_or_refund_without_return": "đe doạ đánh giá 1 sao / đòi hoàn tiền không trả hàng (không nhượng bộ)",
        "suspected_counterfeit": "nghi ngờ hàng giả (chuyển bộ phận chuyên trách)",
        "expired_return_window": "đã quá hạn trả hàng áp dụng của sàn",
        "over_auto_limit_300k": "giá trị đơn vượt hạn mức tự hướng dẫn 300.000đ",
        "serial_returner": "tài khoản đã hoàn >= 3 lần trong 90 ngày gần đây",
        "listing_modified_after_order": "shop đã sửa mô tả sản phẩm sau khi bán (bắt buộc xét theo mô tả lúc đặt)",
        "missing_evidence": "chưa có ảnh/video mở hộp",
    }
    human_action = action_text_map.get(rules["action"], rules["action"])
    human_flags = ", ".join(flag_text_map.get(f, f) for f in rules["flags"]) or "không có cảnh báo đặc biệt"

    context_lines = [
        "Đơn hàng: %s | Sàn: %s | Sản phẩm: %s | Giá: %sđ | Đã giao: %s ngày trước"
        % (order_id, order["platform"].upper(), order["item_name"], f"{order['amount_vnd']:,}", order["delivered_days_ago"]),
        "Mô tả lúc người mua đặt hàng (bản gốc dùng để đối chiếu): %s" % listing.get("listing_at_order", ""),
        "Mô tả hiện tại trên sàn: %s (%s)"
        % (listing.get("listing_current", ""), "ĐÃ BỊ SỬA SAU KHI BÁN" if listing.get("modified_after_order") else "không thay đổi"),
        "Trạng thái bằng chứng hiện có: %s" % order.get("evidence_status", ""),
        "Chính sách %s: hạn trả lỗi %s ngày | hạn đổi ý %s ngày | hạn mức tự hướng dẫn %sđ"
        % (policy["name"], policy["return_window_days"], policy["change_of_mind_days"], f"{policy['auto_approve_limit_vnd']:,}"),
        "Lịch sử tài khoản mua: %s đơn / %s lần hoàn trong 90 ngày (nhóm hoàn lặp lại >= 3 lần: %s)"
        % (history_stats["total_orders_90d"], history_stats["returns_90d"], "CÓ" if history_stats["is_serial_returner"] else "không"),
        "Quyết định đối soát bắt buộc: %s | Hạn áp dụng cho yêu cầu này: %s ngày | Lưu ý: %s"
        % (human_action, rules["max_days"], human_flags),
    ]
    if listing.get("modified_after_order"):
        context_lines.append(
            "CHÚ Ý QUAN TRỌNG: Shop đã sửa mô tả sau khi khách đặt. Bắt buộc trích nguyên văn mô tả lúc đặt (\"%s\") và khẳng định người mua được bảo vệ theo bản lúc đặt."
            % listing.get("listing_at_order", "")
        )
    if ticket:
        context_lines.append("Phiếu chuyển nhân viên nháp: %s (trạng thái chờ nhân viên sàn duyệt)" % ticket["ticket_id"])

    prompt = (
        "%sCăn cứ đã đối chiếu:\n%s\n\n"
        "Tin nhắn người mua:\n%s\n\n"
        "Hãy trả lời 100%% bằng tiếng Việt tự nhiên, súc tích (khoảng 120–220 từ), thái độ trung lập:\n"
        "(1) Nêu rõ kết luận theo đúng 'Quyết định đối soát bắt buộc' (từ chối rõ yêu cầu xin SĐT/địa chỉ, khoá shop, bồi thường thêm hoặc hoàn không trả hàng nếu có),\n"
        "(2) Trích dẫn NGUYÊN VĂN các thông số/chất liệu quan trọng từ 'Mô tả lúc người mua đặt hàng' (nếu hàng nguyên vẹn khớp mô tả thì giải thích trung lập shop giao đúng; nếu bị hư hỏng/móp vỡ vận chuyển/giao thiếu/sai thì khẳng định người mua vẫn được sàn bảo vệ hoàn tiền; nếu mô tả đã sửa thì khẳng định xét theo bản lúc đặt) kèm mốc %s/%s ngày,\n"
        "(3) Nêu bước tiếp theo cụ thể%s.\n"
        "CẤM: không viết tiếng Anh hay trộn ngoại ngữ, không bịa %% phí hoàn hay số hotline, không xin email/SĐT của khách, không in mã flag kỹ thuật tiếng Anh."
        % (
            hist_str,
            "\n".join(context_lines),
            user_text,
            order["delivered_days_ago"],
            rules["max_days"],
            (" và ghi rõ mã phiếu %s" % ticket["ticket_id"]) if ticket else "",
        )
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
