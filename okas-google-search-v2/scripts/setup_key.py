#!/usr/bin/env python3
"""
KAS Google Search V2 — Setup Key
================================
ติดตั้ง Google AI API Key ลง .env แบบถาวร + ทดสอบทันที

Features:
  1. Validate key format (ต้องขึ้นต้นด้วย AIza หรือ AQ.)
  2. เขียนลง .env file → ลบ key เก่า (ถ้ามี) → เขียน key ใหม่
  3. ทดสอบ key โดยค้นหาจริง (query: "test search")
  4. แจ้งผล success/failure พร้อมวิธีแก้

Usage:
  python setup_key.py YOUR_API_KEY_HERE
  python setup_key.py AIzaSy...ยาวๆ...

Exit codes:
  0 = success (key installed + verified)
  1 = key format invalid
  2 = key install failed (write error)
  3 = key verification failed (API error)
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MODEL = "gemini-2.5-flash"


def validate_key(key: str) -> tuple:
    key = key.strip().strip('"').strip("'")
    if not key:
        return False, "❌ Key ว่างเปล่า — กรุณาวาง key ที่ copy จาก Google AI Studio"
    if len(key) < 30:
        return False, f"❌ Key สั้นเกินไป ({len(key)} ตัวอักษร) — key จริงควรยาว ~39 ตัว"
    if not (key.startswith("AIza") or key.startswith("AQ.")):
        return False, f"❌ Key format ไม่ถูกต้อง — ต้องขึ้นต้นด้วย 'AIza' หรือ 'AQ.' (key ของคุณขึ้นต้นด้วย '{key[:4]}...')"
    return True, key


def get_env_path() -> Path:
    if os.name == "nt":
        return Path.home() / "AppData" / "Local" / "hermes" / ".env"
    else:
        return Path.home() / ".hermes" / ".env"


def write_key_to_env(key: str) -> tuple:
    env_path = get_env_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing_lines = []
        if env_path.exists():
            existing_lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        KEY_NAMES = {"GOOGLE_AI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"}
        new_lines = []
        for line in existing_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                new_lines.append(line)
                continue
            if "=" in stripped:
                k = stripped.split("=", 1)[0].strip()
                if k in KEY_NAMES:
                    continue
            new_lines.append(line)
        new_lines.append(f"GOOGLE_AI_API_KEY={key}")
        content = "\n".join(new_lines).strip() + "\n"
        env_path.write_text(content, encoding="utf-8")
        return True, str(env_path)
    except Exception as e:
        return False, f"❌ เขียนไฟล์ไม่สำเร็จ: {e}"


def test_key(key: str) -> tuple:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    body = json.dumps({
        "contents": [{"parts": [{"text": "test search: hello world"}]}],
        "tools": [{"google_search": {}}]
    }).encode()
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        candidates = data.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            preview = text[:100].replace("\n", " ")
            return True, f"✅ ทดสอบสำเร็จ: {preview}..."
        else:
            block_reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
            return False, f"❌ API ตอบกลับแต่ไม่มีเนื้อหา — blockReason: {block_reason}"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="ignore")
        try:
            err = json.loads(err_body)
            msg = err.get("error", {}).get("message", str(e))
        except json.JSONDecodeError:
            msg = err_body[:200]
        code = e.code
        if code == 403:
            return False, f"❌ HTTP 403 (Permission Denied): {msg}\n\n💡 Key นี้ไม่มีสิทธิ์ใช้งาน หรือหมดอายุ → สร้าง key ใหม่ที่ https://aistudio.google.com/apikey"
        elif code == 429:
            return False, f"❌ HTTP 429 (Quota Exceeded): {msg}\n\n💡 ใช้เกิน Free Tier (1,500/day) → รอวันถัดไป หรือสร้าง key ใหม่ใน project อื่น"
        else:
            return False, f"❌ HTTP {code}: {msg}"
    except urllib.error.URLError as e:
        return False, f"❌ Network error: {e.reason}"
    except Exception as e:
        return False, f"❌ Unexpected error: {e}"


def main():
    print("=" * 60)
    print("🔑 KAS Google Search V2 — Setup Key")
    print("=" * 60)
    if len(sys.argv) < 2:
        print("❌ กรุณาระบุ API Key")
        print("Usage: python setup_key.py YOUR_API_KEY")
        print("\n💡 วิธีขอ key: https://aistudio.google.com/apikey")
        sys.exit(1)
    raw_key = " ".join(sys.argv[1:]).strip()
    print("\n[1/3] 🔍 ตรวจสอบ format key...")
    ok, key_or_msg = validate_key(raw_key)
    if not ok:
        print(key_or_msg)
        sys.exit(1)
    key = key_or_msg
    print(f"   ✅ Key format ถูกต้อง ({len(key)} ตัวอักษร)")
    print("\n[2/3] 💾 บันทึก key ลง .env...")
    ok, msg = write_key_to_env(key)
    if not ok:
        print(msg)
        sys.exit(2)
    print(f"   ✅ บันทึกสำเร็จ → {msg}")
    print("\n[3/3] 🧪 ทดสอบ key ด้วยการค้นหาจริง...")
    ok, detail = test_key(key)
    if not ok:
        print(detail)
        print("\n⚠️  Key ถูกบันทึกแล้ว แต่ทดสอบไม่ผ่าน — key อาจใช้ไม่ได้")
        sys.exit(3)
    print(f"   {detail}")
    print("\n" + "=" * 60)
    print("🎉 ติดตั้ง + ทดสอบสำเร็จ! พร้อมใช้งาน Google Search")
    print("=" * 60)


if __name__ == "__main__":
    main()
