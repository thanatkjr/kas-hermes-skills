---
name: kas-rcm-setup
description: ตั้งค่าและใช้งาน RCM MCP Server สำหรับงานตรวจสอบภายใน — สอบถาม Nature of Business, สร้าง Audit Universe, Standard Risk Control Matrix, และ Control Analysis Report พร้อม output เป็น HTML ที่แก้ไขได้และ save เป็น PDF ได้
version: 1.0.0
author: KAS / Thanat Kerdcharoen
license: Proprietary — KAS Internal Use Only
metadata:
  hermes:
    tags: [kas, internal-audit, rcm, mcp, risk-control-matrix, audit-program]
    related_skills: [kas-guard, kas-note, kas-markitdown, kas-htmlformat]
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
hermes mcp test rcm    # ต้องเห็น "✓ Connected" + "✓ Tools discovered: 6"
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
| `mcp_rcm_get_activity` | ดู 1 activity แบบเต็ม (risks, controls, tests, policies, validations, procedures) | ส่ง `process_code` + `activity_code` |
| `mcp_rcm_get_risk_detail` | ดู 1 risk พร้อมทุก field (poison, indicator, validations, policies, procedures, report, controls, tests) | ส่ง `process_code` + `risk_code` |
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

- ✅ `✓ Connected` + `✓ Tools discovered: 6` → พร้อมทำงาน
- ❌ `✗ Failed` → 
  - "invalid_token" → user ยังไม่ได้ OAuth login → ให้เปิด Settings → MCP → Edit server → reconnect
  - "Connection refused" → Cloudflare Worker อาจ offline → แจ้ง admin

### Step 1.3: ตรวจสอบ tools

เรียก `mcp_rcm_get_db_info` เพื่อยืนยันว่าฐานข้อมูลพร้อมใช้

---

## Workflow 2: Nature of Business (NOB)

**Goal:** รวบรวมข้อมูลธุรกิจของลูกค้า → สรุปเป็น HTML ที่แก้ไขได้

### Step 2.1: รับข้อมูล

ให้ user เลือกวิธีให้ข้อมูล:

**Option A: สัมภาษณ์ทีละส่วน (ถามทีละหัวข้อ)**

ถามทีละหัวข้อ 6 ส่วน รอคำตอบก่อนถามต่อ:

1. **สินค้า/บริการหลัก** — กิจการขายสินค้าหรือบริการอะไร? มีกี่กลุ่ม? แต่ละกลุ่มมีสัดส่วนรายได้เท่าไร?
2. **ลูกค้าหลัก** — ลูกค้าเป็นใคร? B2B/B2C/Government? มีลูกค้ารายใหญ่กี่ราย? ช่องทางขาย?
3. **ผู้ขาย/ผู้ให้บริการหลัก** — ซื้อวัตถุดิบ/สินค้า/บริการจากใคร? มี vendor หลักกี่ราย? วิธีการจัดซื้อ?
4. **รายได้และค่าใช้จ่ายหลัก** — รายได้มาจากไหน? รับชำระอย่างไร? ค่าใช้จ่ายหลักมีอะไรบ้าง? โครงสร้างต้นทุน?
5. **รูปแบบการผลิต/ให้บริการ** — กระบวนการผลิต/ให้บริการเป็นอย่างไร? มีสต็อกสินค้าหรือไม่? ใช้เครื่องจักรอะไร?
6. **กฎหมาย/ข้อบังคับ/สัญญาสำคัญ** — อยู่ภายใต้กฎหมายอะไร? มีใบอนุญาตอะไร? สัญญาสำคัญกับคู่ค้า? มาตรฐานที่ต้องปฏิบัติ?
7. **ระบบ ERP/IT ที่ใช้** — ใช้ระบบอะไร? โมดูลที่ใช้? ระบบบัญชี? ระบบ payroll?

⚠️ **ทุกครั้งที่ถาม** — บันทึกคำตอบลง text file ทันทีที่ `C:\Users\ASUS\Hermes\projects\<project_name>\nob_raw.txt`

**Option B: รับไฟล์ที่ user upload**

1. User upload ไฟล์ (PDF, DOCX, TXT) → ใช้ `kas-markitdown` skill แปลงเป็น text
2. อ่านเนื้อหาทั้งหมด → สกัดประเด็นตาม 7 หัวข้อ
3. ถ้าข้อมูลไม่ครบ → ถามเฉพาะหัวข้อที่ขาด

### Step 2.2: ตรวจสอบความครบถ้วน

หลังจากได้ข้อมูลครบ 7 หัวข้อ:
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

สร้าง HTML ที่ `C:\Users\ASUS\Hermes\projects\<project_name>\rcm_matrix_<process>.html`

**HTML ต้องมี (ตาราง 6 คอลัมน์):**

| กิจกรรม | ความเสี่ยง | การควบคุมที่ควรมี | วิธีการตรวจสอบ | คำถามสัมภาษณ์ | Poison |
|---------|-----------|-------------------|---------------|---------------|--------|

แต่ละแถว:
- Activity → `contenteditable` (user ปรับชื่อกิจกรรมให้ตรงกับองค์กรได้)
- Risk → `contenteditable`
- Control → `contenteditable` (user เพิ่ม/แก้ไข control ได้)
- Test → `contenteditable` (user ปรับ test procedure ได้)
- Question → `contenteditable`
- Poison → display only

ปุ่ม:
- 💾 **Save as HTML**
- 🖨️ **Print / Save as PDF**
- ➕ **Add Row** (เพิ่ม control เอง)

ภาคผนวก: raw MCP output

---

## Workflow 5: Control Analysis Report

**Goal:** เปรียบเทียบ "การควบคุมที่ควรมี" (จาก RCM) กับ "การควบคุมที่มีอยู่" (จาก user) → Gap Analysis

### Step 5.1: รับข้อมูลการควบคุมที่มีอยู่

User ต้องให้ข้อมูล "การควบคุมที่มีอยู่" — มาในรูปแบบ:

**Option A: txt file จาก note skill**
- User สร้าง note ด้วย `kas-note` skill → ได้ txt file
- อ่านไฟล์ → สกัดเอา existing controls

**Option B: ไฟล์อื่นที่ user upload**
- User upload PDF/DOCX/TXT → แปลงด้วย `kas-markitdown` → อ่าน controls

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
  <!-- Header -->
  <!-- Content (contenteditable sections) -->
  <!-- Appendix -->
  <!-- Scripts (Save/Print buttons) -->
</body>
</html>
```

### 2. CSS Requirements
- ✅ ฟอนต์ไทย: `'Sarabun', 'Prompt', sans-serif`
- ✅ ตารางมี borders, striped rows, hover effect
- ✅ `contenteditable` elements มี border ล่าง dashed สีเทา
- ✅ Print-friendly (`@media print` — ซ่อนปุ่ม, แสดงเต็มหน้า)
- ✅ Responsive (max-width, overflow-x: auto สำหรับตาราง)

### 3. Editable Sections
- `<div contenteditable="true" class="editable">` สำหรับข้อความ
- `<td contenteditable="true">` สำหรับเซลล์ตาราง
- ต้องมี `data-original` attribute เก็บค่าเริ่มต้น

### 4. Save Button
```html
<button onclick="saveHTML()">💾 Save as HTML</button>
<script>
function saveHTML() {
  const html = document.documentElement.outerHTML;
  const blob = new Blob(['<!DOCTYPE html>\n' + html], {type: 'text/html'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = document.title.replace(/[^a-z0-9ก-๙]/gi, '_') + '.html';
  a.click();
  URL.revokeObjectURL(url);
}
</script>
```

### 5. Print/PDF Button
```html
<button onclick="window.print()">🖨️ Print / Save as PDF</button>
```

### 6. Appendix
- ต้องมี section "ภาคผนวก" ท้ายไฟล์เสมอ
- แสดงข้อมูลดิบครบถ้วน:
  - Raw text จาก txt file ที่ user ให้
  - Raw output จาก MCP tools
- ใช้ `<pre>` tag หรือ `<details><summary>` แบบพับได้

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

1. **MCP tools ไม่โหลดเข้า session** — tools ถูก inject ตอน startup ถ้าเพิ่ม MCP ทีหลังต้อง `/reload-mcp` หรือ `/reset`
2. **Context overflow จาก full activity** — `mcp_rcm_get_activity` ส่งข้อมูลเยอะ (risks, controls, tests, policies, validations, procedures) → ดึงทีละ activity อย่าดึงทีเดียวหลายตัว
3. **OAuth token หมดอายุ** — Cloudflare Workers OAuth token อาจหมดอายุ → `hermes mcp test rcm` ถ้า "invalid_token" → reconnect
4. **Admin ยังไม่เพิ่ม email** — user จะได้ error "Unauthorized" → แจ้งติดต่อ Admin (Thanat) เพื่อเพิ่ม email ใน allowlist
5. **HTML ภาษาไทยพัง** — ต้องใช้ `<meta charset="UTF-8">` และฟอนต์ที่รองรับไทย
6. **`contenteditable` ในตาราง** — อย่าลืม `white-space: pre-wrap` ใน `<td contenteditable>` เพื่อรักษา line break
7. **User แก้ไข HTML แล้ว แต่ save ไม่ได้** — ปุ่ม Save ต้องใช้ JavaScript `Blob` download — ต้องมี `<script>` block ใน HTML
8. **Print/PDF ไม่สวย** — ต้องมี `@media print` CSS เพื่อซ่อนปุ่ม, ปรับ margin, แสดงสีพื้นหลัง
9. **⚠️ การเรียก MCP โดยไม่มี business justification** — ห้ามถาม "ขอข้อมูลทั้งหมดของ process P" โดยไม่ได้ระบุว่าทำไปทำไมและ project ไหน → ต้องมี project context เสมอ
10. **⚠️ Agent พยายามวน loop ดึงข้อมูล** — agent อาจคิดว่า "ขอดึงทุก activity มาแคชไว้" → ห้ามเด็ดขาด! ต้องถาม user ก่อนทุกครั้งว่าจะเอาข้อมูล activity ไหน

---

## Verification Checklist

- [ ] `hermes mcp test rcm` → ✓ Connected, ✓ Tools discovered: 6
- [ ] `mcp_rcm_get_db_info` ทำงานได้
- [ ] NOB interview ครบ 7 หัวข้อ
- [ ] `nob_raw.txt` ถูกบันทึก
- [ ] `nob_summary.html` แก้ไขได้ + save/print ได้
- [ ] `audit_universe.html` มี activity list ที่ถูกต้อง + checkbox ทำงาน
- [ ] `rcm_matrix_<process>.html` มี 6 คอลัมน์ครบ + แก้ไขได้
- [ ] `control_analysis_<process>.html` มี ✅/⚠️/🔴 + test procedures ที่ปรับแล้ว
- [ ] ทุก HTML มีภาคผนวกแสดงข้อมูลดิบ
- [ ] ⛔ Data Protection: ไม่มีการ dump ทั้งฐานข้อมูล (get_activity ≤ 20 ครั้ง)
- [ ] ⛔ Data Protection: มี project context ทุกครั้งที่เรียก MCP
- [ ] ⛔ Data Protection: mcp_access.log ถูกบันทึกทุกครั้ง
