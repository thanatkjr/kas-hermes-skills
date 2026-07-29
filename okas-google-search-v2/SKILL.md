---
name: okas-google-search-v2
description: "OKAS Google Search V2 — สอนติดตั้ง Google API Key แบบ Step-by-Step + ค้นหาคุณภาพสูงมีแหล่งอ้างอิง ห้ามมั่ว"
version: 2.1.0
author: Thanat Kerdcharoen
license: MIT
metadata:
  hermes:
    tags: [search, web, grounding, gemini, google, setup]
---

# OKAS Google Search V2 🔍

> **สืบทอดจาก v1 — ปรับปรุงให้สมบูรณ์แบบ:** setup แบบมี verify, key ไม่หาย, ค้นหาคุณภาพสูงเท่าเดิม

---

## ⛔ กฎเหล็ก (MANDATORY — ห้ามละเมิด)

1. **ทุกการค้นหาต้องมีแหล่งที่มา** — ห้ามตอบลอยๆ
2. **ห้ามคาดเดาหรือปั้นข้อมูลเอง** — ถ้าหาไม่เจอ ให้บอกว่า "หาไม่เจอ"
3. **ใช้ strict mode เสมอ** — Anti-hallucination template บังคับทุก query
4. **ต้องกรองแหล่งที่มา** — domain ที่ไม่กล่าวถึงเป้าหมายโดยตรง → ห้ามอ้าง
5. **ระดับความน่าเชื่อถือ:** ⭐⭐⭐ ทางการ > ⭐⭐ องค์กร/วิชาการ > ⭐ ข่าว > ⚠️ บล็อก > ❌ ไม่กล่าวถึงเป้าหมาย

---

# Part 1: Agent Instructions — วิธีค้นหา

## 🔑 เมื่อ Key พร้อมใช้

```bash
cd "$HOME/AppData/Local/hermes/skills/kas-google-search/okas-google-search-v2/scripts"
python google_search.py "คำค้นหาที่นี่"
```

**script จะ:**
- ใช้ anti-hallucination template อัตโนมัติ (strict mode)
- อ่าน key จาก `~/AppData/Local/hermes/.env` โดยตรง (ไม่พึ่ง environment variable)
- แสดงผล + แหล่งที่มา + grounding URLs

## 🔑 เมื่อ Key ยังไม่ได้ติดตั้ง

ถ้า script รันแล้วได้ error ว่าไม่พบ API Key → **ต้องพาผู้ใช้ติดตั้ง key ทันที** ตามขั้นตอนใน Part 2

**ห้าม:**
- ❌ ใช้ web_search / sub-agent / browser แทน (คุณภาพต่ำ, มั่วข้อมูล)
- ❌ บอกว่า "ไม่สามารถค้นหาได้" แล้วจบ — ต้องพาติดตั้ง key
- ❌ เดาแหล่งที่มา — ต้องมี grounding URLs จริง

## 📊 How to Present Results

หลังได้ผลลัพธ์:
1. **กรอง grounding chunks** — เอาเฉพาะ domains ที่เกี่ยวข้อง
2. **ตรวจสอบ domain ตรงกับข้อเท็จจริง** — domain ที่ไม่กล่าวถึงเป้าหมาย → ห้ามอ้าง
3. **แสดงผลในรูปแบบ table** หรือ bullet points พร้อม ⭐ ความน่าเชื่อถือ
4. **ระบุแหล่งที่มาทุกข้อ**

---

# Part 2: ติดตั้ง Google API Key (Step-by-Step สอน User)

> 📖 **ใช้ section นี้เมื่อ:** ผู้ใช้ถามวิธีติดตั้ง / key ยังไม่มี / key ใช้ไม่ได้

## 📝 วิธีขอ Key (5 ขั้นตอน ~3 นาที)

### ขั้นที่ 1: เข้าเว็บ Google AI Studio

เปิด Chrome → พิมพ์ **https://aistudio.google.com** → กด Enter

ถ้ายังไม่ล็อกอิน → ล็อกอินด้วย Gmail (ส่วนตัวหรือบริษัทก็ได้)

### ขั้นที่ 2: เข้าหน้า API Keys

คลิก **"Get API Key"** เมนูซ้ายมือ

หรือเข้าตรง: **https://aistudio.google.com/apikey**

### ขั้นที่ 3: สร้าง Key ใหม่

คลิกปุ่มสีน้ำเงิน **"Create API Key"**

📌 เลือก **"Create API key in new project"** — แยกโปรเจค ไม่ปนกับงานอื่น

### ขั้นที่ 4: Copy Key

จะมีกล่องเด้งขึ้นมาแสดง API Key (ตัวอักษรยาว ~39 ตัว)

⚠️ **กดปุ่ม Copy ทันที** — แสดงครั้งเดียว! ปิดแล้วหาย → ต้องสร้างใหม่

📌 **Key มี 2 รูปแบบ:**
- `AIzaSy...` — จาก AI Studio (aistudio.google.com) — ใช้ได้กับ Free Tier
- `AQ.Ab8...` — จาก Google Cloud OAuth — ใช้ได้กับ billing account

ทั้งสองแบบใช้ได้กับสคริปต์นี้

### ขั้นที่ 5: ให้ Agent ติดตั้งให้

**บอก agent ว่า:** "นี่คือ key: AIzaSy..." — แล้ว agent จะติดตั้ง + ทดสอบให้

หรือถ้าอยากติดตั้งเอง → `python setup_key.py YOUR_KEY_HERE`

---

# Part 3: การติดตั้ง Key ทางเทคนิค

## 📁 ตำแหน่งที่เก็บ

| OS | Path |
|----|------|
| Windows | `%LOCALAPPDATA%\hermes\.env` → `C:\Users\<user>\AppData\Local\hermes\.env` |
| Linux/Mac | `~/.hermes/.env` |

## 🔧 วิธีติดตั้ง (สำหรับ Agent)

Agent ใช้ script `setup_key.py` — ซึ่งจะ:

1. ✅ ตรวจสอบ format key (ต้องขึ้นต้นด้วย `AIza` หรือ `AQ.`)
2. ✅ เขียนลง `.env` file โดยตรง (key: `GOOGLE_AI_API_KEY`)
3. ✅ ทดสอบ key โดยค้นหาจริง ("test search")
4. ✅ ยืนยันผล success/failure
5. ❌ ถ้า key ใช้ไม่ได้ → แจ้ง error + วิธีแก้

## 🛡️ ทำไม key ไม่หาย?

| ปัญหาที่ v1 เจอ | วิธีแก้ใน v2 |
|:---|:---|
| execute_code ไม่เห็น env var | `google_search.py` อ่าน `.env` file โดยตรง — ไม่พึ่ง environment |
| key ถูกบันทึกแต่ระบบบอกไม่มี | `setup_key.py` ทดสอบ key ทันทีหลังบันทึก → ถ้าไม่ผ่าน = key ผิด |
| ผู้ใช้ใส่ key ผิด format | `setup_key.py` validate format ก่อนบันทึก |
| มีหลาย key สับสน | script อ่าน key จาก `.env` เท่านั้น — แหล่งเดียว |

## 🔍 Troubleshooting

| Error | สาเหตุ | วิธีแก้ |
|-------|--------|--------|
| `404 Not Found` | โมเดลถูกยกเลิก (deprecated) | สคริปต์ v2.1+ มี fallback อัตโนมัติ → อัปเดตสคริปต์เป็นเวอร์ชันล่าสุด |
| `403 PERMISSION_DENIED` | Key ผิด / ยังไม่ activate | สร้าง key ใหม่ที่ https://aistudio.google.com/apikey |
| `429 Quota exceeded` | ใช้เกิน Free Tier หรือ billing ยังไม่ active | ถ้าไม่มี billing → รอวันถัดไป; ถ้ามี billing → เช็ค quota ใน Cloud Console |
| `503 Unavailable` | Server ล่มชั่วคราว | รอ 1-2 นาที แล้วลองใหม่ |
| `ไม่พบ API Key` | ยังไม่ได้ติดตั้ง | พาผู้ใช้ติดตั้งตาม Part 2 |

## 🔥 CRITICAL: การเปิด Billing ทำ Free Tier หาย

**"Once billing is enabled → free tier disappears → all calls become billable"** [google.dev]

| Key Type | Free Tier | Models | Cost |
|----------|:---------:|--------|------|
| **Old key (ไม่มี billing)** | ✅ 1,500 req/day | `gemini-2.5-flash` | $0 |
| **New key (เปิด billing แล้ว)** | ❌ billable | `gemini-3.6-flash` | ~$0.004/req |

> ⚠️ **ถ้า key ปัจจุบันยังใช้ได้ (ไม่มี billing) — อย่าเปิด billing!** ใช้ต่อไปฟรี
> ดูรายละเอียดเพิ่มเติม: `references/model-maintenance.md`

---

# Part 4: ตัวอย่างผลลัพธ์ที่คาดหวัง

## ✅ ดี — แบบนี้ใช้ได้

```
🔍 PIAC วุฒิบัตรผู้ตรวจสอบภายในวิชาชีพ

• พัฒนาโดยสภาวิชาชีพบัญชี (TFAC) ⭐⭐⭐ [tfac.or.th]
• ก.ล.ต. ให้การยอมรับ ⭐⭐⭐ [set.or.th]
• ค่าสอบ 2,200 บาท/วิชา ⭐⭐⭐ [tfac.or.th]
```

## ❌ ไม่ดี — ห้ามทำ

```
• "PIAC คือ..." (ไม่มีแหล่งที่มา)
• "จากการค้นหาทั่วไป..." (ใช้ web_search/sub-agent)
• "แหล่งที่มา: google.com" (หลอน)
```

---

## 📦 Scripts

| Script | หน้าที่ |
|--------|--------|
| `scripts/google_search.py` | ค้นหาด้วย Gemini + Google Search Grounding (เหมือน v1) |
| `scripts/setup_key.py` | ติดตั้ง + ตรวจสอบ API Key |

## 📚 References

| File | เนื้อหา |
|------|--------|
| `references/model-maintenance.md` | วิธีตรวจสอบ model availability + lifecycle |

## Free Tier

| Model | Key Type | ต่อวัน | Cost |
|-------|----------|:------:|------|
| `gemini-2.5-flash` | Old key (no billing) | 1,500 req | $0 |
| `gemini-3.6-flash` | New key (billing) | unlimited* | ~$0.004/req |
| `gemini-2.0-flash` | Old key (no billing) | 1,500 req | $0 |

> ⚠️ **เปิด billing → free tier หายตลอดกาล** — อย่าเปิดถ้า key เดิมยังใช้ได้!
> 
> สคริปต์ v2.1+ มี fallback อัตโนมัติ — ถ้า model แรกใช้ไม่ได้จะลอง model ถัดไป
