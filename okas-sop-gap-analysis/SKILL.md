---
name: okas-sop-gap-analysis
description: วิเคราะห์ช่องว่างระหว่าง SOP กับ Master Context — เทียบ key controls, ระบุ substitute control, กำหนดตำแหน่งแก้ไขใน SOP, ออกเป็น editable HTML พร้อม export JSON/Text
version: 1.0.0
author: OKAS (Kandit Advisory Services)
metadata:
  hermes:
    tags: [sop-review, gap-analysis, internal-audit, master-context, policy-review, OKAS]
    related_skills: [kas-htmlformat, okas-markitdown, okas-guard]
---

# OKAS SOP Gap Analysis

ใช้เมื่อต้องสอบทาน SOP เทียบกับ Master Context (To-be Process) — ตรวจสอบว่า key controls จาก Master Context ปรากฏใน SOP ครบถ้วนหรือไม่ ระบุตำแหน่งแก้ไข พร้อมสร้าง output เป็น HTML แบบ editable

## Overview

Workflow นี้ใช้สำหรับงาน Internal Audit / ที่ปรึกษา ที่มี:
- **Master Context** — เอกสารที่ระบุ key controls, policies, documents ที่ควรมี (ตัวตั้ง)
- **SOP** — นโยบาย/คู่มือปฏิบัติงานที่ทีมออกแบบระบบเขียน (สิ่งที่ตรวจสอบ)
- **OAI Review** — (ถ้ามี) ผลการสอบทานที่คนอื่นทำไว้ก่อนหน้า

## หลักการสำคัญ (Critical Rules)

1. **SOP เป็นตัวตั้งทางซ้าย** — เทียบ SOP → MC ไม่ใช่ MC → SOP
2. **กระบวนการ cross-cutting แทรกอยู่ในแต่ละ SOP** — เช่น กรอบอำนาจอนุมัติ, บริหารสัญญา, ประชุมผู้บริหาร ไม่ต้องแยกวิเคราะห์ต่างหาก
3. **Substitute Control = Acceptable** — ถ้า SOP มีการควบคุมทดแทนที่เพียงพอ ถือว่าผ่าน แต่ต้องระบุให้ชัดเจนว่าอะไรคือการควบคุมทดแทน
4. **ระบุตำแหน่งแก้ไขให้ชัดเจน** — ต้องบอกได้ว่าให้แก้ใน SOP หัวข้อไหน ขั้นตอนไหน ประโยคไหน
5. **ภาษาเป็นทางการ** — หลีกเลี่ยงคำ: โดยปกติ, อย่างเป็นทางการ ใช้: เป็นลายลักษณ์อักษร, อย่างเป็นระบบ
6. **ห้ามแต่งเอง ห้ามมโน** — ทุก gap ต้องอ้างอิงจาก Master Context และ SOP ตัวจริงเท่านั้น

## Workflow (5 Phases)

### Phase 1: แปลงไฟล์ทั้งหมดเป็น Markdown

ใช้ `okas-markitdown` แปลงไฟล์ Master Context (HTML/JSON), SOP (DOCX/PDF), และ OAI Review (DOCX) เป็น Markdown

### Phase 2: สกัด Key Controls จาก Master Context

- อ่าน JSON data จาก Master Context HTML (extract จาก `<script id="omni-data">`)
- แสดงโครงสร้าง: processes, steps, controls, policies, documents
- จับคู่ SOP แต่ละฉบับกับ Master Context process (mapping table)

### Phase 3: สร้าง Gap Analysis ของตัวเองก่อน (อย่าเทียบกับ Reviewer)

สำหรับแต่ละ SOP:
1. อ่าน SOP ฉบับเต็ม → ระบุ sub-processes (เช่น D101-D107)
2. เทียบกับ MC steps ทีละขั้นตอน
3. สำหรับแต่ละ gap:
   - อธิบายสิ่งที่ขาด
   - ตรวจสอบว่ามีการควบคุมทดแทน (substitute control) หรือไม่
   - ระบุตำแหน่งแก้ไขใน SOP (หัวข้อ, ขั้นตอน, ประโยค)
   - ระบุเอกสารที่ควรเพิ่ม
4. **อย่าเทียบกับของ Reviewer ในขั้นตอนนี้**

### Phase 4: เทียบกับ Reviewer (ถ้ามี)

หลังจากสร้าง gap analysis ของตัวเองเสร็จแล้ว:
- เทียบทีละข้อว่า reviewer จับได้หรือพลาด
- ระบุ pattern: reviewer เก่งเรื่องไหน พลาดเรื่องไหน

### Phase 5: สร้าง Output HTML + D/N Cross-Reference

#### 5A: Cross-Reference กับ OAI Review

หลังจากสร้าง gap analysis ของตัวเองเสร็จ:
1. Parse OAI Review → สกัดทุกข้อของ reviewer แยกตาม SOP
2. เทียบ AI gaps กับ reviewer findings ทีละข้อ:
   - ตรงกัน → tag **(D)** = Duplicate (reviewer ก็พบ gap นี้)
   - ไม่ตรง → tag **(N)** = New (KAS Team เพิ่มเอง)
3. ข้อที่ reviewer พบแต่ AI ไม่พบ → เพิ่มเป็น gap ใหม่ tagged **(N)**
4. ไม่ต้องมี Appendix — reviewer-only items คือ gap ปกติ

#### 5B: D/N Tag Format

```
Title format: "2.1 Gap — Short Name (D)" หรือ "2.1 Gap — Short Name (N)"
```

- (D) และ (N) ต่อท้ายชื่อ gap ใน `<div class="title">...</div>`
- ห้ามใช้ badge ลอย ห้ามใช้ W/N
- ต้องมี legend: "(D) = Duplicate — ตรงกับ OAI Review   (N) = New — KAS Team เพิ่ม"

#### 5C: การควบคุมทดแทน Format

- ใช้คำว่า **"การควบคุมทดแทน"** เต็มคำ — ห้ามใช้ emoji หรือสัญลักษณ์ 🔄 ⚠️ แทน
- Content: "มีบางส่วน — SOP XX (ชื่อ) มีกระบวนการ... ซึ่งครอบคลุม... แต่ยังขาด..."
- หรือ "ไม่มี — [เหตุผลว่าทำไมไม่มี compensating control]"

#### 5D: HTML Template Generation (Batch Mode)

สร้าง HTML ตาม kas-htmlformat structure พร้อม:
- Editable text boxes (contenteditable) — 4 กล่องต่อ gap
- Toolbar: Save / Save As / Export JSON / Export Text
- Auto-save + Ctrl+S
- Print landscape (16:9)

## Output Structure

แต่ละ Gap Item ต้องมีองค์ประกอบครบ:

```
1. ชื่อเอกสาร SOP: <ชื่อไฟล์ SOP>
2. การควบคุมสำคัญที่ระบุใน Master Context แต่ไม่ได้ระบุใน SOP
  2.X <ชื่อการควบคุม>: ควรเติมในเอกสาร SOP ตรงหัวข้อไหน อย่างไร
     - 🔴 Gap: สิ่งที่ขาดหายไป (อ้างอิง MC)
     - 🔄 การควบคุมทดแทน: มี/ไม่มี/ไม่เพียงพอ (พร้อมเหตุผล)
     - 📍 ตำแหน่งแก้ไขใน SOP: หัวข้อ/ขั้นตอน/ประโยคที่ต้องแก้
     - ✏️ วิธีแก้ไข: ข้อความที่จะเพิ่ม/แก้ไข
     - 📄 เอกสารที่ควรเพิ่ม: รายการเอกสาร + ตำแหน่งใน SOP
```

## HTML Box Colors (4 กล่องต่อ Gap)

| กล่อง | CSS Class | สี | เนื้อหา |
|---|---|---|---|
| 🔴 Gap | `.box-label.gap` | แดง (#fef2f2) | สิ่งที่ขาดหายไป |
| 🔄 Substitute | `.box-label.sub` | เหลือง (#fffbeb) | การควบคุมทดแทน |
| 📍 Fix | `.box-label.action` | ฟ้า (#dbeafe) | ตำแหน่ง + วิธีแก้ไข |
| 📄 Docs | `.box-label.doc` | เขียว (#ecfdf5) | เอกสารที่ควรเพิ่ม |

## SOP → Master Context Mapping

| SOP | Master Context Process |
|-----|----------------------|
| 01 R&D | (embedded in other processes) |
| 02 Cost | (embedded — procurePay, management) |
| 03 Fixed Asset | fixedAssets |
| 04 HR & Payroll | hr |
| 05 Petty Cash | pettyCash |
| 06 Cash Advance | pettyCash |
| 07 Procurement | procurePay |
| 08 Inventory & Warehouse | procurePay |
| 09 Sales Revenue | salesGov, salesPrivate |
| 10 IT | itgc, pdpa |
| 11 Budget | management |
| 12 การเงินและบัญชี | procurePay, management |
| 13 Installation & O&M | installOm |

หมายเหตุ: approval, contracts, rpt, management เป็น cross-cutting — แทรกอยู่ในแต่ละ SOP ไม่ต้องแยกวิเคราะห์

## ⛔ CRITICAL RULE: ห้ามสร้าง Gap โดยไม่อ่าน SOP จริง

**นี่คือข้อผิดพลาดร้ายแรงที่สุดที่เคยเกิดขึ้น** — Agent สร้าง gap สำหรับ SOP 05-13 โดยดูแค่ Master Context แล้ว assume ว่า SOP ไม่มี ทั้งที่ SOP มีกระบวนการนั้นอยู่แล้ว

```
❌ WRONG: อ่านแค่ MC → "MC บอกว่าต้องมี X → SOP ต้องไม่มี X" → flag เป็น gap
✅ RIGHT: อ่าน SOP ก่อน → ตรวจสอบว่ามี X จริงไหม → ถ้ามี = ไม่ใช่ gap
```

**ก่อน flag gap ทุกครั้ง ต้องถามตัวเอง**: "เราอ่าน SOP ตัวจริงหรือยัง? เราพบบรรทัดที่ระบุว่ามีการควบคุมนี้หรือไม่?"

### Phase 3.5: Verify Gaps Against SOP (MANDATORY — ห้ามข้าม)

หลังจากสร้าง gap list:
1. สำหรับแต่ละ gap — ตรวจสอบ SOP ตัวจริงว่ามีการควบคุมนั้นหรือไม่
2. ใช้ keyword search ใน SOP markdown:
   ```python
   # Example: verify "Surprise Count" gap
   if 'สุ่มตรวจนับ' in sop_text or 'surprise count' in sop_text.lower():
       print("⚠️ SOP has this — NOT a real gap")
   ```
3. ถ้า SOP มีแล้ว → **ลบ gap นั้นทันที** ห้ามเก็บไว้ "เผื่อมีประโยชน์"
4. ถ้าไม่แน่ใจ → อ่าน section นั้นใน SOP โดยตรง (read_file แบบระบุ offset)

## Common Pitfalls

1. **⛔ สร้าง gap โดยไม่อ่าน SOP** — CRITICAL: ต้องอ่าน SOP ทุกฉบับก่อน flag gap (ดูหัวข้อด้านบน)
2. **ใช้ MC เป็นตัวตั้ง** — ต้องใช้ SOP เป็นตัวตั้ง MC เป็นตัวอ้างอิง
3. **ลืมตรวจสอบ substitute control** — ต้องถามทุกครั้งว่า SOP มีการควบคุมทดแทนไหม
4. **ระบุตำแหน่งแก้ไขไม่ชัด** — ต้องระบุหัวข้อ/ขั้นตอน/ประโยคที่จะแก้
5. **รีบเทียบกับ reviewer ก่อนทำเองเสร็จ** — ต้องทำ gap analysis ของตัวเองให้เสร็จก่อน
6. **ภาษากึ่งถาม-ตอบ** — ต้องใช้ภาษาทางการ ไม่ใช้ "อยากให้เพิ่มเรื่อง" หรือ "ขาดเรื่อง"
7. **พลาด gap เชิงโครงสร้าง** — กลุ่มกิจกรรมที่หายไปทั้งกลุ่ม (เช่น Project Asset Management) มองข้ามง่ายกว่า gap รายจุด
8. **อ่านไฟล์ binary โดยตรง** — ต้องใช้ okas-markitdown แปลงก่อนเสมอ
9. **D/N tags ผิดตำแหน่ง** — ต้องต่อท้ายชื่อ gap เช่น "2.1 Gap — Asset Requisition (D)" ไม่ใช้ badge ลอย
10. **Substitute Control ใช้สัญลักษณ์แทนข้อความ** — ต้องใช้คำว่า "การควบคุมทดแทน" เต็มคำ ห้ามใช้ 🔄 ⚠️ → แทน

## Verification Checklist

- [ ] Phase 1: แปลงไฟล์ทั้งหมดเป็น .md แล้ว
- [ ] Phase 2: สกัด MC structure ครบทุก process
- [ ] ⛔ Phase 3: **อ่าน SOP ทุกฉบับ** ก่อนสร้าง gap list (ห้ามข้าม — ดู CRITICAL RULE)
- [ ] Phase 3.5: **Verify ทุก gap** — ตรวจสอบ SOP ตัวจริงว่ามีการควบคุมนั้นหรือไม่
- [ ] ทุก gap มี: MC ref, SOP status, substitute control check, fix location, documents
- [ ] Phase 4: เทียบกับ reviewer (ถ้ามี) — tag (D)/(N)
- [ ] Phase 5: HTML output — slide-container, editable boxes, save/export toolbar
- [ ] D/N tags ต่อท้ายชื่อ gap ถูกต้อง — ไม่ใช้ badge ลอย
- [ ] การควบคุมทดแทนใช้ข้อความเต็ม — ไม่มี 🔄 ⚠️ →
- [ ] ภาษาเป็นทางการ — ไม่มี "โดยปกติ", "อย่างเป็นทางการ"
- [ ] ระบุตำแหน่งแก้ไขใน SOP ชัดเจน (หัวข้อ/ขั้นตอน/ประโยค)
