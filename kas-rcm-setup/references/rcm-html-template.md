# RCM HTML Template — Pattern Reference

เทมเพลตอ้างอิงสำหรับสร้าง HTML RCM Matrix — ใช้ pattern ที่ผ่านการทดสอบกับ SICT แล้ว

## Data Extraction Rules (CRITICAL)

🔴 **Tests และ Questions อยู่ที่ CONTROL level** — ห้ามดึงจาก risk level:

```python
# ❌ WRONG — risk.get("tests") และ risk.get("questions") ได้ [] เสมอ
for risk in activity["risks"]:
    test = risk.get("tests")        # [] — EMPTY!
    q = risk.get("questions")       # [] — EMPTY!

# ✅ CORRECT — ดึงจากแต่ละ control
for risk in activity["risks"]:
    for ctrl in risk["controls"]:
        test_names = [t["test_name"] for t in ctrl.get("tests", [])]  # 2 tests
        test_text = "\n\n".join(test_names)
        q_text = ctrl.get("question_text", "")  # 1 question
        nature = ctrl.get("control_nature", "")
```

**1 row = 1 control** (ไม่ใช่ 1 test)

ดูโครงสร้างเต็มใน `references/database-schema.md`

## Key CSS Patterns

### 1. Sticky Header + Scrollable Container
```
.scroll-outer { width: 100%; max-width: 100vw; overflow: auto; height: calc(100vh - 185px); }
table.rcm thead th { position: sticky; top: 0; z-index: 10; }
```
**กฎ:** `overflow` ต้องอยู่บน parent — ห้ามอยู่บน element เดียวกับ `position: sticky`

### 2. Fixed Table Width + Horizontal Scrollbar
```
table.rcm { table-layout: fixed; min-width: 1400px; width: 1400px; }
table.rcm th:nth-child(1), table.rcm td:nth-child(1) { width: 100px; }
table.rcm th:nth-child(2), table.rcm td:nth-child(2) { width: 200px; }
/* ... รวมทุกคอลัมน์ต้อง = min-width */
```
**กฎ:** `min-width` ต้องเกิน viewport → scrollbar โผล่. ใช้ `nth-child` กำหนด width ทั้ง `th` และ `td`

### 3. Styled Scrollbar
```
.scroll-outer::-webkit-scrollbar { width: 10px; height: 10px; }
.scroll-outer::-webkit-scrollbar-track { background: #f0f0f0; }
.scroll-outer::-webkit-scrollbar-thumb { background: #bdbdbd; border-radius: 5px; }
.scroll-outer::-webkit-scrollbar-thumb:hover { background: #888; }
.scroll-outer::-webkit-scrollbar-corner { background: #f0f0f0; }
```

### 4. Search/Filter Bar
```
<input type="text" id="searchInput" placeholder="🔍 ค้นหา..." oninput="doSearch()">
<select id="searchField" onchange="doSearch()">
  <option value="all">ทุกคอลัมน์</option>
  <option value="proc">กระบวนการ</option>
  ...
</select>
```
JS: `classList.add('hidden')` / `classList.remove('hidden')` ในการซ่อนแถว

### 5. Contenteditable
```
[contenteditable="true"] { border-bottom: 1px dashed #ccc; outline: none; cursor: text; }
[contenteditable="true"]:focus { border-bottom: 2px solid #1a237e; background: #fffde7; }
```

## Default Column Layout (7 columns)
| # | Column | Width | Editable |
|---|--------|-------|----------|
| 1 | กระบวนการ | 100px | ❌ |
| 2 | กิจกรรม | 200px | ✅ |
| 3 | ความเสี่ยง | 220px | ✅ |
| 4 | การควบคุมที่ควรมี | 230px | ✅ |
| 5 | วิธีการตรวจสอบ | 270px | ✅ |
| 6 | คำถามสัมภาษณ์ | 250px | ✅ |
| 7 | ลักษณะควบคุม | 80px | ❌ |

**❌ ห้ามใส่คอลัมน์ Poison เป็น default** — user ไม่ต้องการ

## Print
```css
@media print {
  .toolbar, .summary { display: none; }
  .scroll-outer { overflow: visible; height: auto; border: none; }
  table.rcm thead th { position: static; }
  @page { size: A3 landscape; margin: 8mm; }
}
```

## Header Rules
- ❌ ห้ามใส่ icon/รูปแปลกๆ — ใช้ text + emoji (📋)
- ✅ gradient สีน้ำเงินเข้ม (#1a237e → #283593)
- ✅ แสดง: ชื่อรายงาน + metadata

## Verified With
- SICT (Silicon Craft Technology) — 20 activities, 232 controls, 12 processes
- Browser: Chrome/Edge (WebKit scrollbar styles)
