---
name: kas-rcm-setup
description: ตั้งค่าและใช้งาน RCM MCP Server สำหรับงานตรวจสอบภายใน — สอบถาม Nature of Business, สร้าง Audit Universe, Standard Risk Control Matrix, และ Control Analysis Report พร้อม output เป็น HTML ที่แก้ไขได้และ save เป็น PDF ได้
version: 1.2.0
author: KAS / Thanat Kerdcharoen
license: Proprietary — KAS Internal Use Only
metadata:
  hermes:
    tags: [kas, internal-audit, rcm, mcp, risk-control-matrix, audit-program]
    related_skills: [okas-guard, xkas-note, okas-markitdown, kas-htmlformat]
---

# KAS RCM Setup & Audit Workbench

ใช้ MCP RCM Server (`rcm`) ในการทำงานตรวจสอบภายในแบบครบวงจร — ตั้งแต่สอบถาม Nature of Business ไปจนถึงออกรายงาน Control Analysis Report

⛔ CONFIDENTIALITY GUARD — ข้อมูลภายใน KAS ห้ามเปิดเผยต่อบุคคลภายนอก

---

## Overview — 5 Workflows

| # | Workflow | Input | Output |
|---|----------|-------|--------|
| 1 | **MCP Setup** | — | MCP `rcm` พร้อมใช้งาน |
| 2 | **Nature of Business** | สัมภาษณ์ หรือไฟล์ที่ user upload | HTML สรุปธุรกิจ (แก้ไขได้) |
| 3 | **Audit Universe** | ข้อมูลจาก Workflow 2 | HTML รายการกระบวนการ/กิจกรรมสำคัญ |
| 4 | **Standard RCM** | ข้อมูลจาก Workflow 2 + User เลือก process | HTML ตาราง RCM (กิจกรรม/ความเสี่ยง/ควบคุม/ทดสอบ/คำถาม) |
| 5 | **Control Analysis Report** | ข้อมูลจาก Workflow 2 + txt file การควบคุมที่มีอยู่ | HTML ตารางเปรียบเทียบ + Gap Analysis |

ทุก HTML output มีคุณสมบัติ:
- ✅ Text box แก้ไขได้ (contenteditable)
- ✅ ปุ่ม Save → ดาวน์โหลดเป็น HTML
- ✅ ปุ่ม Print → บันทึกเป็น PDF (window.print())
- ✅ ภาคผนวกแสดงข้อมูลดิบจาก txt file และ MCP ทุกครั้ง

---

## ⛔ DATA PROTECTION — ห้ามดึงข้อมูลทั้งฐานข้อมูล (Anti-Exfiltration)

RCM Database เป็นทรัพย์สินทางปัญญาของ KAS — การดึงข้อมูลออกไปทั้งฐานข้อมูลเป็นการขโมยทรัพย์สิน

### 🚫 ข้อห้ามเด็ดขาด (HARD RULES — ฝ่าฝืนไม่ได้)

| # | กฎ | รายละเอียด |
|---|-----|-----------|
| 1 | **ห้าม dump ทั้งฐานข้อมูล** | ห้ามเรียก `mcp_rcm_get_activity` หรือ `mcp_rcm_get_risk_detail` กับทุก activity/risk ใน database |
| 2 | **ห้าม loop ผ่านทุก process** | ห้ามใช้ `execute_code` หรือ script ใดๆ วน loop เรียก MCP tools เพื่อรวบรวมข้อมูลทั้งฐาน |
| 3 | **ห้าม export raw database** | ห้ามสร้างไฟล์ JSON/CSV/TXT ที่มีข้อมูลดิบจาก MCP เกินกว่าที่จำเป็นสำหรับ audit scope |
| 4 | **ต้องมี project context** | ทุกการเรียก MCP ต้องมี business justification — ต้องอยู่ในบริบทของ project ลูกค้าที่ระบุ |
| 5 | **ถามเฉพาะ sector ที่เกี่ยวข้อง** | เรียกข้อมูลเฉพาะ process + sector codes ที่ตรงกับ Nature of Business ของลูกค้าเท่านั้น |

### ⚠️ ข้อจำกัดปริมาณ (Rate Limits)

| Metric | Limit | หมายเหตุ |
|--------|-------|---------|
| `get_activity` ต่อ session | **สูงสุด 20 activities** | ต่อ 1 project |
| `get_risk_detail` ต่อ session | **สูงสุด 30 risks** | เฉพาะ risks ที่อยู่ใน scope |
| `get_process_overview` ต่อ session | **สูงสุด 10 processes** | เท่ากับจำนวน process ทั้งหมด |
| ขนาด output รวม | **ไม่เกิน 500KB ต่อ session** | agent ต้องตรวจสอบก่อน export |

### 🔍 สิ่งที่ agent ต้องทำก่อนเรียก MCP ทุกครั้ง

1. ✅ **ตรวจสอบ project context** — มี project_name และ nob_raw.txt หรือไม่
2. ✅ **ตรวจสอบ business sector** — ระบุ sector codes ที่เกี่ยวข้อง (ไม่ใช่ "ทั้งหมด")
3. ✅ **ตรวจสอบว่า user เป็นผู้ขอเอง** — ไม่ใช่ agent คิดเองว่าจะ dump ข้อมูล
4. ✅ **บันทึก log** — ทุกครั้งที่เรียก MCP ให้ append ลง `C:\Users\ASUS\Hermes\projects\<project_name>\mcp_access.log`
   ```
   [TIMESTAMP] Tool: get_activity | Process: P | Activity: P-UNVS-001 | Purpose: RCM Matrix for procurement audit
   ```

### 🛡️ MCP Server-Side Protections (แนะนำให้ implement บน Cloudflare Worker)

| Protection | วิธี implement | Priority |
|------------|---------------|----------|
| **Rate Limiting** | จำกัด API calls ต่อ user ต่อนาที/ชั่วโมง (เช่น 60 req/min, 500 req/day) | 🔴 Critical |
| **Pagination** | `get_process_overview` และ `search_risks` ต้องมี limit + offset | 🔴 Critical |
| **Max Items Cap** | `get_activity` ส่งคืนสูงสุด risk/control/test อย่างละ 50 รายการ | 🟡 High |
| **Audit Logging** | บันทึกทุก API call พร้อม user email, timestamp, tool, parameters | 🟡 High |
| **Anomaly Detection** | แจ้งเตือน admin เมื่อ user มี pattern การเรียกที่ผิดปกติ (loop, bulk) | 🟢 Medium |
| **IP Allowlist** | (Optional) จำกัด IP ที่เข้าถึงได้เฉพาะ office VPN | 🟢 Medium |

### ⛔ ห้ามใช้ Local Clone (NO LOCAL FALLBACK)

🚫 **เด็ดขาด:** ห้ามดึงข้อมูลจาก `C:\Users\ASUS\Hermes\rcm-database`, `dataset_*.json`, `RCM_Database.json`, หรือ `scripts/query.py` — ใช้ MCP Cloudflare (`rcm-mcp-server.thanatkjr.workers.dev`) เท่านั้น

| กฎ | รายละเอียด |
|----|-----------|
| **ห้ามใช้ local clone** | ห้าม `git pull` + อ่าน `dataset_*.json` โดยตรง — ข้อมูลอาจเก่ากว่า MCP server |
| **ห้ามใช้ query.py** | `query.py` ไม่มี `sector_code` ใน `--list-activities` และไม่มี `get_process_rcm` |
| **ถ้า MCP tools ไม่ inject** | ใช้ปุ่ม **Reload MCP** ใน Settings → MCP → Reload MCP → `/reset` → ถ้ายังไม่ได้ผล → ปิด-เปิด Hermes Desktop ใหม่ |
| **ห้าม fallback** | อย่าใช้ "MCP tools ไม่พร้อม → ใช้ local แทน" — ต้องแก้ให้ MCP tools inject ได้ก่อน |

### 🚨 การตรวจพบการละเมิด

ถ้า agent พบว่ามีความพยายาม:
- เรียก `get_activity` เกิน 20 ครั้งใน session เดียว
- เรียก `get_process_overview` กับทุก process โดยไม่มี sector filter
- สร้างไฟล์ที่มีข้อมูลดิบจาก MCP เกิน scope

**→ Agent ต้อง STOP ทันที และแจ้ง user ว่า:**
> "⛔ การดำเนินการนี้เข้าข่ายการดึงข้อมูลทั้งฐานข้อมูล — หยุดเพื่อป้องกันการละเมิด Data Protection Policy ของ KAS"
> 
> "หากต้องการข้อมูลเพิ่ม กรุณาระบุเฉพาะ process/activity ที่อยู่ใน audit scope"

---

## 🆕 Workflow 0: MCP Tool Injection Fix (Fallback เมื่อ tools ไม่ inject)

**ปัญหา:** บน Windows `mcp` package มี dependency `pywin32` (`pywintypes`) ซึ่งอาจไม่มีใน sandbox Python ของ Hermes → MCP tools ไม่ inject เข้า agent session แม้ `hermes mcp test rcm` จะผ่าน

**✅ Workaround: `rcm_http_client.py`** — Python client ที่เรียก Cloudflare โดยตรงผ่าน HTTP ล้วน ๆ ไม่ต้องใช้ `mcp` SDK (อยู่ใน `scripts/rcm_http_client.py`)

### วิธีใช้ใน execute_code

```python
import sys
sys.path.insert(0, r"C:\Users\ASUS\AppData\Local\hermes\skills\audit\kas-rcm-setup\scripts")
from rcm_http_client import RCMClient

client = RCMClient()

# ใช้เหมือน mcp_rcm_* tools ทุกประการ:
db = client.get_db_info()
processes = client.list_processes()
activities = client.get_process_overview("P")
risks = client.search_risks("ทุจริต")
activity = client.get_activity("P", "P-UNVS-001")
risk = client.get_risk_detail("P", "P-UNVS-001.R1")
rcm = client.get_process_rcm("P", sector_code="FOOD")

client.close()
```

### API Reference

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_db_info()` | — | `dict` — version, counts |
| `list_processes()` | — | `list` — 10 processes |
| `get_process_overview(process_code)` | `process_code: str` | `list` — activities with sector_code |
| `search_risks(query, process_code?, risk_category?)` | `query: str` | `list` — matching risks |
| `get_activity(process_code, activity_code)` | `process_code, activity_code: str` | `dict` — full activity tree |
| `get_risk_detail(process_code, risk_code)` | `process_code, risk_code: str` | `dict` — all risk fields |
| `get_process_rcm(process_code, sector_code)` | `process_code, sector_code: str` | `dict` — full RCM for UNVS+sector |

> ⚠️ **`find_activities` ยังไม่มี wrapper ใน `rcm_http_client.py`** — เรียกผ่าน generic helper ได้เลย: `client._tool("find_activities", {"keywords_activity": [...], "keywords_person": [...], "keywords_doc": [...], "process_code": "P", "sector_code": "FOOD", "min_facets": 1})` — คืน `{total_matched, returned, capped, facets_supplied, min_facets, results[]}` โดย **cap = 20 results เสมอ** (ดู rcm-knowledge)

### ข้อดี
- ✅ ไม่ต้องพึ่ง MCP tool injection
- ✅ ไม่ต้องใช้ `mcp` SDK (ไม่มี dependency `pywin32`)
- ✅ ใช้ OAuth token เดียวกับที่ Hermes ใช้ — ไม่ต้อง login ใหม่
- ✅ ใช้ `urllib` ล้วน ๆ — ทำงานได้ในทุก Python environment

### Verification
```bash
cd "C:\Users\ASUS\AppData\Local\hermes\skills\audit\kas-rcm-setup\scripts"
python rcm_http_client.py --tool get_db_info
```

---

## Prerequisites (ก่อนเริ่ม)

### MCP Server — สิ่งที่ Admin ต้องทำก่อน

Admin (Thanat) ต้องเพิ่ม email ของ user ใน Cloudflare Workers ก่อน user จะ connect ได้:

1. เปิด Cloudflare Dashboard → Workers & Pages → `rcm-mcp-server`
2. ตั้งค่า OAuth → เพิ่ม email ของ user ใน allowlist
3. แจ้ง user ว่าพร้อมใช้งานแล้ว

### MCP Server — สิ่งที่ User ต้องทำ

**วิธีที่ 1: ผ่าน GUI (แนะนำ)**
1. เปิด Hermes → Settings → MCP
2. กด `New server`
3. ใส่:
   - Name: `rcm`
   - Server JSON:
     ```json
     {
       "url": "https://rcm-mcp-server.thanatkjr.workers.dev/mcp",
       "auth": "oauth",
       "enabled": true
     }
     ```
4. กด `Save server`
5. ระบบจะเปิด browser ให้ login ด้วย Gmail
6. กลับมาที่ Hermes → `/reload-mcp`

**วิธีที่ 2: ผ่าน CLI**
```bash
hermes mcp add rcm --url "https://rcm-mcp-server.thanatkjr.workers.dev/mcp"
# จากนั้นตั้งค่า auth ใน GUI (Settings → MCP → Edit server → auth: oauth)
```

### ตรวจสอบว่า MCP พร้อมใช้งาน

```bash
hermes mcp list        # ต้องเห็น rcm: ✓ enabled
hermes mcp test rcm    # ต้องเห็น "✓ Connected" + "✓ Tools discovered: 8"
```

ถ้าไม่ผ่าน → แจ้ง user ติดต่อ Admin เพื่อเพิ่ม email ใน allowlist

---

## MCP Tools Reference

หลังจากเชื่อมต่อ MCP `rcm` สำเร็จ tools ต่อไปนี้จะพร้อมใช้งาน:

| Tool | หน้าที่ | วิธีเรียก |
|------|--------|-----------|
| `mcp_rcm_list_processes` | รายการ 10 processes (ELC, P, R, IC, OP, HR, AF, FA, IT, SHE) | เรียกโดยตรง |
| `mcp_rcm_get_process_overview` | กิจกรรมทั้งหมดใน 1 process (codes + names) | ส่ง `process_code` |
| `mcp_rcm_search_risks` | ค้นหา risks ด้วย keyword ไทย/อังกฤษ | ส่ง `keyword` และ optional filters |
| `mcp_rcm_find_activities` | 🆕 ค้นหากิจกรรมแบบ intersection 3 มิติ (ขั้นตอน/ผู้รับผิดชอบ/เอกสาร) — คืน `facets_hit` + `matched` | ส่ง `keywords_activity`, `keywords_person`, `keywords_doc`, `process_code`, optional `sector_code`/`min_facets` |
| `mcp_rcm_get_activity` | ดู 1 activity แบบเต็ม (risks, controls, tests, policies, validations, procedures) | ส่ง `process_code` + `activity_code` |
| `mcp_rcm_get_risk_detail` | ดู 1 risk พร้อมทุก field (poison, indicator, validations, policies, procedures, report, controls, tests) | ส่ง `process_code` + `risk_code` |
| `mcp_rcm_get_process_rcm` | 🆕 ดึง RCM ทั้ง process แบบ scoped (กรองตาม sector) — คืน risks/controls/tests/questions ครบใน call เดียว | ส่ง `process_code`, `sector_code` |
| `mcp_rcm_get_db_info` | ข้อมูล version, last update, record counts | เรียกโดยตรง |

---

## Workflow 1: MCP Setup Verification

**Goal:** ตรวจสอบว่า MCP `rcm` พร้อมใช้งาน

### Step 1.1: เช็คสถานะ

```bash
hermes mcp list
```

- ✅ ถ้าเห็น `rcm` และ status `✓ enabled` → ไป Step 1.2
- ❌ ถ้าไม่เห็น → แจ้ง user ติดตั้งตาม "วิธีที่ 1" หรือ "วิธีที่ 2" ข้างบน

### Step 1.2: ทดสอบการเชื่อมต่อ

```bash
hermes mcp test rcm
```

- ✅ `✓ Connected` + `✓ Tools discovered: 8` → พร้อมทำงาน
- ❌ `✗ Failed` → 
  - "invalid_token" / "401" → token หมดอายุ → **รัน `rcm_http_client.py --tool get_db_info` เพื่อ refresh อัตโนมัติ** (ดู Common Pitfall #4) — ไม่ต้อง reconnect เองเว้นแต่ refresh_token ใช้ไม่ได้แล้ว

### Step 1.3: ตรวจสอบ tools

เรียก `mcp_rcm_get_db_info` เพื่อยืนยันว่าฐานข้อมูลพร้อมใช้

---

## Workflow 2: Nature of Business (NOB)

**Goal:** รวบรวมข้อมูลธุรกิจของลูกค้า → สรุปเป็น HTML ที่แก้ไขได้

### Step 2.1: รับข้อมูล

ให้ user เลือกวิธีให้ข้อมูล:

**Option A: Upload ไฟล์พร้อมกัน (⚡ พบบ่อยที่สุด — แนะนำ)**
1. User มัก upload หลายไฟล์พร้อมกัน (Company Profile, Org Chart, งบการเงิน) + พูดสั้นๆ เช่น "ตามนี้"
2. Agent ต้อง parallel process ทันที:
   - แปลง PDF ทั้งหมดพร้อมกัน (pymupdf สำหรับ text-based, pymupdf+vision สำหรับ scanned)
   - ค้นหา Internet (`okas-google-search-v2`) พร้อมกัน 2-3 queries
   - บันทึก `nob_raw.txt` ทันทีที่ได้ข้อมูล
3. หลัง compile ครบ → แสดงสรุปสั้น + ถามเฉพาะหัวข้อที่ยังขาด
4. **ห้ามถามทีละข้อถ้า user ให้ไฟล์มาแล้ว** — user คาดหวังว่า agent จะ extract ข้อมูลทั้งหมดจากไฟล์เอง

**Option B: สัมภาษณ์ทีละส่วน (ถามทีละหัวข้อ)**

ถามทีละหัวข้อ 6 ส่วน รอคำตอบก่อนถามต่อ:

... (รายละเอียด 7 หัวข้อเหมือนเดิม) ...

1. **สินค้า/บริการหลัก** — กิจการขายสินค้าหรือบริการอะไร? มีกี่กลุ่ม? แต่ละกลุ่มมีสัดส่วนรายได้เท่าไร?
2. **ลูกค้าหลัก** — ลูกค้าเป็นใคร? B2B/B2C/Government? มีลูกค้ารายใหญ่กี่ราย? ช่องทางขาย?
3. **ผู้ขาย/ผู้ให้บริการหลัก** — ซื้อวัตถุดิบ/สินค้า/บริการจากใคร? มี vendor หลักกี่ราย? วิธีการจัดซื้อ?
4. **รายได้และค่าใช้จ่ายหลัก** — รายได้มาจากไหน? รับชำระอย่างไร? ค่าใช้จ่ายหลักมีอะไรบ้าง? โครงสร้างต้นทุน?
5. **รูปแบบการผลิต/ให้บริการ** — กระบวนการผลิต/ให้บริการเป็นอย่างไร? มีสต็อกสินค้าหรือไม่? ใช้เครื่องจักรอะไร?
6. **กฎหมาย/ข้อบังคับ/สัญญาสำคัญ** — อยู่ภายใต้กฎหมายอะไร? มีใบอนุญาตอะไร? สัญญาสำคัญกับคู่ค้า? มาตรฐานที่ต้องปฏิบัติ?
7. **ระบบ ERP/IT ที่ใช้** — ใช้ระบบอะไร? โมดูลที่ใช้? ระบบบัญชี? ระบบ payroll?

⚠️ **ทุกครั้งที่ถาม** — บันทึกคำตอบลง text file ทันทีที่ `C:\Users\ASUS\Hermes\projects\<project_name>\nob_raw.txt`

**Option B: รับไฟล์ที่ user upload**

1. User upload ไฟล์ (PDF, DOCX, TXT) → แปลงเป็น text:
   - **PDF:** ใช้ `pymupdf` (fitz) โดยตรงด้วย `execute_code` — เร็วกว่าและรองรับภาษาไทยดีกว่า `okas-markitdown`
     - ถ้า PDF เป็นแบบภาพ (scanned) → แปลงหน้าเป็น PNG ด้วย `page.get_pixmap(dpi=200)` แล้วใช้ `vision_analyze` อ่าน
   - **DOCX/XLSX:** ใช้ `read_file` — Hermes auto-extracts ให้
2. อ่านเนื้อหาทั้งหมด → สกัดประเด็นตาม 7 หัวข้อ
3. บันทึกข้อมูลที่สกัดได้ลง `nob_raw.txt` ทันที (กันข้อมูลหาย)
4. **Internet Research (CRITICAL):** ทันทีที่ได้ข้อมูลจากไฟล์ → ค้นหาข้อมูลเสริมจาก internet:
   - ใช้ `okas-google-search-v2` skill → `google_search.py` หลาย query พร้อมกัน
   - ค้นหาด้วยชื่อบริษัท + แบรนด์ — หาข้อมูลช่องทางขาย, รายได้, ข่าว, ประกาศรับสมัครงาน, ระบบ ERP, มาตรฐาน
   - **อย่ารอให้ user บอกให้ค้น** — agent ต้อง proactive ค้นหาทันทีที่ข้อมูลจากไฟล์ไม่ครบ
   - Append ผลการค้นหาลง `nob_raw.txt`
5. ถ้าข้อมูลยังไม่ครบ → ถามเฉพาะหัวข้อที่ขาด

### Step 2.2: ตรวจสอบความครบถ้วน

หลังจากได้ข้อมูลจากทุกแหล่ง (ไฟล์ + internet search):
- ✅ ถ้าครบทุกหัวข้อ → ไป Step 2.3
- ⚠️ ถ้าบางหัวข้อไม่มีข้อมูล → ถามเพิ่มเฉพาะส่วนที่ขาด

### Step 2.3: วิเคราะห์และสรุป

ใช้ข้อมูลจาก Step 2.1-2.2:
1. จำแนกประเภทอุตสาหกรรม (sector) — อาหาร? ก่อสร้าง? ค้าปลีก? ผลิต? บริการ?
2. ระบุ business sector codes ที่เกี่ยวข้องกับ RCM (ดูจาก activity codes ใน RCM เช่น FOOD, CONS, COMM, MACH, TOUR)
3. สรุปเป็น structured summary

### Step 2.4: สร้าง HTML Output

สร้าง HTML file ที่ `C:\Users\ASUS\Hermes\projects\<project_name>\nob_summary.html`

**HTML ต้องมี:**
- หัวข้อ: "Nature of Business — [ชื่อบริษัท]"
- แต่ละ section (7 หัวข้อ) เป็น `<div contenteditable="true">` — user แก้ไขได้
- ปุ่ม 💾 **Save as HTML** → ดาวน์โหลดไฟล์ HTML ปัจจุบัน (รวมที่แก้ไขแล้ว)
- ปุ่ม 🖨️ **Print / Save as PDF** → `window.print()`
- ภาคผนวก: แสดง raw text ทั้งหมดที่ใช้

**HTML Template:** ดู `templates/nature-of-business.html` ใน skill นี้

---

## Workflow 3: Audit Universe

**Goal:** จาก NOB → สร้างรายการกระบวนการ/กิจกรรมสำคัญ (Audit Universe) ตาม RCM framework

### Step 3.1: ระบุ business sectors

จากข้อมูล NOB (Workflow 2) → ระบุว่ารวม business sector ไหนบ้าง:

ใช้ logic:
- อาหาร/เครื่องดื่ม → FOOD
- ก่อสร้าง/อสังหา → CONS, PROP
- ค้าปลีก/ค้าส่ง → COMM
- ผลิต/เครื่องจักร → MACH
- ท่องเที่ยว/โรงแรม → TOUR
- โลจิสติกส์ → LOGI
- เกษตร → AGRI
- ไอที/ซอฟต์แวร์ → ICT
- สื่อ/บันเทิง → MEDA
- พลังงาน → ENGY
- ฯลฯ

📌 **UNVS (Universal) activities ใช้ได้กับทุกธุรกิจ** — ต้องรวมเสมอ

### Step 3.2: ดึง activity list จาก MCP

> 🆕 **แนะนำ:** ถ้า user ให้ keyword/ข้อมูลกระบวนการมา → ใช้ `find_activities` (intersection 3 มิติ: `keywords_activity` + `keywords_person` + `keywords_doc` + `process_code`) แทนการไล่ดู list ทั้งหมด — ดู workflow เต็มใน skill `rcm-knowledge`

เรียก `mcp_rcm_get_process_overview` สำหรับทุก process ที่เกี่ยวข้อง:

```
เรียกทีละ process:
- mcp_rcm_get_process_overview(process_code="ELC")
- mcp_rcm_get_process_overview(process_code="P")
- mcp_rcm_get_process_overview(process_code="R")
- ... (ทุก process ที่มี sector codes ตรงกับธุรกิจ)
```

สำหรับแต่ละ process → กรอง activity ที่มี sector_code = "UNVS" หรือ ตรงกับ sector ของลูกค้า

### Step 3.3: สร้าง Audit Universe

จัดกลุ่ม activity ตาม:
1. **Process** (ELC, P, R, IC, OP, HR, AF, FA, IT, SHE)
2. **ประเภท** — UNVS (ทั่วไป) vs Sector-specific

### Step 3.4: สร้าง HTML Output

สร้าง HTML ที่ `C:\Users\ASUS\Hermes\projects\<project_name>\audit_universe.html`

**HTML ต้องมี:**
- ตาราง: Process | Activity Code | Activity Name | Sector | Recommend? (checkbox)
- User เลือก checkbox ได้ว่าจะเอากิจกรรมไหนเข้า audit scope
- ปุ่ม 💾 **Save as HTML**
- ปุ่ม 🖨️ **Print / Save as PDF**
- ภาคผนวก: raw output จาก MCP

---

## Workflow 4: Standard Risk Control Matrix

**Goal:** สร้างตาราง RCM (กิจกรรม/ความเสี่ยง/การควบคุม/ทดสอบ/คำถาม) สำหรับ process/กิจกรรมที่ user เลือก

### Step 4.1: ให้ user เลือก

ให้ user เลือก:
1. **Process** ที่ต้องการ (จาก dropdown — 10 processes)
2. **Activity** ที่ต้องการ (จาก list ที่ดึงมาจาก MCP)
   - หรือ "ทั้งหมดใน process นี้"
3. **Risk Category** (optional filter) — "Fraud Risk", "Operational Risk", "Compliance Risk", etc.

### Step 4.2: ดึงข้อมูลจาก MCP

```
mcp_rcm_get_activity(process_code="P", activity_code="P-UNVS-001")
```

ได้ข้อมูล:
- Risk → risk_code, risk_name, risk_category, poison
- Control → control_code, control_name, control_category, control_method, control_nature
- Test → test_code, test_name
- Question → question_code, question_text
- Policies, Validations, Procedures

⚠️ **สำคัญ:** ดึงทีละ activity เพื่อป้องกัน context overflow
- ถ้า user เลือกหลาย activity → ดึงทีละตัว สะสมใน text file
- ใช้ `execute_code` จัดการ batch processing

### Step 4.3: สร้าง HTML Output

สร้าง HTML ที่ `C:\Users\ASUS\Hermes\projects\<project_name>\rcm_matrix_<client>.html`

**HTML ต้องมี (ตาราง 7 คอลัมน์ — DEFAULT ไม่รวม Poison):**

| กระบวนการ | กิจกรรม | ความเสี่ยง | การควบคุมที่ควรมี | วิธีการตรวจสอบ | คำถามสัมภาษณ์ | ลักษณะควบคุม |
|-----------|---------|-----------|-------------------|---------------|---------------|-------------|

แต่ละแถว:
- กระบวนการ → `contenteditable="false"` (display only, ใช้อ้างอิง SICT process code)
- Activity → `contenteditable` (user ปรับชื่อกิจกรรมให้ตรงกับองค์กรได้)
- Risk → `contenteditable`
- Control → `contenteditable` (user เพิ่ม/แก้ไข control ได้)
- Test → `contenteditable` (user ปรับ test procedure ได้)
- Question → `contenteditable`
- Control Nature → display only

**❌ Poison column — ห้ามใส่เป็น default** (user ไม่ต้องการ)

**ฟีเจอร์บังคับ:**
- 💾 **Save as HTML**
- 🖨️ **Print / Save as PDF** (A3 landscape)
- 🔍 **Search bar** — ค้นหาข้อความ กรองตามคอลัมน์ แสดงจำนวนผลลัพธ์
- 📊 **Summary bar** — แสดงจำนวน processes, activities, controls ที่ครอบคลุม
- 📏 **Styled scrollbar** — มองเห็นชัด ความสูง 12px
- 📐 **Column max-width** — ป้องกันคอลัมน์ยาวเกินด้วย `max-width` + `word-break: break-word`

**ภาคผนวก:** raw MCP output ใน `<details><summary>` แบบพับได้

ดูตัวอย่างที่สมบูรณ์ใน `references/rcm-html-template.md`

---

## Workflow 5: Control Analysis Report

**Goal:** เปรียบเทียบ "การควบคุมที่ควรมี" (จาก RCM) กับ "การควบคุมที่มีอยู่" (จาก user) → Gap Analysis

### Step 5.1: รับข้อมูลการควบคุมที่มีอยู่

User ต้องให้ข้อมูล "การควบคุมที่มีอยู่" — มาในรูปแบบ:

**Option A: txt file จาก note skill**
- User สร้าง note ด้วย `xkas-note` skill → ได้ txt file
- อ่านไฟล์ → สกัดเอา existing controls

**Option B: ไฟล์อื่นที่ user upload**
- User upload PDF/DOCX/TXT → แปลงด้วย `okas-markitdown` → อ่าน controls

**Option C: User พิมพ์/บอกโดยตรง**
- ถามทีละ activity → user อธิบาย existing controls

⚠️ **ทุกครั้งที่ได้ข้อมูล** — บันทึกลง `C:\Users\ASUS\Hermes\projects\<project_name>\existing_controls.txt`

### Step 5.2: Map existing controls → RCM activities

อ่าน existing controls จาก txt file → เทียบกับ RCM activities:
- ✅ **Covered** — มี control ตรงกับที่ RCM แนะนำ
- ⚠️ **Partial** — มีบางส่วน แต่ไม่ครบ
- 🔴 **Gap** — ไม่มี control นี้เลย

### Step 5.3: ปรับ test procedures ให้สอดคล้องกับธุรกิจ

จาก test procedures ใน RCM:
1. อ่าน test description จาก MCP
2. ปรับภาษาให้สอดคล้องกับ Nature of Business (Workflow 2)
   - เปลี่ยนชื่อเอกสาร/ระบบ/ตำแหน่ง ให้ตรงกับองค์กร
   - เพิ่มรายละเอียดเฉพาะของธุรกิจ
3. ใช้ `execute_code` สำหรับ batch processing ถ้ามีหลาย activity

### Step 5.4: สร้าง HTML Output

สร้าง HTML ที่ `C:\Users\ASUS\Hermes\projects\<project_name>\control_analysis_<process>.html`

**HTML ต้องมี (ตาราง 6 คอลัมน์):**

| กิจกรรม | ความเสี่ยง | การควบคุมที่ควรมี | การควบคุมที่มีอยู่ | สถานะ | วิธีการตรวจสอบ |
|---------|-----------|-------------------|-------------------|-------|---------------|

- สถานะ: ✅ Covered / ⚠️ Partial / 🔴 Gap (dropdown ใน HTML)
- การควบคุมที่มีอยู่: `contenteditable` (user แก้ไข/เพิ่มได้)
- วิธีการตรวจสอบ: `contenteditable` — ปรับมาจาก RCM test procedures ให้สอดคล้องกับธุรกิจ

**สรุปท้ายตาราง:**
- จำนวนทั้งหมด: N controls
- ✅ Covered: X (Y%)
- ⚠️ Partial: Y (Z%)
- 🔴 Gap: Z (W%)

ปุ่ม:
- 💾 **Save as HTML**
- 🖨️ **Print / Save as PDF**

ภาคผนวก:
- Raw MCP output
- Raw existing controls (txt file content)

---

## 🆕 Workflow 6: Interactive RCM Builder (Sector → Process → find_activities → RCM)

**Goal:** สร้าง RCM / policy & procedure แบบ interactive — user เลือก sector + process ผ่าน checkbox → ให้ข้อมูลกระบวนการ (ขั้นตอน/คน/เอกสาร) → `find_activities` คัดกรองกิจกรรมที่เกี่ยวข้องจริง → ดึง RCM เต็ม → output HTML ตาม `kas-rcm-v1`

ใช้ workflow นี้เมื่อ user ต้องการทำ RCM หรือ policy/procedure ของธุรกิจใด ๆ — แทนการไล่ activity list ทั้งหมด (848 activities) ด้วย `find_activities` (intersection 3 มิติ)

> 📌 sector codes ครบ 31 ตัว + ชื่อไทย + 9 หมวด → `references/sector-codes.md`

### Step 0: ระบุ industry/sector เบื้องต้น

1. ถาม user ว่าเป็นธุรกิจอะไร (1-2 ประโยค) — ขาย/บริการอะไร
2. ระบุ sector code เบื้องต้นจาก `references/sector-codes.md`

### Step 1: เลือก sector + process (checkbox)

**Sector:**
1. แสดง 31 sector codes พร้อมชื่อไทย + หมวด (จาก `references/sector-codes.md`) เป็น checkbox
2. ให้ user ติ๊กเลือก sector ที่ตรงกับธุรกิจ (เลือกได้หลายตัว)
   - ⚠️ UNVS (Universal) ไม่ต้องให้เลือก — `get_process_rcm` รวม UNVS ให้อัตโนมัติเสมอ

**Process:**
1. เรียก `list_processes()` → 10 processes พร้อมชื่อไทย
2. แสดงเป็น checkbox ให้ user ติ๊กเลือก process ที่ต้องการ

### Step 2: รับข้อมูลกระบวนการ (ขั้นตอน/บุคลากร/เอกสาร)

ถาม user ให้ข้อมูลกระบวนการ **เท่าที่มี** (ไม่ต้องครบ) — 3 กลุ่ม:
1. **ขั้นตอน/กิจกรรม** เช่น "ขอซื้อ, เปรียบเทียบราคา, ตรวจรับ"
2. **บุคลากร/หน่วยงาน** เช่น "ผู้จัดการฝ่ายจัดซื้อ, คณะกรรมการจัดซื้อ"
3. **เอกสาร/ฟอร์ม/รายงาน** เช่น "ใบขอซื้อ, ใบสั่งซื้อ, ใบกำกับภาษี"
   - ⚠️ ห้ามใส่ระบบ IT (ERP/WMS) ในกลุ่มเอกสาร

⚠️ **บันทึกข้อมูลดิบทันที** → `C:\Users\ASUS\Hermes\projects\<project_name>\process_input.txt` (กันข้อมูลหาย)

### Step 3: find_activities match

1. สกัด keyword 3 กลุ่มจาก Step 2
2. เรียก `find_activities(keywords_activity, keywords_person, keywords_doc, process_code, sector_code)`
   - แคบด้วย `process_code` + `sector_code` ให้มากที่สุด (ลดผลลัพธ์เกิน cap)
3. อ่านผล: แต่ละ result มี `activity_code`, `activity_name`, `sector_code`, `facets_hit` (0-3), `score`, `matched`

### Step 4: แสดง 3 กลุ่มให้ user ติ๊ก confirm

| กลุ่ม | เงื่อนไข | ความหมาย |
|-------|---------|-----------|
| A) Match ตรง | `facets_hit` 2-3 | ตรงกับข้อมูล user มากที่สุด |
| B) น่าสนใจ | `facets_hit` 1 | ตรงบางมิติ — เผื่อ user เลือกเพิ่ม |
| C) ใน sector ไม่ match | sector_code ตรงแต่ไม่ match keyword | จาก `get_process_overview` กรอง sector แล้วลบ A+B ออก |

- แสดง `matched` field ให้ user เห็นว่า "ตรงเพราะ keyword ตัวไหน" (UX)
- ให้ user ติ๊ก confirm กิจกรรมที่จะเอาเข้า RCM

### Step 5: ดึง RCM เต็ม

1. เรียก `get_process_rcm(process_code, sector_code)` สำหรับแต่ละ process ที่เลือก
2. กรองเอาเฉพาะ activity_code ที่ user เลือกใน Step 4
3. เลือกหลาย sector → เรียกทีละ sector (1 call = 1 sector engagement)

### Step 6: สร้าง RCM HTML + ผสานข้อมูล Step 2

1. สร้าง RCM HTML ตาม skill `kas-rcm-v1` (หรือ template v3 ใน skill นี้)
2. **ผสานข้อมูล Step 2 เข้า test procedures / คำถามสัมภาษณ์** — ปรับภาษาให้ตรงธุรกิจ
   - ⚠️ เนื้อหา RCM (risk/control/test) ต้องมาจาก database เท่านั้น — ข้อมูล Step 2 ใช้**ปรับ** test/คำถามให้ตรงธุรกิจ ไม่ใช่แต่ง control ใหม่ (ยึด R2: Zero Fabrication)

### ⚠️ Pitfalls เฉพาะ workflow นี้

1. **`find_activities` cap = 20 results** — ถ้า `total_matched` > 20 จะถูกตัด (`capped: true`) → แคบ keyword + process + sector ให้มากที่สุดก่อนเรียก หรือวนหลายชุด keyword
2. **sector list ไม่ต้อง scan ทุกครั้ง** — ใช้ `references/sector-codes.md` (31 codes ครบ) ไม่ต้อง `get_process_overview` 10 ครั้งเพื่อหา sector
3. **กลุ่ม C ต้องดึงจาก `get_process_overview`** — `find_activities` คืนเฉพาะที่ match keyword ไม่คืน "ใน sector ทั้งหมด" → กรองเองจาก overview
4. **UNVS รวมอัตโนมัติ** — ไม่ต้องให้ user เลือก UNVS ซ้ำ
5. **keywords_doc ห้ามใส่ระบบ IT** — ERP/WMS ไม่ใช่เอกสาร

---

## HTML Output Standards

ทุก HTML output ต้องมีคุณสมบัติเหล่านี้:

### 1. โครงสร้างไฟล์

```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>[ชื่อรายงาน] — [ชื่อบริษัท]</title>
  <style>
    /* CSS — ดู templates/ */
  </style>
</head>
<body>
  <!-- Header (clean, no icons — text only) -->
  <!-- Toolbar: Save + Print buttons + Search bar -->
  <!-- Summary bar: process count, coverage info -->
  <!-- Table wrapper with visible scrollbar -->
  <!-- Appendix -->
  <!-- Scripts (Save/Print/Search) -->
</body>
</html>
```

### 2. CSS Requirements
- ✅ ฟอนต์ไทย: `'Sarabun', 'Prompt', 'Tahoma', sans-serif`
- ✅ ตารางมี borders, striped rows, hover effect
- ✅ `contenteditable` elements มี border ล่าง dashed สีเทา, `cursor: text`
- ✅ Print-friendly (`@media print` — ซ่อน toolbar/summary, แสดงเต็มหน้า)
- ✅ **Visible styled scrollbar** — ใช้ `::-webkit-scrollbar` สไตล์ความสูง 12px, thumb สี #bdbdbd
- ✅ **Column width constraints** — ใช้ `max-width` + `word-break: break-word` ป้องกันคอลัมน์ยาวเกิน
- ✅ **Sticky header** — toolbar และ table header ติดด้านบนขณะ scroll

### 3. Header Rules
- ❌ **ห้ามใส่ icon/รูปแปลกๆ** ใน header — ใช้ text เท่านั้น (📋 emoji พอได้)
- ✅ Header เป็น gradient สีน้ำเงินเข้ม (`#1a237e` → `#283593`)
- ✅ แสดง: ชื่อรายงาน (h1) + metadata (ชื่อผู้จัดทำ, จำนวน processes/activities/controls)

### 4. Search/Filter Bar (MANDATORY สำหรับ RCM/ตารางใหญ่)
- ✅ `<input>` search box พร้อม `oninput` — ค้นหาข้อความในทุกแถว
- ✅ `<select>` dropdown เลือกกรองเฉพาะคอลัมน์ (ทุกคอลัมน์ / กระบวนการ / กิจกรรม / ความเสี่ยง / การควบคุม)
- ✅ ปุ่ม "✕ ล้าง" เพื่อ reset filter
- ✅ ตัวนับผลลัพธ์ — แสดง "N / total รายการ"
- ✅ ใช้ JavaScript `classList.add('hidden')` / `classList.remove('hidden')` ในการซ่อนแถว
- ✅ เพิ่ม `data-proc`, `data-act`, `data-risk`, `data-ctrl` attributes บน `<tr>` เพื่อให้ search เร็ว

### 5. Editable Sections
- `<div contenteditable="true" class="editable">` สำหรับข้อความ
- `<td contenteditable="true">` สำหรับเซลล์ตาราง
- ต้องมี `data-original` attribute เก็บค่าเริ่มต้น

### 6. Save Button
```html
<button onclick="saveHTML()">💾 Save as HTML</button>
<script>
function saveHTML() {
  const html = document.documentElement.outerHTML;
  const blob = new Blob(['<!DOCTYPE html>\n' + html], {type: 'text/html'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'RCM_<CLIENT>_' + new Date().toISOString().slice(0,10) + '.html';
  a.click();
  URL.revokeObjectURL(url);
}
</script>
```

### 7. Print/PDF Button
```html
<button onclick="window.print()">🖨️ Print / Save as PDF</button>
```
- ต้องมี `@media print` CSS ซ่อน toolbar/summary
- `@page { size: A3 landscape; margin: 8mm; }` สำหรับตารางกว้าง

### 8. Appendix
- ต้องมี section "ภาคผนวก" ท้ายไฟล์เสมอ
- แสดงข้อมูลดิบครบถ้วน:
  - Raw text จาก txt file ที่ user ให้
  - Raw output จาก MCP tools
- ใช้ `<details><summary>` แบบพับได้ (ไม่ใช้ `<pre>` เต็ม — ยาวเกิน)

### 9. Default RCM Column Layout

- ✅ **v1 (7 columns):** กระบวนการ | กิจกรรม | ความเสี่ยง | การควบคุมที่ควรมี | วิธีการตรวจสอบ | คำถามสัมภาษณ์ | ลักษณะควบคุม — สำหรับ 1-2 processes
- ✅ **v3 (8 columns + expand):** # | กิจกรรม | ความเสี่ยง | การควบคุม | Policy | Procedure | KRI | วิธีการตรวจสอบ — **แนะนำสำหรับทุกโปรเจคใหม่** (ดู 9b)
- ❌ **ห้ามใส่คอลัมน์ Poison เป็น default** — user ไม่ต้องการ (ใส่ใน expandable detail แทน)

### 🆕 9a. Enhanced RCM Template (v2 — Sheet Tabs + Risk Tags)

เมื่อสร้าง RCM แบบ multi-process (3+ processes) ให้ใช้ enhanced template จาก `references/rcm-html-template-v2.md` ซึ่งเพิ่ม:

| Feature | รายละเอียด |
|---------|-----------|
| 📑 **Sheet Tabs** | ปุ่มนำทางแต่ละ process แสดงจำนวน rows เป็น badge — `switchProcess()` JS |
| 📖/📕 **Expand/Collapse** | ปุ่มแสดงทุก Process หรือทีละ Process |
| 🏷️ **Risk Category Badges** | แท็กสีตามประเภท (Operational=ส้ม, Fraud=แดง, Compliance=น้ำเงิน, Reporting=เขียว, ฯลฯ) |
| 🔗 **Rowspan** | Activity code + name ยุบรวมข้ามแถว risk/control — ลดความซ้ำซ้อน |
| 🔍 **Column Filter** | `<select>` 6 ตัวเลือก: ทุกคอลัมน์, กิจกรรม, ความเสี่ยง, การควบคุม, วิธีการตรวจสอบ, คำถาม |
| 9️⃣ **9 Columns** | เพิ่มคอลัมน์ # (ลำดับ) + เปลี่ยน "กระบวนการ" เป็น "ประเภทความเสี่ยง" แบบ color tag |
| 🎨 **kas-htmlformat** | Border style พร้อม print 16:9 PPT |

**v2 Column Layout (9 columns):**
| # | Column | Width |
|---|--------|-------|
| 1 | # (ลำดับ) | 55px |
| 2 | กิจกรรม (code) | 90px |
| 3 | ชื่อกิจกรรม | 200px |
| 4 | ประเภทความเสี่ยง | 100px |
| 5 | ความเสี่ยง | 280px |
| 6 | การควบคุมที่ควรมี | 280px |
| 7 | วิธีการตรวจสอบ | 240px |
| 8 | คำถามสัมภาษณ์ | 200px |
| 9 | ลักษณะควบคุม | 85px |

### 🆕 9b. Interactive RCM Template (v3 — 8 Columns + Resize + Column Toggle + Expandable Detail)

**v3 เป็น template หลักที่แนะนำสำหรับทุกโปรเจคใหม่** — พัฒนาจาก session SICT (2026-08-09)
ดู template เต็มใน `references/rcm-html-template-v3.md`

| Feature | รายละเอียด |
|---------|-----------|
| 8️⃣ **8 Columns** | #, กิจกรรม(code:name), ความเสี่ยง, การควบคุม, Policy, Procedure, KRI, วิธีการตรวจสอบ |
| 📏 **Column Resize** | ลากขอบขวาของ header ปรับ width ได้ทุกคอลัมน์ |
| ⚙️ **Column Toggle** | Dropdown checkbox แสดง/ซ่อนคอลัมน์ — #,กิจกรรม,ความเสี่ยง ล็อค 🔒 |
| ▶ **Expandable Detail** | คลิก ▶ ข้างความเสี่ยง → แสดง Poison, Report, Validation, คำถามสัมภาษณ์ |
| 📑 **Sheet Tabs** | 9 process tabs พร้อม row count badges (เหมือน v2) |
| 🔍 **Search** | Full-text search พร้อม result counter |

**v3 Column Layout (8 columns):**
| # | Column | Source | Hideable | Width |
|---|--------|--------|:---:|------:|
| 1 | # | auto | 🔒 | 45px |
| 2 | กิจกรรม | `code: name` merged, rowspan | 🔒 | 200px |
| 3 | ความเสี่ยง + ▶ | `risk_name` | 🔒 | 280px |
| 4 | การควบคุมที่ควรมี | `control_name` | ✅ | 280px |
| 5 | Policy | `risk.policies[]` joined | ✅ | 280px |
| 6 | Procedure | `risk.procedures[]` joined | ✅ | 280px |
| 7 | KRI | `risk.indicator_name` | ✅ | 250px |
| 8 | วิธีการตรวจสอบ | `control.tests[]` joined | ✅ | 350px |

**v3 Detail Row (expandable):**
| Field | Source |
|-------|--------|
| 🔴 Poison | `risk.poison` (โลภะ/โทสะ/โมหะ) |
| 📈 Report | `risk.report_name` |
| 📎 Validation | `risk.validations[]` (2 items) |
| ❓ คำถามสัมภาษณ์ | `control.question_text` (from each control) |

**Build Strategy สำหรับไฟล์ใหญ่ (15-25 MB):**
1. `execute_code` → build CSS header → `write_file`
2. `execute_code` → build body HTML → write to `_body.html`
3. `execute_code` → build detail data JS + main JS → write to `_js.html`
4. `terminal` → `cat header body js > final.html`

**เมื่อไหร่ใช้ v3 vs v2 vs v1:**
| สถานการณ์ | ใช้ |
|-----------|-----|
| 1 process, แก้ไขทีละรายการ | v1 (7 columns) |
| 3+ processes, ต้องการ Risk Tags สี | v2 (9 columns + color badges) |
| **ทุกโปรเจคใหม่, ลูกค้าดู presentation** | **v3 (8 columns + resize + toggle + expand)** |
| ต้องการ Policy/Procedure/KRI ในคอลัมน์หลัก | v3 |
| ต้องการปรับ layout หน้างาน (ซ่อนคอลัมน์, ปรับ width) | v3 |

---

## Project File Structure

ทุก project ของ KAS เก็บที่:
```
C:\Users\ASUS\Hermes\projects\<project_name>\
  ├── nob_raw.txt              ← ข้อมูลดิบจากสัมภาษณ์
  ├── nob_summary.html         ← Workflow 2 output
  ├── audit_universe.html      ← Workflow 3 output
  ├── existing_controls.txt    ← การควบคุมที่มีอยู่จาก user
  ├── rcm_matrix_<process>.html ← Workflow 4 output
  └── control_analysis_<process>.html ← Workflow 5 output
```

---

## Common Pitfalls

1. **🔴 MCP tools ไม่ปรากฏใน agent tool list (CRITICAL)** — แม้ `hermes mcp test rcm` จะแสดง "Tools discovered: 8" แต่ agent อาจไม่เห็น `mcp_rcm_*` ใน tool list ที่ใช้งานได้ สาเหตุ:
   - Session ถูกเริ่มก่อน MCP server ถูก configure
   - MCP tools ถูก reload แล้ว (`MCP tools reloaded`) แต่ไม่ inject เข้า turn ปัจจุบัน
   - `mcp` Python package มี dependency issue (เช่น `pywin32` / `pywintypes` missing บน Windows sandbox)

   **✅ วิธีแก้ (เรียงตามลำดับ):**
     1. **Settings → MCP → ปุ่ม Reload MCP** → รอ notification "MCP tools reloaded" → `/reset`
     2. ถ้ายังไม่ได้ → **Settings → MCP → เลือก rcm → Remove → Add ใหม่** (ใส่ JSON เดิม) → `/reset`
     3. ถ้ายังไม่ได้ → **ปิด-เปิด Hermes Desktop ใหม่** (full restart)
     4. 🆕 **ถ้ายังไม่ได้ → ใช้ `rcm_http_client.py` fallback** (ดู Workflow 0) — เรียก Cloudflare ตรงผ่าน HTTP ไม่ต้องพึ่ง MCP tool injection เลย
   - **Verification หลัง `/reset`:** ส่งข้อความ "test" → agent ต้องเรียก `mcp_rcm_get_db_info` ได้ หรือใช้ `rcm_http_client.py`
2. **🆕 `get_process_rcm` — tool ใหม่ที่ดึงทั้ง process ใน call เดียว** — ใช้แทน `get_process_overview` + `get_activity` ทีละตัว เร็วกว่ามาก (9 processes = 9 calls แทน 277+ calls)
   - Parameters: `process_code`, `client_name`, `sectors` (list)
   - ส่งคืนทุก activities (ที่ตรง sector), risks, controls, tests, questions
   - Output ใหญ่ — ใช้ `execute_code` จัดการ batch processing
   - **⚠️ ข้อจำกัดของ `query.py`:** `--list-activities` ไม่คืน `sector_code` — ถ้าต้องกรองตาม sector (จำเป็นเสมอสำหรับ audit universe/RCM) ใช้ Workaround #3 แทน
2. **MCP tools ไม่โหลดเข้า session** — tools ถูก inject ตอน startup ถ้าเพิ่ม MCP ทีหลังต้อง `/reload-mcp` หรือ `/reset`
3. **Context overflow จาก full activity** — `mcp_rcm_get_activity` ส่งข้อมูลเยอะ (risks, controls, tests, policies, validations, procedures) → ดึงทีละ activity อย่าดึงทีเดียวหลายตัว
4. **OAuth token หมดอายุ** — Cloudflare Workers OAuth token มีอายุ ~1 ชั่วโมง (access token) และจะหมดอายุถ้าไม่มีการเรียกใช้ — `hermes mcp test rcm` ถ้า "invalid_token" / "401" → **✅ วิธีแก้เร็วสุด: รัน `rcm_http_client.py` ตัวเดียวก็ refresh ให้เสร็จ:**
   ```bash
   cd "C:\Users\ASUS\AppData\Local\hermes\skills\audit\kas-rcm-setup\scripts"
   python rcm_http_client.py --tool get_db_info
   ```
   ตัว client จะเจอ HTTP 401 → เรียก `_refresh_token()` (refresh_token grant) อัตโนมัติ → เขียน token ใหม่กลับ `mcp-tokens/rcm.json` → ใช้ได้ต่อทันที **ไม่ต้องไป Settings → MCP → reconnect เอง** (reconnect คือทางเลือกเฉพาะกรณี token หมดอายุแล้ว refresh_token ก็ใช้ไม่ได้ หรือ user ยังไม่เคย OAuth login เลย)
   - **เช็คอายุ token ก่อน:** `python -c "import json,time; d=json.load(open(r'C:\Users\ASUS\AppData\Local\hermes\mcp-tokens\rcm.json')); print('expired' if time.time()>d['expires_at'] else f\"{int((d['expires_at']-time.time())/60)} min left\")"`
5. **Admin ยังไม่เพิ่ม email** — user จะได้ error "Unauthorized" → แจ้งติดต่อ Admin (Thanat) เพื่อเพิ่ม email ใน allowlist
6. **HTML ภาษาไทยพัง** — ต้องใช้ `<meta charset="UTF-8">` และฟอนต์ที่รองรับไทย
7. **`contenteditable` ในตาราง** — อย่าลืม `white-space: pre-wrap` ใน `<td contenteditable>` เพื่อรักษา line break
8. **User แก้ไข HTML แล้ว แต่ save ไม่ได้** — ปุ่ม Save ต้องใช้ JavaScript `Blob` download — ต้องมี `<script>` block ใน HTML
8. **Print/PDF ไม่สวย** — ต้องมี `@media print` CSS เพื่อซ่อนปุ่ม, ปรับ margin, แสดงสีพื้นหลัง
9. **🔴 Sticky header หาย (scroll แล้ว header ไม่ติด)** — เกิดจาก ancestor element มี `overflow: hidden` (เช่น `.process-panel { overflow: hidden; }`) → สร้าง clipping boundary ที่ทำลาย `position: sticky`. **วิธีแก้:** 
   - ❌ ลบ `overflow: hidden` จาก parent ทุกตัวที่อยู่ระหว่าง scroll container กับ `<thead>`
   - ✅ ใช้ parent-child pattern — `.scroll-outer` ถือ `overflow: auto`, `<thead>` ใช้ `position: sticky; top: 0; z-index: 10;`
   - ✅ ตรวจสอบ chain: `.process-panel` → `.scroll-outer` → `table.rcm` → `thead` → `th` — ทุก ancestor ต้องไม่มี `overflow: hidden`
   - แบบเก่า (V3/V4 มี bug นี้):
   ```css
   .scroll-outer { width: 100%; max-width: 100vw; overflow: auto; height: calc(100vh - 185px); }
   table.rcm thead th { position: sticky; top: 0; }
   ```
10. **🔴 Horizontal scrollbar ไม่โผล่** — container ขยายตามตารางเพราะ `width: max-content`. **วิธีแก้:** ใช้ `table-layout: fixed` + กำหนด `min-width` ที่เกิน viewport + กำหนดความกว้างแต่ละคอลัมน์ผ่าน `th:nth-child(N)`:
   ```css
   table.rcm { table-layout: fixed; min-width: 1400px; width: 1400px; }
   table.rcm th:nth-child(1), table.rcm td:nth-child(1) { width: 100px; }
   table.rcm th:nth-child(2), table.rcm td:nth-child(2) { width: 200px; }
   /* ... */
   ```

10. **⚠️ การเรียก MCP โดยไม่มี business justification** — ห้ามถาม "ขอข้อมูลทั้งหมดของ process P" โดยไม่ได้ระบุว่าทำไปทำไมและ project ไหน → ต้องมี project context เสมอ
11. **⚠️ Agent พยายามวน loop ดึงข้อมูล** — agent อาจคิดว่า "ขอดึงทุก activity มาแคชไว้" → ห้ามเด็ดขาด! ต้องถาม user ก่อนทุกครั้งว่าจะเอาข้อมูล activity ไหน
11. **⚠️ Agent ถาม user ก่อนค้น internet** — เมื่อสกัดข้อมูลจากไฟล์ (NOB) แล้วยังไม่ครบ → agent ต้องค้น internet (Google Search Grounding) **ก่อน** ถาม user ไม่ใช่ถาม user ก่อนแล้วให้ user บอกให้ค้นทีหลัง → เป็นการเสียเวลาผู้ใช้
12. **HTML RCM header ห้ามใส่ icon/รูปแปลกๆ** — ใช้ text + emoji เท่านั้น (📋) — user feedback: "บรรทัดบนสุดมันแปลกๆ"
13. **Pitch Deck → RCM Mapping** — เมื่อ user มี pitch deck/proposal ที่ระบุ audit universe processes ไว้แล้ว:
    1. Map processes ของลูกค้า → RCM processes (ดูว่า process ไหนตรงกับ RCM process code ไหน)
    2. ใช้ `get_process_rcm` ดึง RCM สำหรับทุก process ที่เกี่ยวข้อง (9 calls = จบ)
    3. กรองเอาเฉพาะ UNVS + sector-specific activities ที่ตรงกับธุรกิจ
    4. เลือก 15-20 กิจกรรมสำคัญที่สุดตาม risk profile ของลูกค้า (high-risk processes ก่อน)
    5. สร้าง HTML RCM พร้อม search/filter, scrollbar, save/print
    6. ตั้งชื่อไฟล์: `RCM_<CLIENT>_v<N>.html`
15. **🔴 Tests และ Questions อยู่ที่ CONTROL level ไม่ใช่ RISK level** — `get_process_rcm` ส่ง tests/question เป็น field ในแต่ละ control ไม่ใช่ใน risk:
   - ❌ **ผิด:** `risk.get("tests")` / `risk.get("questions")` — จะได้ [] เสมอ
   - ✅ **ถูก:** `control["tests"]` (list ของ `{test_code, test_name}`) และ `control["question_text"]` (string)
   - แต่ละ control มี 2 tests และ 1 question — ต้องวนลูป `risk["controls"]` แล้วดึงจากแต่ละ control
   - **ตรวจสอบง่ายๆ:** ถ้าคอลัมน์วิธีการตรวจสอบกับคำถามสัมภาษณ์ว่างทั้งหมด → แสดงว่าดึงผิด level

16. **🔴 Risk-level fields ที่มีแต่ยังไม่ได้ใช้ใน default HTML** — ทุก risk มี field เหล่านี้ (100% coverage):
   - `poison`: โลภะ / โทสะ / โมหะ
   - `indicator_code`, `indicator_name`: KRI (ตัวชี้วัดความเสี่ยง)
   - `validations[]`: หลักฐานการตรวจสอบ (2 รายการต่อ risk, มี code + text)
   - `policies[]`: นโยบายที่เกี่ยวข้อง (2 ฉบับต่อ risk, มี code + text)
   - `procedures[]`: ขั้นตอนปฏิบัติงาน (2 ขั้นตอนต่อ risk, มี code + text)
   - `report_code`, `report_name`: รายงานที่เกี่ยวข้อง
   - **ถ้า user ถามถึง policy/procedure** → field เหล่านี้พร้อมใช้ทันที ไม่ต้อง query เพิ่ม
   - **วิธีเพิ่มลง HTML:** ใช้ expandable detail row (คลิกแถว risk แล้ว expand แสดง detail) ดีกว่าเพิ่มคอลัมน์เพราะตารางกว้างอยู่แล้ว
   - ดูโครงสร้างเต็มใน `references/database-schema.md`

17. **⛔ ห้ามใช้ local dataset files (R5 — ใช้ MCP เท่านั้น)** — เมื่อ `get_process_rcm` ไม่ inject อย่า fallback ไป local clone/`dataset_*.json`/`query.py` เด็ดขาด (ขัด Data Protection Policy) — ใช้ `rcm_http_client.py` (ใน `scripts/`) เรียก Cloudflare ตรงผ่าน HTTP แทน (ดู Workflow 0)

18. **🔴 Activity list แสดงแค่ code (ไม่โชว์ชื่อเต็ม)** — `data-act` attribute เก็บเฉพาะ activity code (เช่น \"AF-UNVS-001\") ไม่ใช่ชื่อเต็ม. ดึงชื่อเต็มจาก `td[data-col=\"1\"]` หรือ `td.act-merge` → `.textContent.trim()`

19. **🔴 Toolbar 2 แถว** — user ต้องการแถวเดียว. ใช้ `flex-wrap: nowrap`, `overflow-x: auto`, ลด padding/font, ย่อ label เหลือ icon (`title` แทน), `flex-shrink: 0`

20. **🔴 Split-panel sidebar ถูกปฏิเสธ** (V4) — user ชอบ popup modal สำหรับ filter (V5 pattern: `openActPicker()` → modal checklist + apply)

21. **🔴 contenteditable cell แก้ไขผ่าน script** — ใช้ `.textContent` ไม่ใช่ `.innerText` หรือ `.innerHTML`

22. **🔴 ไม่มี tool `list_sectors` — ใช้ `references/sector-codes.md`** — database มี **31 sector codes** (DB v4) แต่ไม่มี tool คืนรายชื่อ sector โดยตรง → ใช้ `references/sector-codes.md` (31 codes + ชื่อไทย + 9 หมวด, Admin confirm 2026-08-17) ได้เลย ไม่ต้อง derive ใหม่ทุกครั้ง (`references/sector-mapping.md` เป็นไฟล์เก่า เก็บ detail การ parse SET ไว้ แต่ canonical = sector-codes.md)

23. **🔴 `find_activities` มี cap = 20 results** — output มี `total_matched` / `returned` / `capped`; ถ้า `capped: true` แปลว่ามี match เกิน 20 ถูกตัด → ต้องแคบ keyword + `process_code` + `sector_code` ให้มากที่สุดก่อนเรียก หรือวนเรียกหลายชุด keyword โครงสร้าง result: `{activity_code, activity_name, process_code, sector_code, facets_hit, score, matched:{activity[],person[],doc[]}}` — `sector_code` ใช้ filter ต่อได้

24. **`rcm_http_client.py` ใช้ `_tool(name, args)` เรียก tool ใดก็ได้** — แม้ client ยังไม่มี wrapper (เช่น `find_activities`) ก็เรียก `client._tool("find_activities", {...})` ได้ตรง ๆ เป็น escape hatch สำหรับ tool ใหม่ที่ยังไม่ได้ wrap

---

## Verification Checklist

- [ ] `hermes mcp test rcm` → ✓ Connected, ✓ Tools discovered: 8
- [ ] `mcp_rcm_get_db_info` ทำงานได้
- [ ] NOB interview ครบ 7 หัวข้อ
- [ ] `nob_raw.txt` ถูกบันทึก
- [ ] `nob_summary.html` แก้ไขได้ + save/print ได้
- [ ] `audit_universe.html` มี activity list ที่ถูกต้อง + checkbox ทำงาน
- [ ] `rcm_matrix_<process>.html` มี 7 คอลัมน์ครบ + แก้ไขได้ (หรือใช้ v2 template ถ้า multi-process)
- [ ] `rcm_matrix_<client>.html` (v2) มี Sheet Tabs + Risk Tags + Expand/Collapse ถ้า 3+ processes
- [ ] `control_analysis_<process>.html` มี ✅/⚠️/🔴 + test procedures ที่ปรับแล้ว
- [ ] ทุก HTML มีภาคผนวกแสดงข้อมูลดิบ
- [ ] ⛔ Data Protection: ไม่มีการ dump ทั้งฐานข้อมูล (get_activity ≤ 20 ครั้ง)
- [ ] ⛔ Data Protection: มี project context ทุกครั้งที่เรียก MCP
- [ ] ⛔ Data Protection: mcp_access.log ถูกบันทึกทุกครั้ง
