---
name: kas-htmlformat
description: สร้าง HTML ในรูปแบบที่พร้อมแปลงเป็น PowerPoint — โครงสร้าง slide container, split layout, ตาราง, diagram, print landscape
license: MIT
author: Thanat Kerdcharoen
version: 1.1.0
---

# KAS HTMLFORMAT

สร้าง HTML ไฟล์ที่มีโครงสร้างเสมือนสไลด์ PowerPoint — พร้อมนำไปแปลงเป็น .pptx โดย KAS HTML Converter
หรือ Print เป็น PDF landscape ได้ทันที

## Workflow (4 Steps)

### Step 1 — ถามอัตราส่วน
ถาม user: "PPT จะใช้อัตราส่วนไหน?"
- **16:9** (default) → width 13.333" height 7.5"
- **4:3** → width 10" height 7.5"

### Step 2 — Overall Design
ถาม user ทีละข้อ (ยืนยันทีละข้อ):
1. **Header**: ข้อความด้านบน — "ใส่ Header อะไร? (เว้นว่าง = ไม่มี)"
2. **Footer**: ข้อความด้านล่าง — "ใส่ Footer อะไร?"
3. **เลขหน้า**: "ใส่เลขหน้ามุมขวาล่างหรือไม่? (yes/no)"
4. **ฟอนต์**: "ใช้ฟอนต์อะไร? (default: Sarabun สำหรับไทย, JasmineUPC ตกแต่ง)"

### Step 2.5 — ถามว่า user มีเนื้อหาไหม (สำคัญที่สุด)
**ก่อนสร้าง preview ใดๆ** ต้องถามก่อนว่า:

> "คุณมีเนื้อหาที่ต้องการใส่ในสไลด์แล้วหรือไม่?"

- **ถ้ามี** → ให้ user ส่งเนื้อหามา (text, bullet, ตาราง, diagram) → ห้ามแต่งเองเด็ดขาด
- **ถ้ายังไม่มี** → ช่วยออกแบบโครงสร้างเนื้อหา (ถามทีละส่วน) → user ยืนยันก่อนไปต่อ

### Step 3 — Preview (ถาม user ก่อนว่าจะดูแบบไหน)
ก่อนแสดง preview ต้องถามก่อนว่า:

> "ต้องการดู preview แบบไหน?"
> 1. 📝 **โครงสร้างเนื้อหาแบบ Bullet** — แสดงเป็นข้อความ อ่านเร็ว
> 2. 🌐 **Preview HTML ใน Browser** — เห็น layout จริง สี ตาราง diagram เหมือนสไลด์

- **ถ้าเลือก Bullet** → แสดง preview แบบข้อความเรียบง่าย:

```
📋 แผนสไลด์ — "สรุปผลการตรวจระบบจัดซื้อ" (8 หน้า)

SLIDE 1 | COVER
  สรุปผลการตรวจระบบจัดซื้อ
  บริษัท จ๊กก๊ก จำกัด

SLIDE 2 | SPLIT
  🔹 ซ้าย: วัตถุประสงค์
    • ประเมินความเพียงพอของระบบควบคุมภายใน
    • ตรวจสอบการปฏิบัติตามนโยบาย
  🔹 ขวา: ขอบเขต
    • วงจรจัดซื้อทั้งกระบวนการ
    • ระยะเวลา ม.ค.-มิ.ย. 2569

SLIDE 3 | TABLE
  ตารางสรุปผลประเมิน 4 ด้าน
  คอลัมน์: ด้าน | ระดับควบคุม | ระดับปฏิบัติ | รวม

SLIDE 4 | SPLIT
  🔹 ซ้าย: ข้อตรวจพบ Vendor
  🔹 ขวา: ความเสี่ยง + ข้อเสนอแนะ

...
```

**กฎ preview:**
- แต่ละ slide = 1 บรรทัดหัวข้อ + เนื้อหาย่อ 2-5 บรรทัด
- ไม่ต้องวาดกรอบ ASCII — ใช้ย่อหน้า + emoji
- ถ้า slide มี 20+ หน้า → แสดงแค่ 5 หน้าแรก + "..." + หน้าสุดท้าย
- user สามารถคลิกดูรายละเอียดแต่ละ slide ได้

### Step 4 — Generate HTML
สร้าง HTML ไฟล์ที่มีโครงสร้างตามนี้:

```html
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<style>
  @page { size: [W] [H] landscape; margin: 0; }
  body { font-family: '[FONT]', sans-serif; }
  .slide-container {
    width: [W]; height: [H];
    margin: 0 auto 20px;
    page-break-after: always;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  .slide-header { /* แถบสี */ }
  .slide-footer { /* เลขหน้า */ }
  .split { display: flex; }
  .pbox { flex: 1; padding: 20px; }
  .dbox { /* diagram box */ }
</style>
</head>
<body>
  <!-- แต่ละ slide = 1 .slide-container -->
</body>
</html>
```

## โครงสร้าง HTML ที่ใช้

### Slide Container
```html
<div class="slide-container">
  <div class="slide-header">หัวข้อ</div>
  <div class="slide-body">
    <!-- content here -->
  </div>
  <div class="slide-footer">หน้า 1/10</div>
</div>
```

### Split Layout (2-3 คอลัมน์)
```html
<div class="split">
  <div class="pbox left-bg">
    <h2>คอลัมน์ซ้าย</h2>
    <ul><li>bullet</li></ul>
  </div>
  <div class="pbox right-bg">
    <h2>คอลัมน์ขวา</h2>
    <p>เนื้อหา</p>
  </div>
</div>
```

### Table
```html
<table class="data-table">
  <thead><tr><th>หัวข้อ</th><th>รายละเอียด</th></tr></thead>
  <tbody><tr><td>...</td><td>...</td></tr></tbody>
</table>
```

### Diagram (กล่อง + ลูกศร)
```html
<div class="diagram-row">
  <div class="dbox"><strong>1</strong><p>ขั้นตอนที่ 1</p></div>
  <div class="dbox"><strong>2</strong><p>ขั้นตอนที่ 2</p></div>
  <div class="dbox"><strong>3</strong><p>ขั้นตอนที่ 3</p></div>
</div>
```
ใช้แต่ **สี่เหลี่ยม** เท่านั้น — ไม่ใช้วงกลม วงรี หรือรูปทรงแปลก

### Section Break (หน้าคั่น)
```html
<div class="slide-container section-break">
  <h1>ส่วนที่ 2</h1>
  <p>หัวข้อใหม่</p>
</div>
```

## Related Skills

- **kas-sop-review-html**: SOP Review HTML template with editable boxes, toolbar (Save/Export/Add Page/Delete Page), gap analysis format (Gap → Substitute → Fix → Docs). Use when building SOP review documents instead of generic presentations.
- **Substitute Control Classification**: ดู `references/substitute-control-classification.md` สำหรับ framework การจำแนกการควบคุมทดแทน (🔴 ไม่มี / ⚠️ มีบางส่วน / ✅ มี) พร้อม cross-SOP references
- **SOP Review D/N Tagging**: ดู `references/sop-review-dn-tagging.md` สำหรับระบบแท็ก (D)=Duplicate/(N)=New และการ cross-reference กับ OAI Review

## Templates

| Template | ใช้เมื่อ |
|----------|--------|
| `templates/sop-review-template.html` | สร้าง SOP Gap Analysis — โครงสร้างครบ: cover, gap slides พร้อม 4 edit-boxes, toolbar (Save/Save As/Export JSON/Add Page/Delete/Export Text), modal confirm delete, auto-save, Ctrl+S |

## References

| Reference | ใช้เมื่อ |
|-----------|--------|
| `references/css-bar-charts.md` | สร้าง Financial Dashboard ด้วย Pure CSS Bar Charts — หลีกเลี่ยง Chart.js (มีปัญหา rendering บน file://) ใช้ Horizontal/Stacked/Comparison bars แทน |
| `references/business-model-canvas-grid.md` | สร้าง Business Model Canvas 1 หน้า — CSS Grid 5 คอลัมน์ พร้อม highlight boxes และ color coding |

## กฎเหล็ก

| # | กฎ |
|---|-----|
| 0 | **ห้ามแต่งเนื้อหาเอง** — ต้องถาม user ก่อนว่ามีเนื้อหาไหม ถ้ามีให้ user ส่งมา |
| 1 | **ห้ามใช้รูปทรงแปลก** — เฉพาะสี่เหลี่ยม (`border-radius` ≤ 8px) |
| 2 | **ห้าม tab/sub-sheet** — ตารางใช้ `<table>` ธรรมดา |
| 3 | **เลขหน้าต้องตรง** — `หน้า X/ทั้งหมด` |
| 4 | **ทุก slide ต้องมี .slide-container** — parser ใช้ class นี้หา slide |
| 5 | **แสดง preview ก่อนสร้าง HTML เสมอ** — user ต้องกดยืนยัน |
| 6 | **Print landscape ได้** — `@page { size: landscape }` |
| 7 | **สีต้อง contrast พอ** — พื้นอ่อน ตัวหนังสือเข้ม |
| 8 | **1 slide-container = 1 slide ใน PPTX** |
| 9 | **ห้ามย่อภาษาไทย** — เมื่อ batch-generate หลายไฟล์ ห้ามย่อข้อความให้สั้นลงเพื่อประหยัด token หรือเวลา ภาษาไทยต้องเป็นประโยคเต็ม อ่านรู้เรื่อง มีรายละเอียดเพียงพอ ถ้าต้องการประหยัดพื้นที่ให้ลดจำนวนไฟล์ต่อ batch ไม่ใช่ลดคุณภาพภาษา |
| 10 | **ใช้ write_file สำหรับ HTML ที่มีภาษาไทย** — execute_code มักพังกับ Unicode และ Thai string escaping (`\\uXXXX`) delegate_task ค้างเมื่อ prompt ใหญ่เกิน ให้สร้าง HTML เต็มด้วย write_file โดยตรง ไฟล์ละ 1 ครั้ง |
| 11 | **ห้ามใช้ emoji ใน content labels** — label ของกล่องเนื้อหาต้องเป็นข้อความล้วน เช่น `การควบคุมทดแทน` ห้ามใช้ `🔄 การควบคุมทดแทน`, `⚠️ มีบางส่วน` ใน label (emoji ใน toolbar/badge เช่น 🔴 Gap ใช้ได้) |
| 12 | **Gap title format**: เลข + "Gap — " + ชื่อสั้นภาษาอังกฤษ + " (D)" หรือ " (N)" — เช่น `2.1 Gap — Asset Requisition & Budget Check (D)` — (D)=Duplicate (ซ้ำกับ OAI Review), (N)=New (KAS Team เพิ่ม) |

## Pitfalls

| Pitfall | Solution |
|---------|----------|
| execute_code + Thai strings → SyntaxError จาก Unicode escaping | ใช้ `write_file` เขียน HTML ที่มีภาษาไทยโดยตรง |
| delegate_task สำหรับสร้าง HTML → ค้างเงียบ (silent timeout) | delegate ไม่เหมาะกับ task ที่ต้องสร้างไฟล์ขนาดใหญ่และมีหลายขั้นตอน — ใช้ `write_file` ทีละไฟล์แทน |
| Batch-generate แล้วภาษาหด → user ต้องแก้ซ้ำ | กฎข้อ 9: ลดจำนวนไฟล์ต่อ batch อย่าลดคุณภาพภาษา |
| regenerate ทั้ง 12 ไฟล์เพราะ template bug → แก้ template ครั้งเดียวแล้ว reuse | ใช้เทคนิค Template Extraction (ดูด้านล่าง) |
| Chart.js CDN แสดงผลไม่ได้บน file:// protocol (canvas มีขนาด 0) | ใช้ Pure CSS bar charts แทน — `div` + `style="width:X%"` — ดู `references/css-bar-charts.md` |
| Layout ซับซ้อนเกิน (split panel) → user ปฏิเสธ | ยึด layout เดิม เพิ่มฟีเจอร์ผ่าน modal/popup — user ชอบเรียบง่าย |
| **🔴 Chart.js ไม่ render บน `file://` protocol** — canvas dimensions คำนวณผิด, bars ถูกบีบอัดเหลือแค่ขอบซ้าย, CDN script อาจไม่โหลด | ❌ อย่าใช้ Chart.js สำหรับไฟล์ที่เปิดจาก `file://` — ใช้ **Pure CSS Bar Charts** แทน (ดู `references/css-bar-charts.md`) — render ทันที, print ได้, ไม่ต้องพึ่ง CDN |
| **🔴 `height: 98vh` + `overflow: hidden` ทำให้เนื้อหาถูกตัด** — กล่องที่เนื้อหาเยอะ (เช่น Business Model Canvas, Dashboard cards) จะถูก clip ไม่แสดงผลด้านล่าง | ❌ อย่าใช้ `height: 98vh` (หรือ fixed height ใด ๆ) บน grid/flex container ที่มีเนื้อหาผันแปร — ใช้ `auto` height ให้เนื้อหาไหลตามธรรมชาติ และลบ `overflow: hidden` ออก |
| **🔴 Sidebar layout ซับซ้อน → user ปฏิเสธ** — user ชอบความเรียบง่าย เมื่อต้องการ filter ข้อมูลในตาราง (เช่น RCM) ให้ใช้ **Modal Popup** แทน Sidebar ถาวร — popup เปิด-ปิดได้ ไม่เปลืองพื้นที่หน้าจอ | ✅ ใช้ Modal (`position: fixed`) พร้อม checkbox list + search filter + ปุ่ม Apply/Cancel — อย่า redesign layout หลัก (split panel) เว้นแต่ user ขอเอง |

## Chart Alternatives

เมื่อ Chart.js ไม่ทำงาน (file:// protocol) → ใช้ Pure CSS bar charts — ดู `references/css-bar-charts.md` สำหรับ stacked bars, horizontal bars, comparison bars

## Template Extraction Pattern

เมื่อต้องสร้าง HTML หลายไฟล์ที่มีโครงสร้างเหมือนกันแต่เนื้อหาต่างกัน (เช่น SOP Review 13 ฉบับ):

1. กำหนด **Gold Standard** 1 ไฟล์ที่มี CSS/JS/Toolbar สมบูรณ์
2. อ่านไฟล์ต้นแบบ → หาตำแหน่ง section-break header และ slide-end
3. เก็บ `before` (ทุกอย่างก่อน section-break) และ `after` (ตั้งแต่ slide-end)
4. สร้าง gap slides ใหม่ → `before + section_header + gap_slides + after`
5. Replace ชื่อ SOP ทั้งหมดใน before/after ด้วยชื่อใหม่

วิธีนี้ทำให้ทุกไฟล์ใช้ CSS/JS/Toolbar/Modal เดียวกัน — แก้ bug ครั้งเดียวมีผลทุกไฟล์

## CSS Classes Reference


### Interactive Editable Mode

สำหรับเอกสารที่ต้องการให้ผู้รับแก้ไขเนื้อหาได้ — ใช้ `.edit-box` แทน static content ภายใน `.slide-body` ดู `references/interactive-editable-pattern.md` สำหรับรายละเอียด full pattern (editable boxes, save/export toolbar, auto-save, JSON/Text export)

| Class | ใช้กับ | คำอธิบาย |
|-------|--------|---------|
| `.slide-container` | `<div>` | 1 หน้า = 1 slide |
| `.slide-header` | `<div>` | แถบหัวเรื่อง + สีพื้น |
| `.slide-footer` | `<div>` | เลขหน้า + footer text |
| `.split` | `<div>` | flex container แบ่งคอลัมน์ |
| `.pbox` | `<div>` | กล่องเนื้อหา (ใช้ใน split) |
| `.left-bg` | `.pbox` | พื้นหลังเขียวอ่อน (หลักการ) |
| `.right-bg` | `.pbox` | พื้นหลังเทาอ่อน (เอกสาร/นิยาม) |
| `.data-table` | `<table>` | ตารางข้อมูล |
| `.diagram-row` | `<div>` | เรียงกล่องแนวนอน |
| `.dbox` | `<div>` | กล่อง diagram + ลูกศร |
| `.section-break` | `.slide-container` | หน้าคั่นเปลี่ยนตอน |
| `.cover-slide` | `.slide-container` | หน้าปก |
