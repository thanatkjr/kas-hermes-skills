---
name: kas-htmlformat
description: สร้าง HTML ในรูปแบบที่พร้อมแปลงเป็น PowerPoint — โครงสร้าง slide container, split layout, ตาราง, diagram, print landscape
version: 1.0.0
author: Thanat Kerdcharoen
license: MIT
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

## CSS Classes Reference

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
