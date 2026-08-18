---
name: kas-sop-review-html
description: Generate editable SOP Review HTML files with gap analysis — compare SOPs against Master Context, produce 16:9 slide-container HTML with editable boxes, toolbar (Save/SaveAs/ExportJSON/AddPage/ExportText), ready for print/PPTX conversion.
version: 1.0.0
tags: [sop-review, gap-analysis, html, editable, pptx, internal-audit]
related_skills: [kas-htmlformat, kas-ia-report-helper, okas-markitdown]
---

# KAS SOP Review HTML Generator

สร้างไฟล์ HTML สำหรับสอบทาน SOP เทียบกับ Master Context — มีกล่องข้อความที่แก้ไขได้ (contenteditable), Toolbar สำหรับ Save/Export/Add Page, และโครงสร้าง slide-container 16:9 landscape พร้อมแปลงเป็น PPTX

## When to Use

- User มี Master Context (To-be Process) และ SOP หลายฉบับที่ต้องสอบทาน
- User ต้องการ output เป็น HTML ที่สามารถแก้ไข แชร์ และ print/convert เป็น PowerPoint ได้
- User ต้องการให้ทีม review ต่อได้โดยแก้ไขใน browser โดยตรง

## Workflow

### Phase 1: Prepare Data
1. แปลง SOP และ Master Context เป็น Markdown ด้วย `okas-markitdown`
2. อ่าน Master Context → สกัด key controls (Policy, Control, Documents) ต่อขั้นตอน
3. อ่าน SOP แต่ละฉบับ → สกัดโครงสร้าง (กระบวนการย่อย, การควบคุมภายใน, เอกสาร)

### Phase 2: Gap Analysis (กฎเหล็ก)

**🚨 CRITICAL — ห้ามแต่ง gap โดยไม่อ่าน SOP (บทเรียนจาก Oxygen AI Project)**

ในโปรเจกต์ Oxygen AI (สิงหาคม 2569) — AI วิเคราะห์ gap สำหรับ SOP 05-13 **โดยไม่ได้อ่าน SOP จริง** — ใช้ Master Context อย่างเดียวฟันธงว่า SOP ขาด → ผลลัพธ์: แต่ง gap ไป ~30 รายการที่ SOP มีอยู่แล้ว (เช่น SOP 13 มี O101-O112 ครบ แต่ flag ทั้ง 4 ข้อเป็น gap)

**Loss**: เสียเวลา regenerate 3 รอบ (v1 → v2 → v3), ผู้ใช้เสียความเชื่อมั่น, ต้องอ่าน SOP จริงทั้งหมดภายหลังแล้วแก้ใหม่ทั้งหมด

**กฎเหล็ก (ต้องทำตามลำดับ ห้ามข้าม):**
1. **อ่าน SOP markdown ทุกฉบับให้จบก่อน** — อ่านทุกหน้า ทุกกระบวนการย่อย ทุกการควบคุมภายใน — ห้ามข้าม ห้ามดูแค่สารบัญ
2. บันทึกทุกกระบวนการย่อย, การควบคุมภายใน, และเอกสารที่มีใน SOP — **ทำ checklist ว่ามีอะไรบ้าง**
3. **อย่าเริ่มวิเคราะห์ gap จนกว่าจะอ่าน SOP ครบทุกฉบับ**
4. เทียบกับ Master Context ทีละขั้นตอน — หาเฉพาะสิ่งที่ **ขาดจริง**
5. **ถ้า SOP มี control นั้นอยู่แล้ว = ไม่ใช่ gap** — ลบทิ้งทันที
6. **ห้ามแต่ง gap จาก MC โดยไม่อ่าน SOP** — คือความผิดพลาดร้ายแรงที่สุด ทำให้ output ทั้งหมดใช้ไม่ได้
7. **ถ้า SOP มีครบทุกอย่าง = 0 gaps = PASS** — อย่าพยายามหา gap ให้เจอจนมั่ว
8. **ตรวจสอบ markdown ว่าถูกต้อง** — ก่อนวิเคราะห์ให้เทียบ markdown กับต้นฉบับ .docx/.pdf อย่างน้อย 1 จุดต่อ SOP เพื่อยืนยันว่า conversion ไม่เพี้ยน

**ขั้นตอน Gap Analysis (ทำตามลำดับ):**
1. **ใช้ SOP เป็นตัวตั้ง** — ไม่ใช้ MC เป็นตัวตั้ง
2. **อ่าน SOP ให้ครบก่อน** — ห้าม assume, ห้ามเดา, ห้ามแต่ง
3. **สร้าง output ของตัวเองก่อน** — ยังไม่เทียบกับของ reviewer คนอื่น
4. **ห้ามแต่งเอง ห้ามมโน** — ต้องอ่าน SOP จริงและ MC จริง
5. **ระบุตำแหน่งแก้ไขให้ชัดเจน** — "SOP XX หัวข้อ YY ขั้นตอน ZZ ข้อ N"
6. **ถ้า SOP มี Substitute Control** — รับได้ แต่ต้องระบุให้ชัดเจนว่าอะไรคือการควบคุมทดแทน
7. ภาษา: เป็นทางการ, ไทย, หลีกเลี่ยง "โดยปกติ" และ "อย่างเป็นทางการ"

### Phase 3: Generate HTML
ใช้ template จาก `references/template.html` — แทนที่:
- `{sop_name}` — ชื่อ SOP
- `{sop_file}` — ชื่อไฟล์ SOP ต้นฉบับ
- `{mc_name}` — ชื่อ MC process (และจำนวนขั้นตอน)
- `{gaps}` — array ของ gap objects

## Gap Object Structure

แต่ละ gap มี 5 fields:
```python
{
    'id': '2.1',                    # ลำดับข้อ
    'title': 'ชื่อการควบคุม',        # ชื่อจาก MC
    'mc_ref': 'MC process ขั้นตอน N', # อ้างอิง MC
    'gap': 'คำอธิบายสิ่งที่ขาด',      # 🔴 สิ่งที่ SOP ขาด
    'substitute': 'มี/ไม่มี/บางส่วน',  # 🔄 การควบคุมทดแทน
    'fix_location': 'SOP XX หัวข้อ YY', # 📍 ตำแหน่งแก้ไข
    'fix_how': 'วิธีแก้ไขโดยละเอียด',   # ✏️ วิธีแก้
    'docs': 'เอกสารที่ควรเพิ่ม'         # 📄 เอกสาร
}
```

## HTML Features

| ฟีเจอร์ | รายละเอียด |
|---|---|
| Editable Boxes | `contenteditable="true"` — คลิกพิมพ์แก้ไขได้ทุกกล่อง |
| 💾 Save | บันทึกลง localStorage + Ctrl+S shortcut |
| 📁 Save As… | ดาวน์โหลด HTML ใหม่ทั้งหน้า |
| 📦 Export JSON | ส่งออกข้อมูลทั้งหมดเป็น JSON |
| ➕ Add Page | เพิ่ม slide ใหม่พร้อม 4 กล่องว่าง |
| 📄 Export Text | ส่งออกเป็น plain text |
| Auto-save | แก้ไขแล้วเซฟอัตโนมัติ 3 วินาที |
| Print-ready | `@page { size: 13.333in 7.5in landscape }` |

## Font Sizes (user-tested)

| องค์ประกอบ | ขนาด |
|---|---|
| body | 19px |
| .slide-header .title | 23px |
| .edit-box .box-content | 19px |
| .edit-box .box-label | 15px |
| .cover-slide h1 | 52px |
| .cover-slide .cover-sub | 25px |
| .section-break h2 | 43px |
| .toolbar button | 18px |
| .toolbar .brand | 23px |

## File Naming Convention

`OxygenAI-Draft-SOP-Review-<XX>-<Topic>-v1.html`

ตัวอย่าง:
- `OxygenAI-Draft-SOP-Review-03-FixedAsset-v1.html`
- `OxygenAI-Draft-SOP-Review-07-Procurement-v1.html`

## Substitute Control Classification

ห้ามเขียนว่า "ไม่มี" ทุกกรณี — ต้องแยกเป็น 3 ระดับ:

| ระดับ | ความหมาย | ใช้เมื่อ |
|---|---|---|
| 🔴 **ไม่มี** | ไม่มีการป้องกันความเสี่ยงเลย | ไม่มี SOP ใดในองค์กรที่ครอบคลุมจุดนี้ |
| ⚠️ **มีบางส่วน** | มีการควบคุมบางส่วน แต่ยังต้องเติม | SOP อื่นมีกระบวนการที่เกี่ยวข้องแต่ไม่ได้เชื่อมโยงโดยตรง หรือ SOP นี้มีองค์ประกอบบางส่วนแต่ไม่ครบ |
| ✅ **มี** | มีการควบคุมอื่นที่ชดเชยได้ | กระบวนการใน SOP อื่นสามารถใช้เป็น compensating control ได้อย่างสมบูรณ์ |

**ทุกครั้งที่ใช้ "มีบางส่วน" ต้องระบุ**: SOP ไหน กระบวนการอะไร ที่ให้การควบคุมทดแทน และอะไรที่ยังขาด

ตัวอย่างที่ดี:
```
⚠️ มีบางส่วน — SOP 07 (Procurement) มีกระบวนการขอซื้อ (PR/PO) ที่ต้องผ่านการอนุมัติตาม Approval Matrix 
ซึ่งครอบคลุมการควบคุมการจัดซื้อในระดับหนึ่ง แต่ยังขาด (1) การตรวจสอบเกณฑ์การบันทึกเป็นสินทรัพย์ถาวร 
และ (2) การตรวจสอบ Annual Fixed Asset Budget ก่อนสั่งซื้อ
```

## MC Cross-Coverage Check (Phase 2A)

ก่อนเริ่ม Gap Analysis — ตรวจสอบว่า **MC process ไหนไม่มี SOP ไหนครอบคลุมเลย**:

```python
# Extract all MC processes from omni-data JSON
processes = [p['key'] for p in data['processes']]
# Map SOP → MC coverage
# Find orphan processes (no SOP covers them)
```

Cross-cutting processes ที่มักไม่มี SOP โดยตรง:
- `approval` — อำนาจอนุมัติ (ทุก SOP อ้างถึงแต่ไม่มีใคร define)
- `contracts` — บริหารสัญญา (repository, tracking, bank guarantee, employee contracts)
- `rpt` — รายการเกี่ยวโยงกัน (Related Party Transaction)
- `management` — ประชุมผู้บริหาร (meeting agenda, action log, performance review)
- `pdpa` — PDPA (ถ้าไม่มี SOP แยก)

**วิธีจัดการ**: 
- ลำดับแรก: ตรวจสอบว่า SOP ที่มีอยู่ครอบคลุมบางส่วนหรือไม่ (เช่น SOP 09 มี contract review, SOP 13 O112 มี contract termination → contracts step 6 covered)
- ส่วนที่เหลือ: เพิ่มเป็น gap ใน SOP ที่ใกล้เคียงที่สุด (เช่น Contract Register → SOP 09, Bank Guarantee → SOP 07, Management Meeting → SOP 11)

## v2 Cross-Referencing with Reviewer (D/N Tags)

เมื่อต้องการเทียบผลลัพธ์ของ AI กับของ reviewer:

1. **อ่าน OAI Review Word document** → แปลงด้วย markitdown → parse ทุกข้อของ reviewer แยกตาม SOP
2. **เทียบทีละ gap** — AI gap ไหนตรงกับ reviewer → tag `(D)` = Duplicate, ไม่ตรง → tag `(N)` = New
3. **ข้อของ reviewer ที่ AI ไม่มี** → เพิ่มเป็น gap ปกติติด tag `(N)` (New finding from reviewer)
4. **Save เป็น v2** — ห้าม save ทับ v1

### D/N Tag Placement

Tag ต้อง**ต่อท้ายชื่อ gap** ใน `.slide-header .title`:

```html
<!-- ตัวอย่าง -->
<div class="title">2.1 Gap — Asset Requisition & Budget Check (D)</div>
<div class="title">2.4 Gap — Depreciation Review Process (N)</div>
```

- `(D)` = Duplicate — รายการนี้ตรงกับที่ reviewer ระบุใน OAI Review
- `(N)` = New — รายการนี้เพิ่มโดย KAS Team (reviewer ไม่ได้ระบุ)

### (D)* Tag — Reviewer Items NOT in Master Context

เมื่อ cross-reference กับ OAI Review แล้วพบรายการที่ reviewer ระบุ แต่**ไม่ได้มาจาก Master Context** (เป็นข้อเสนอแนะเพิ่มเติมของ reviewer เอง) ให้ tag เป็น `(D)*`:

```html
<div class="title">2.7 Gap — Employee Exit Clearance Process (D)*</div>
```

- `(D)*` = Duplicate (ตรง OAI Review) + `*` ข้อเสนอแนะเพิ่มเติมที่ไม่อยู่ใน Master Context
- ใช้ `*` เพื่อให้ผู้ใช้สังเกตว่าเป็นข้อเสนอแนะเพิ่มเติม ไม่อิง MC
- MC ref ใน slide ให้ใช้ `📌 OAI Review — <รหัสกิจกรรม>` แทน `📌 Master Context`

### OAI Review Completeness Check (Phase 2B)

เมื่อสร้าง SOP-html เสร็จแล้ว (v1 หรือ v2) — ต้องตรวจสอบว่า**ทุกรายการใน OAI Review ปรากฏใน SOP-html ครบถ้วน**:

1. **อ่าน OAI Review markdown ทั้งหมดอีกครั้ง** — จับทุกรายการแยกตาม SOP (ทั้ง "สิ่งที่อยากให้เพิ่ม", "การควบคุมภายใน", "เอกสารที่เกี่ยวข้อง", "คำถามเพิ่มเติม")
2. **เทียบกับ SOP-html** — ตรวจสอบว่า gap แต่ละข้อใน html ตรงกับ reviewer finding หรือไม่
3. **รายการที่ reviewer มี แต่ SOP-html ไม่มี**:
   - อ่าน SOP จริงก่อน — ตรวจสอบว่า SOP มีเนื้อหานั้นหรือไม่
   - ถ้า SOP มีแล้ว → ไม่ต้องเพิ่ม (reviewer อาจพลาด)
   - ถ้า SOP ไม่มี หรือมีบางส่วน → สร้าง gap ใหม่ ติด tag `(D)*`
### Legend

เพิ่ม legend ใน section-break หน้าแรก:
```html
<p style="margin-top:12px;font-size:17px">(D) = Duplicate — ตรงกับ OAI Review &nbsp;&nbsp; (N) = New — KAS Team เพิ่ม &nbsp;&nbsp; (D)* = OAI Review เพิ่มเติม (ไม่อิง MC)</p>
```

## Language Quality — Formal Thai Style (Gold Standard)

### Fix Section Format

วิธีแก้ไขต้องใช้รูปแบบ `📂 ตำแหน่ง` + `✏️ วิธีแก้ไข` แบบ SOP 03 (gold standard):

```
📂 ตำแหน่ง: SOP XX หัวข้อ "กระบวนการย่อย: YYY" — เพิ่มกระบวนการใหม่ก่อน/หลัง ZZZ

✏️ วิธีแก้ไข: เพิ่มหัวข้อ "..." โดยมีเนื้อหาดังนี้

"ข้อความที่ควรเพิ่มใน SOP ระบุรายละเอียดเป็นประโยคเต็มภาษาไทยอย่างเป็นทางการ..."

ขั้นตอนการดำเนินงาน:
(1) ...
(2) ...
```

**กฎเหล็กด้านภาษา**:
- ใช้ประโยคเต็ม มีประธาน-กริยา-กรรม
- ใช้คำเชื่อม: "ทั้งนี้" "ในกรณีที่" "โดยมีเนื้อหาดังนี้" "นอกจากนี้"
- เขียนขั้นตอนเป็นลำดับเลข (1) (2) (3) พร้อมคำอธิบายแต่ละขั้นตอน
- ห้ามใช้ bullet แบบสั้น ("- หัวข้อ" โดยไม่มีคำอธิบาย)
- ห้ามใช้ลูกศร → — ใช้ "จากนั้น" หรือ "จึง" หรือเขียนเป็นประโยค
- ข้อความใน quotation ("...") ต้องเขียนเสมือนเป็นเนื้อหาที่จะนำไปใส่ใน SOP จริง
- แต่ละขั้นตอนควรมีความยาวอย่างน้อย 1-2 บรรทัด

### Gap Box Language

ช่อง Gap (สิ่งที่ขาดหายไป) ต้อง:
- ระบุให้ชัดเจนว่า SOP มีอะไร (สิ่งที่กล่าวถึง) และไม่มีอะไร (สิ่งที่ขาด)
- อ้างอิงถึงข้อกำหนดใน Master Context ว่า MC กำหนดไว้ว่าอย่างไร
- อธิบายผลกระทบหรือความเสี่ยงที่เกิดจากการขาดการควบคุมนี้
- ความยาว: 3-5 ประโยค

ช่อง Substitute Control ต้อง:
- ระบุระดับ: "ไม่มี", "มีบางส่วน", หรือ "มี"
- ถ้า "มีบางส่วน": ระบุ SOP อื่นที่ให้การควบคุมทดแทน และอะไรที่ยังขาด
- เขียนเป็นประโยคเต็ม ไม่ใช้ bullet

## Delete Page Feature

ทุกไฟล์ต้องมีปุ่ม 🗑️ Delete พร้อม modal confirm:

```html
<button onclick="deletePage()" style="background:#dc2626;border-color:#dc2626;">🗑️ Delete</button>
```

Modal แสดงชื่อหน้าและ ID ก่อนลบ — ปุ่ม ❌ ยกเลิก / 🗑️ ยืนยันการลบ
ลบเฉพาะหน้าที่เพิ่มด้วย ➕ Add Page (id ขึ้นต้นด้วย `slide-new-`)

## Batch Generation Rules

1. **ห้ามใช้ delegate_task** สำหรับสร้าง HTML — delegate ค้างเงียบ (silent timeout) เมื่อ prompt ใหญ่
2. **ห้ามใช้ execute_code + Thai strings** — Unicode escaping (`\uXXXX`) ทำให้ SyntaxError
3. **ใช้ write_file โดยตรง** สำหรับ HTML ที่มีภาษาไทย — ไฟล์ละ 1 ครั้ง แต่เรียกหลาย write_file ในเทิร์นเดียวได้
4. **Template Extraction**: ใช้ไฟล์ gold standard (SOP 03) สกัด `before` (CSS+JS+Toolbar+Cover) และ `after` (slide-end ถึง </html>) แล้วสร้าง gap slides ใหม่ — แทนที่ section header + gaps + end slide
5. **ห้ามย่อภาษาเพื่อประหยัด token** — ถ้าข้อมูลเยอะเกิน ให้ลดจำนวนไฟล์ต่อ batch อย่าลดคุณภาพภาษา

## Pitfalls

1. **❌ CRITICAL: อย่าวิเคราะห์ gap โดยไม่อ่าน SOP** — การเดา gap จาก MC อย่างเดียวทำให้ output ใช้ไม่ได้ 100% (จริง: Oxygen AI SOP 13 flag 4 gaps แต่อ่านจริงพบ SOP มี O101-O112 ครบ → 0 gaps → regenerate 3 รอบ)
2. **❌ CRITICAL: markdown อาจเพี้ยน** — ก่อนวิเคราะห์ให้ spot-check markdown เทียบต้นฉบับ อย่างน้อย 1 กระบวนการต่อ SOP (ตัวอย่าง: check ว่า O101 ใน .md ตรงกับ .docx ไหม)
3. **❌ ลืม MC cross-coverage** — 13 MC processes แต่บางตัว (approval, contracts, rpt, management) ไม่มี SOP ครอบคลุม → ต้องตรวจจับและเพิ่มเป็น gap ใน SOP ที่ใกล้เคียง
4. **❌ ลืม OAI Review completeness** — หลังจากสร้าง SOP-html ต้อง cross-check ว่าทุกรายการใน OAI Review ปรากฏใน html ครบ → รายการนอก MC ให้ tag (D)*
5. **อย่าใช้ MC เป็นตัวตั้ง** — SOP ต้องอยู่ซ้าย MC อยู่ขวา
6. **อย่าใส่ comparison กับ reviewer ใน v1** — output นี้คือของเราเอง (v2/v3 ค่อย cross-reference)
7. **ถ้า SOP ครบ = 0 gaps = PASS** — อย่าฝืนหา gap ให้เจอ (บทเรียน: SOP 11+13 PASS จริง)
8. **อย่าลืม `slide-end` id** — Add Page ใช้เป็น anchor ในการแทรก
9. **CSS ต้องมี `@page`** — เพื่อ print landscape เป็น PPTX ได้
10. **Substitute Control ต้อง nuanced** — ไม่ใช่ทุกอย่างเป็น "ไม่มี" ต้องแยก 🔴/⚠️/✅
11. **write_file หลายไฟล์ในเทิร์นเดียว** — อย่าเรียกทีละไฟล์ต่อเทิร์น (user จะเห็นว่าหยุดทำงาน)
12. **ภาษาไทยห้ามย่อเด็ดขาด** — user จะจับได้ทันทีและให้แก้ใหม่ทั้งหมด
13. **การควบคุมทดแทน = ข้อความล้วน** — ห้ามใช้ emoji (🔄 ⚠️) ใน label
14. **ห้ามใช้ → (ลูกศร) ใน content** — ใช้ "จากนั้น" หรือเขียนเป็นประโยคเต็มแทน
15. **Batch Generation: ห้ามใช้ delegate_task** — delegate ค้างเงียบเมื่อ prompt ใหญ่
16. **D/N tags ต่อท้ายชื่อ gap** — เช่น `2.1 Gap — Name (D)` หรือ `2.1 Gap — Name (N)`
17. **ภาษา fix section ต้อง formal** — ใช้ `📂 ตำแหน่ง` + `✏️ วิธีแก้ไข` + ข้อความใน quotation + ขั้นตอนเลข (1)(2)(3)

## Verification Checklist

- [ ] **✅ อ่าน SOP markdown ทุกฉบับครบหรือยัง?** (สำคัญที่สุด — ถ้าไม่อ่าน = มั่ว — บทเรียน: Oxygen AI สร้าง gap ปลอม ~30 รายการเพราะข้ามขั้นตอนนี้)
- [ ] **✅ spot-check markdown กับต้นฉบับ** — อย่างน้อย 1 กระบวนการต่อ SOP เพื่อยืนยัน conversion ถูกต้อง
- [ ] **✅ MC Cross-Coverage** — ตรวจสอบว่า MC process ทุกตัวมี SOP ครอบคลุมหรือไม่ (approval, contracts, rpt, management มักไม่มี SOP โดยตรง → เพิ่มเป็น gap ใน SOP ที่ใกล้เคียง)
- [ ] **✅ OAI Review Completeness** — ทุกรายการใน OAI Review ต้องปรากฏใน SOP-html (ถ้าไม่มีใน MC → tag (D)*)
- [ ] **✅ ถ้า SOP ครบ = 0 gaps = PASS** — อย่าฝืนหา
- [ ] ทุก gap มี 4 sections: Gap, การควบคุมทดแทน, Fix Location+How, Documents
- [ ] วิธีแก้ไขใช้รูปแบบ `📂 ตำแหน่ง` + `✏️ วิธีแก้ไข` — ภาษาเต็มประโยค
- [ ] ตำแหน่งแก้ไขระบุถึงระดับหัวข้อ/ขั้นตอน/ข้อใน SOP
- [ ] ปุ่ม ➕ Add Page ทำงาน — สร้างหน้าเปล่าพร้อมกล่องว่าง
- [ ] Print preview: landscape 16:9, ไม่มี toolbar
- [ ] ทุกกล่องคลิกแก้ไขได้, Ctrl+S ทำงาน, Export JSON/Text ได้ข้อมูลครบ
- [ ] ไม่มี emoji (🔄⚠️) ใน label "การควบคุมทดแทน"
- [ ] ไม่มีลูกศร (→) ในเนื้อหา — ใช้ "จากนั้น" หรือประโยคเต็ม
- [ ] D/N/(D)* tags ต่อท้ายชื่อ gap — เช่น `2.1 Gap — Name (D)` หรือ `2.7 Gap — Name (D)*`
- [ ] Legend "(D) = Duplicate (N) = New (D)* = OAI Review เพิ่มเติม" ในหน้า section break
