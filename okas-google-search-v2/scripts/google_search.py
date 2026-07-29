#!/usr/bin/env python3
"""
KAS Google Search V2 — ค้นหาข้อมูลผ่าน Gemini + Google Search Grounding
                   แบบมีแหล่งอ้างอิง + ป้องกัน hallucination อัตโนมัติ
Usage: python google_search.py "query here"
Prerequisite: API key in ~/AppData/Local/hermes/.env (GOOGLE_AI_API_KEY or GOOGLE_API_KEY)

Key feature: อ่าน .env file โดยตรง — ไม่พึ่ง environment variable
             (Hermes execute_code doesn't inherit .env, so we read the file ourselves)
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MODEL = "gemini-2.5-flash"  # ฟรี 1,500 req/day

# ══════════════════════════════════════════════════════════════
# KEY LOADING — ROBUST: read .env file directly
# ══════════════════════════════════════════════════════════════

def load_api_key() -> str:
    """Load Google AI API key from .env file (multiple locations, multiple key names)."""
    KEY_NAMES = ["GOOGLE_AI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"]
    ENV_PATHS = [
        Path.home() / "AppData" / "Local" / "hermes" / ".env",
        Path.home() / ".hermes" / ".env",
    ]
    # 1. Try environment variable first
    for name in KEY_NAMES:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    # 2. Try reading .env file directly
    for env_path in ENV_PATHS:
        if env_path.exists():
            try:
                content = env_path.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key in KEY_NAMES and value:
                            return value
            except Exception:
                continue
    return ""

API_KEY = load_api_key()

# ══════════════════════════════════════════════════════════════
# ANTI-HALLUCINATION PROMPT TEMPLATE
# ══════════════════════════════════════════════════════════════

ANTI_HALLUCINATION_TEMPLATE = """RULES (DO NOT BREAK):
1. ONLY report facts that are EXPLICITLY found in the search results.
2. If a source does NOT contain the target name/company/topic, DO NOT cite it.
3. For EACH fact, name the EXACT source domain (e.g. "sec.or.th", "set.or.th").
4. If you are UNSURE whether a fact applies to the right person/entity, say "UNCERTAIN" and explain why.
5. DO NOT connect unrelated information. A website only counts as a source if it DIRECTLY mentions the target.
6. If NO results found for a source, say "NOT FOUND" — do NOT fabricate.

QUESTION: {query}"""


def wrap_strict(query: str) -> str:
    """Wrap query with anti-hallucination rules."""
    return ANTI_HALLUCINATION_TEMPLATE.format(query=query)


# ══════════════════════════════════════════════════════════════
# CORE SEARCH
# ══════════════════════════════════════════════════════════════

def google_search(query: str) -> dict:
    """ค้นหาด้วย Gemini + Google Search Grounding (raw query, no template)."""
    if not API_KEY:
        return {"error": "🔑 ไม่พบ API Key — รัน setup_key.py เพื่อติดตั้ง key ก่อน"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text": query}]}],
        "tools": [{"google_search": {}}]
    }).encode()
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="ignore")
        try:
            err = json.loads(err_body)
            return {"error": err.get("error", {}).get("message", str(e)), "code": e.code}
        except json.JSONDecodeError:
            return {"error": err_body[:300], "code": e.code}
    except urllib.error.URLError as e:
        return {"error": f"🌐 Network error: {e.reason}", "code": None}


def search_strict(query: str) -> dict:
    """ค้นหาแบบ strict — ห่อ query ด้วย anti-hallucination template อัตโนมัติ."""
    return google_search(wrap_strict(query))


def search_and_return_json(query: str, strict: bool = True) -> dict:
    """Agent-friendly: returns dict with text, sources, and errors."""
    result = search_strict(query) if strict else google_search(query)
    if "error" in result:
        return {"error": result["error"], "code": result.get("code")}
    candidates = result.get("candidates", [])
    text_parts = []
    for c in candidates:
        for p in c.get("content", {}).get("parts", []):
            if "text" in p:
                text_parts.append(p["text"])
    gm = candidates[0].get("groundingMetadata", {}) if candidates else {}
    chunks = gm.get("groundingChunks", [])
    sources = []
    seen = set()
    for ch in chunks:
        w = ch.get("web", {})
        uri = w.get("uri", "?")
        if uri not in seen:
            sources.append({"title": w.get("title", "?"), "uri": uri})
            seen.add(uri)
    return {
        "text": "\n".join(text_parts),
        "sources": sources,
        "search_queries": gm.get("webSearchQueries", []),
    }


# ══════════════════════════════════════════════════════════════
# CLI FORMATTING
# ══════════════════════════════════════════════════════════════

def format_result(result: dict) -> str:
    """Format results with sources for CLI display."""
    if "error" in result:
        if result.get("code") == 403:
            return f"❌ Error (403): {result['error']}\n\n💡 วิธีแก้: API Key อาจหมดอายุหรือไม่มีสิทธิ์ → สร้าง key ใหม่ที่ https://aistudio.google.com/apikey"
        if result.get("code") == 429:
            return f"❌ Error (429): {result['error']}\n\n💡 วิธีแก้: ใช้เกิน Free Tier (1,500/day) → รอวันถัดไป หรือใช้ key อื่น"
        return f"❌ Error (HTTP {result.get('code', '?')}): {result['error']}"
    candidates = result.get("candidates", [])
    if not candidates:
        return "❌ ไม่พบผลลัพธ์ — ลองเปลี่ยนคำค้นหา"
    output = []
    for c in candidates:
        for p in c.get("content", {}).get("parts", []):
            if "text" in p:
                output.append(p["text"])
    gm = candidates[0].get("groundingMetadata", {})
    chunks = gm.get("groundingChunks", [])
    if chunks:
        output.append("\n=== 📎 แหล่งที่มา ===")
        seen = set()
        idx = 1
        for ch in chunks:
            w = ch.get("web", {})
            uri = w.get("uri", "?")
            if uri not in seen:
                output.append(f"{idx}. {w.get('title', 'ไม่ระบุชื่อ')}")
                output.append(f"   {uri}")
                seen.add(uri)
                idx += 1
    return "\n".join(output)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("🔍 Query: ")
    result = search_strict(query)
    print(format_result(result))
