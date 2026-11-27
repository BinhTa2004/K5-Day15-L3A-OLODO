"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá:
        "text", "model", "tokens_in", "tokens_out"

Hỗ trợ qua .env (KHÔNG commit .env):
    MODEL_PROVIDER = fake | openai | groq | openrouter | deepseek | gemini | anthropic | ollama
    MODEL_NAME     = mã model (vd gpt-4o-mini, gemini-2.5-flash, llama-3.3-70b-versatile...)
    API_KEY        = key của nhóm (không cần với fake / ollama)
    API_BASE_URL   = (tuỳ chọn) ghi đè URL cho provider tương thích OpenAI
"""
import json
import os
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = os.environ.get("SHOW_RAW", "").strip() == "1"


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()
API_BASE_URL = (os.environ.get("API_BASE_URL") or "").strip()

OPENAI_COMPAT_URLS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions",
}


def post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    """Gửi POST JSON bằng thư viện chuẩn urllib, trả về dict phản hồi."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=dict({"Content-Type": "application/json", "User-Agent": "OLODO-Hackathon/1.0"}, **headers),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %d: %s" % (e.code, e.read().decode("utf-8", "replace")[:350]))
    if SHOW_RAW:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    return data


def _call_openai_compat(url: str, system: str, user: str) -> dict:
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    headers = {"Authorization": "Bearer " + API_KEY}
    data = post_json(url, headers, {"model": MODEL_NAME, "messages": messages, "temperature": 0.2})
    usage = data.get("usage") or {}
    return {
        "text": data["choices"][0]["message"]["content"],
        "tokens_in": int(usage.get("prompt_tokens", 0)),
        "tokens_out": int(usage.get("completion_tokens", 0)),
    }


def _call_gemini(system: str, user: str) -> dict:
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s" % (MODEL_NAME, API_KEY)
    body = {
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.2},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = post_json(url, {}, body)
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts")) or []
    text = "".join(p.get("text", "") for p in parts if "text" in p)
    usage = data.get("usageMetadata") or {}
    tokens_in = int(usage.get("promptTokenCount", 0))
    tokens_out = int(usage.get("candidatesTokenCount", 0)) + int(usage.get("thoughtsTokenCount", 0))
    return {"text": text, "tokens_in": tokens_in, "tokens_out": tokens_out}


def _call_anthropic(system: str, user: str) -> dict:
    url = "https://api.anthropic.com/v1/messages"
    body = {
        "model": MODEL_NAME,
        "max_tokens": 1024,
        "system": system or "",
        "messages": [{"role": "user", "content": user}],
    }
    data = post_json(url, {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"}, body)
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    usage = data.get("usage") or {}
    return {"text": text, "tokens_in": int(usage.get("input_tokens", 0)), "tokens_out": int(usage.get("output_tokens", 0))}


def _call_ollama(system: str, user: str) -> dict:
    url = API_BASE_URL or "http://localhost:11434/api/chat"
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(url, {}, {"model": MODEL_NAME, "messages": messages, "stream": False}, timeout=300)
    return {
        "text": data["message"]["content"],
        "tokens_in": int(data.get("prompt_eval_count", 0)),
        "tokens_out": int(data.get("eval_count", 0)),
    }


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:80], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    if MODEL_PROVIDER != "ollama" and not API_KEY:
        raise RuntimeError("Thiếu API_KEY trong file .env cho MODEL_PROVIDER=%s" % MODEL_PROVIDER)
    if not MODEL_NAME:
        raise RuntimeError("Thiếu MODEL_NAME trong file .env cho MODEL_PROVIDER=%s" % MODEL_PROVIDER)

    if MODEL_PROVIDER in OPENAI_COMPAT_URLS:
        url = API_BASE_URL or OPENAI_COMPAT_URLS[MODEL_PROVIDER]
        r = _call_openai_compat(url, system, user)
    elif MODEL_PROVIDER == "gemini":
        r = _call_gemini(system, user)
    elif MODEL_PROVIDER == "anthropic":
        r = _call_anthropic(system, user)
    elif MODEL_PROVIDER == "ollama":
        r = _call_ollama(system, user)
    else:
        raise NotImplementedError("Chưa hỗ trợ MODEL_PROVIDER=%s trong codebase/ai.py" % MODEL_PROVIDER)

    return {
        "text": r["text"],
        "model": MODEL_NAME,
        "tokens_in": int(r["tokens_in"]),
        "tokens_out": int(r["tokens_out"]),
    }
