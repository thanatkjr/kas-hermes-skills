---
name: kas-rcm-v1
description: Generate interactive RCM (Risk Control Matrix) HTML files from RCM data — sticky table headers, activity-picker filter, multi-select delete, insert-row, undo/redo, UNVS-first sorting, and control-level dropdown with color coding. Use when building an editable RCM worksheet for internal-audit fieldwork that team members fill in on their own laptops.
version: 1.0.0
---

# RCM HTML Generator

สร้างไฟล์ **RCM (Risk Control Matrix)** แบบ interactive HTML ที่ทีมตรวจสอบภายในใช้กรอกข้อมูลภาคสนามได้ — มี sticky header, filter กิจกรรม, ลบ/เพิ่มแถว, undo/redo, เรียง UNVS ก่อน, และ dropdown ระดับการควบคุม

ไฟล์ output เป็น **HTML เดียว (self-contained)** ไม่ต้องติดตั้งอะไร — เปิดใน browser ได้ทุกเครื่อง (Windows/Mac/Linux) แชร์ให้ทีมผ่าน OneDrive/Drive/LINE ได้ทันที

## Prerequisites (ทำครั้งเดียว)

1. **Python 3.8+** — ใช้รัน generator script (ทุก OS มี)
2. **ข้อมูล RCM** — ดึงจาก MCP `rcm` (Cloudflare) ผ่าน `mcp_rcm_get_process_rcm` แล้ว normalize เป็น JSON ตาม schema ด้านล่าง
   - ดู skill `rcm-knowledge` สำหรับวิธี setup MCP และ `kas-rcm-setup` สำหรับ MCP Server

> ⚠️ **ห้าม hardcode path ของเครื่องตัวเอง** — skill นี้ใช้ `pathlib` + relative path เท่านั้น ทุกคนในทีมใช้ได้เหมือนกันไม่ว่าจะใช้ Windows/Mac/Linux

## Field Mapping (ข้อมูล → คอลัมน์)

RCM HTML มี 13 คอลัมน์ (10 ข้อมูล + 3 ให้กรอก):

| Col | หัวคอลัมน์ | มาจาก field | หมายเหตุ |
|-----|-----------|-------------|---------|
| 0 | # | (auto) | เลขลำดับ |
| 1 | กิจกรรม | activity_code + activity_name | merge ด้วย rowspan ต่อ 1 กิจกรรม |
| 2 | ความเสี่ยง | risk_name | |
| 3 | การควบคุมที่ควรมี | control_name | |
| 4 | Policy | policies[] (หลายรายการ join `\n`) | |
| 5 | Procedure | procedures[] (หลายรายการ join `\n`) | |
| 6 | KRI | indicator_name | |
| 7 | วิธีการตรวจสอบ | tests[] (หลายรายการ join `\n`) | |
| 8 | Report | report_name | |
| 9 | คำถามสัมภาษณ์ | question_text | |
| 10 | การควบคุมที่มีอยู่จริง | — (ว่าง) | `contenteditable` ให้กรอก |
| 11 | ระดับการควบคุมภายใน | — (ว่าง) | `<select>` 4 ระดับ + สี |
| 12 | หน่วยงานที่รับผิดชอบ | — (ว่าง) | `contenteditable` ให้กรอก |

### ระดับการควบคุมภายใน (col 11)

| ค่า | สีพื้น | คำอธิบาย |
|-----|--------|---------|
| Ad-hoc | 🔴 `#ffcdd2` | ไม่มีมาตรฐาน กำหนดเป็นครั้งคราว |
| Developing | 🟡 `#fff9c4` | มีกระบวนการแต่ไม่สม่ำเสมอ |
| Standard | 🟢 `#c8e6c9` | มีมาตรฐาน มีวัด/ประเมิน/ปรับปรุง |
| Leading | 🔵 `#bbdefb` | มาตรฐานสากล/ผู้นำอุตสาหกรรม |

## Input JSON Schema (normalized)

```json
{
  "client_name": "Silicon Craft Technology (SICT)",
  "db_version": "DB v2",
  "processes": [
    {
      "code": "R",
      "label": "P1 รายได้",
      "activities": [
        {
          "code": "R-ELEC-001",
          "name": "การขายตาม Forecast/Contract OEM และการคิดราคาตาม BOM",
          "rows": [
            {
              "risk": "ข้อความความเสี่ยง",
              "control": "ข้อความการควบคุม",
              "policy": ["บรรทัดที่ 1", "บรรทัดที่ 2"],
              "procedure": ["ขั้นตอนที่ 1", "ขั้นตอนที่ 2"],
              "kri": "ตัวชี้วัดความเสี่ยง",
              "test": ["วิธีการตรวจ 1", "วิธีการตรวจ 2"],
              "report": "ชื่อรายงาน",
              "question": "คำถามสัมภาษณ์"
            }
          ]
        }
      ]
    }
  ]
}
```

ดูตัวอย่างเต็ม: `templates/sample_input.json`

## Workflow

### Step 1 — เตรียมข้อมูล

1. เรียก `mcp_rcm_get_process_rcm(process_code="R", sector_code="ELEC")` ทีละ process
2. Normalize เป็น JSON schema ด้านบน (เขียน `execute_code` หรือสคริปต์ตัวช่วย)
3. บันทึกเป็น `rcm_data.json`

### Step 2 — Generate HTML

```bash
python scripts/generate_rcm.py rcm_data.json -o RCM_<client>_<date>.html
```

ตัวเลือก:
- `-o/--output` — ชื่อไฟล์ output (default: `RCM_{client}_{date}.html`)
- ไม่มี option อื่น — เรียบง่าย

### Step 3 — แจกทีม

- เปิดไฟล์ใน browser → กด **💾 บันทึก** เพื่อ save กลับ (เก็บทุกการแก้ไข)
- แชร์ผ่านช่องทางที่ทีมใช้ (OneDrive, Drive, LINE, Email)

## HTML Features Reference

| ปุ่ม/ฟีเจอร์ | การทำงาน |
|-------------|---------|
| 💾 บันทึก | save HTML กลับเป็นไฟล์ใหม่ (รวมทุกการแก้ไข) |
| 🖨️ PDF | พิมพ์/export PDF (A3 landscape) |
| 📖 ทั้งหมด / 📕 เดี่ยว | expand/collapse ทุก process |
| ⚙️ | toggle คอลัมน์ (ซ่อน/แสดง) |
| 📋 กิจกรรม | popup เลือกกิจกรรม — filter แสดงเฉพาะที่เลือก |
| 🔍 ค้นหา | search ทั่วตาราง |
| ☑️ | select mode — คลิกเลือกหลายแถว |
| 🗑️ | ลบแถวที่เลือก (มี confirm modal) |
| ➕ | เพิ่มแถว (inherit กิจกรรมเดิม, คลิกแถวเพื่อเลือกตำแหน่ง) |
| ↩️ / ↪️ | undo / redo (Ctrl+Z / Ctrl+Y) |
| 🔤 | เรียงกิจกรรม UNVS ขึ้นก่อน |
| Ctrl+F | focus ช่องค้นหา |

- **Sticky header**: header คอลัมน์ติดด้านบนตอน scroll (สำคัญ — อย่าใส่ `overflow: hidden` ที่ `.process-panel` เด็ดขาด)
- **UNVS-first**: กิจกรรมที่มี `-UNVS-` ใน code ขึ้นก่อนกิจกรรม sector เสมอ

## Customization

- **เปลี่ยนชื่อคอลัมน์**: แก้ `COL_NAMES` ใน template (array 13 ตัว)
- **เพิ่ม/ลดระดับการควบคุม**: แก้ `<option>` ใน `<select class="control-level">` + ฟังก์ชัน `updateControlLevel`
- **เปลี่ยนสี theme**: แก้ CSS `--` variables หรือตรง `.app-header` / `thead th`
- **เพิ่มคอลัมน์**: ดู `templates/rcm_template.html` comment `<!-- ADD COLUMN -->`

## Common Pitfalls

1. **Sticky header ไม่ติด** — ห้ามใส่ `overflow: hidden` ที่ `.process-panel` (ตัว parent ของ `.scroll-outer`) เพราะมันสร้าง containing block ใหม่ทำลาย `position: sticky`
2. **Toolbar ขึ้น 2 แถว** — ต้อง `flex-wrap: nowrap` + ลด padding/font และใช้ `flex-shrink: 0` ที่ปุ่ม
3. **ชื่อกิจกรรมเหลือแค่ code** — `data-act` เก็บแค่ code ต้องดึงชื่อเต็มจาก `td[data-col="1"]` (หรือ activity name) แยกต่างหาก
4. **Undo ไม่ทำงานหลัง insert** — ต้องเก็บ reference ของ DOM node (ไม่ใช่ outerHTML) สำหรับ insert/delete อย่างถูกต้อง
5. **ภาษาไทยใน execute_code** — ถ้าใช้ Python เขียน HTML โดยตรง ระวัง unicode escape ใช้ `write_file` หรือ template + `.replace()` ดีกว่า
6. **hardcode path เครื่องตัวเอง** — ห้ามใช้ `C:\Users\xxx` ใน script; ใช้ `pathlib` + relative path เท่านั้น

## Related Skills

- `rcm-knowledge` — ดึงข้อมูล RCM จาก MCP (query activity/risk/control)
- `kas-rcm-setup` — setup RCM MCP Server
- `kas-htmlformat` — โครงสร้าง HTML ที่พร้อมแปลงเป็น PowerPoint (แนวทาง layout)
