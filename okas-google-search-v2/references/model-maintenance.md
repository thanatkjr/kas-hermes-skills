# Gemini Model Maintenance & Discovery

> อัปเดตล่าสุด: 13 Jul 2026 — `gemini-2.5-flash` ✅, `gemini-1.5-*` ❌

## วิธีตรวจสอบว่ามี models อะไรให้ใช้บ้าง

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_AI_API_KEY" \
  | python -c "
import sys,json
d=json.load(sys.stdin)
for m in d.get('models',[]):
    name=m.get('name','').replace('models/','')
    methods=m.get('supportedGenerationMethods',[])
    if 'generateContent' in methods:
        print(f'  {name} — {m.get(\"displayName\",\"\")}')"
```

หรือใช้ Python:

```python
import urllib.request, json
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
data = json.loads(urllib.request.urlopen(url).read())
for m in data["models"]:
    if "generateContent" in m.get("supportedGenerationMethods", []):
        print(m["name"].replace("models/", ""))
```

## วิธีทดสอบว่า model รองรับ `google_search` tool ไหม

```python
import urllib.request, json

model = "gemini-2.5-flash"  # เปลี่ยนเป็น model ที่ต้องการทดสอบ
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
body = json.dumps({
    "contents": [{"parts": [{"text": "test"}]}],
    "tools": [{"google_search": {}}]
}).encode()

try:
    resp = urllib.request.urlopen(urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}))
    data = json.loads(resp.read())
    chunks = data.get("candidates", [{}])[0].get("groundingMetadata", {}).get("groundingChunks", [])
    print(f"✅ {model}: OK — {len(chunks)} sources")
except urllib.error.HTTPError as e:
    print(f"❌ {model}: HTTP {e.code} — {e.read().decode(errors='ignore')[:200]}")
```

## Model Lifecycle — สิ่งที่เรียนรู้

- Google deprecates Gemini models เป็นระยะ (ทุก 6-12 เดือน)
- Model ที่ deprecated แล้วจะคืน 404 — `"is not found for API version v1beta"`
- Model ที่ถูกลบแล้ว:
  - `gemini-1.5-flash` — ❌ 404 (กลางปี 2026)
  - `gemini-1.5-pro` — ❌ 404
  - `gemini-2.5-flash-lite` — ❌ 404 ("no longer available to new users")

## 🔥 CRITICAL: Billing kills Free Tier

**"Once billing is enabled on a project for the Gemini API, the free tier disappears entirely, and all usage becomes billable."** [google.dev]

| Key Type | Free Tier | Models Available | Recommendation |
|----------|:---------:|------------------|----------------|
| **Old key (no billing)** | ✅ 1,500 req/day | `gemini-2.5-flash` | 🏆 BEST — keep using |
| **New key (billing enabled)** | ❌ — all billable | `gemini-3.6-flash`, `gemini-flash-latest` | Set budget alerts! |

### Key Type Detection

- `AIzaSy...` — from AI Studio (aistudio.google.com) — usually no billing, can use old models
- `AQ.Ab8...` — from Google Cloud OAuth — usually has billing, needs new models

### Model Compatibility Matrix (verified Jul 2026)

| Model | Old Key (no billing) | New Key (billing) | Search Grounding |
|-------|:---:|:---:|:---:|
| `gemini-2.5-flash` | ✅ | ❌ 404 deprecated | ✅ |
| `gemini-2.0-flash` | ✅ | ⚠️ 429 quota=0 | ✅ |
| `gemini-3.5-flash` | N/A | ✅ (503 busy) | ✅ |
| **`gemini-3.6-flash`** | N/A | ✅ **works** | ✅ 8 sources |
| `gemini-flash-latest` | N/A | ✅ | ✅ |

### What to tell users who just got a new key

```
⚠️ ถ้าได้ key ใหม่จาก AI Studio:
   - gemini-2.5-flash ใช้ไม่ได้ (Google เลิกให้ key ใหม่ใช้แล้ว)
   - ต้องใช้ gemini-3.6-flash หรือ gemini-flash-latest
   - ถ้าเปิด billing → free tier หาย → ทุก call เสียเงิน
   - ถ้ายังไม่เปิด billing → ใช้ gemini-2.0-flash แทนได้ (free tier)
```

### Budget Setup (when billing is unavoidable)

1. ไป https://console.cloud.google.com → Billing → Budgets & alerts
2. สร้าง budget → ตั้ง alert ที่ $1/month
3. ตั้ง quota limit ป้องกันใช้เกิน

### Cost Estimation (gemini-3.6-flash, billing-enabled)

| Metric | Value |
|--------|-------|
| Input tokens | $1.50 / 1M tokens |
| Output tokens | $7.50 / 1M tokens |
| Per search (~300 in + 500 out) | **~$0.0042 ≈ 0.14 THB** |
| 400 THB budget | **~2,800 searches** |
| 50 searches/day | ~210 THB/month |

### Debugging: env var shadowing .env

**Symptom:** ติดตั้ง key ใหม่ด้วย `setup_key.py` แล้ว แต่ script ยังใช้ key เก่า

**Root cause:** `load_api_key()` อ่าน environment variable ก่อน → เจอ key เก่าที่ค้างอยู่ใน env → ไม่เคยอ่าน .env เลย

**Fix (applied in v2.1):** กลับลำดับ — อ่าน `.env` file ก่อน, env var เป็น fallback

```python
# ❌ OLD (v2.0): env var first → shadowed .env
def load_api_key():
    for name in KEY_NAMES:
        val = os.environ.get(name, "").strip()
        if val: return val          # ← หยุดที่นี่! ไม่ถึง .env
    # ... never reaches .env read

# ✅ NEW (v2.1): .env file first → env var as fallback
def load_api_key():
    for env_path in ENV_PATHS:     # ← .env file first
        if env_path.exists():
            # ... read from file
            return value
    for name in KEY_NAMES:         # ← env var as fallback
        val = os.environ.get(name, "").strip()
        if val: return val
```

**How to detect:** 
```python
# Check BOTH sources
import os
from pathlib import Path
env_val = os.environ.get('GOOGLE_AI_API_KEY', '')
env_file = Path.home() / 'AppData/Local/hermes/.env'
for line in env_file.read_text().splitlines():
    if line.startswith('GOOGLE_AI_API_KEY='):
        file_val = line.split('=',1)[1].strip()
        break
if env_val[:10] != file_val[:10]:
    print(f'⚠️ MISMATCH: env={env_val[:10]}... vs .env={file_val[:10]}...')
    print('   → .env is source of truth, ignoring env var')
```

## เมื่อไหร่ควรอัปเดต MODELS list ใน `google_search.py`

- **ทุก 3-6 เดือน** — รัน discovery endpoint เช็คว่า models ใน list ยังอยู่ครบไหม
- **ถ้ามีคนแจ้ง error 404** — เช็คทันที
- **Google ประกาศ model ใหม่** — เพิ่มเป็น secondary/fallback

## Fallback Pattern ที่ใช้ใน v2.1

```python
MODELS = [
    "gemini-2.5-flash",      # primary: old keys (no billing) — ฟรี 1,500 req/day
    "gemini-3.6-flash",      # fallback: new keys (billing) — launched Jul 2026
    "gemini-flash-latest",   # fallback: always points to latest flash
    "gemini-2.0-flash",      # last resort: stable, rarely deprecated
]
```

Logic:
- 404 (model not found) → skip, try next
- 429 (quota exceeded) → skip, try next (quota pool คนละอัน)
- 403 (permission denied) → stop, don't skip (key issue, ไม่เกี่ยวกับ model)
