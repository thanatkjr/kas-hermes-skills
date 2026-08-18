# Interactive Editable HTML Pattern

ส่วนขยายของ kas-htmlformat — ทำให้ slide-container กลายเป็นเอกสารที่แก้ไขได้ พร้อม save/export toolbar

## When to Use

เมื่อต้องการให้ผู้รับไฟล์ HTML สามารถแก้ไขเนื้อหาในกล่องข้อความได้โดยตรง พร้อมบันทึกและส่งออก

## Key Features

- `contenteditable="true"` บน `.box-content` — คลิกเพื่อพิมพ์แก้ไข
- Toolbar sticky ด้านบน — Save / Save As / Export JSON / Export Text
- Auto-save ไปยัง localStorage ทุก 3 วินาทีหลังจากแก้ไข
- Ctrl+S shortcut
- Export JSON — ส่งออกข้อมูลทั้งหมดเป็น JSON (ใช้ regenerate HTML ได้)
- Export Text — ส่งออกเป็น plain text
- Toast notification — แสดงสถานะ save/export

## CSS for Editable Boxes

```css
.edit-box {
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
}
.edit-box .box-label {
  /* label header — gap/sub/action/doc */
  font-size: 11px; font-weight: 800;
  padding: 5px 12px;
}
.edit-box .box-content {
  padding: 8px 12px; min-height: 48px;
  outline: none; white-space: pre-wrap;
}
.edit-box .box-content:focus {
  background: #fffbeb;
  box-shadow: inset 0 0 0 2px #fbbf24;
}
.edit-box .box-content:empty::before {
  content: 'คลิกเพื่อพิมพ์...';
  color: #94a3b8; font-style: italic;
}
```

## Toolbar HTML

```html
<div class="toolbar">
  <button onclick="saveAll()">💾 Save</button>
  <button onclick="saveAs()">📁 Save As…</button>
  <button onclick="exportJSON()">📦 Export JSON</button>
  <button onclick="exportText()">📄 Export Text</button>
</div>
```

## JavaScript Functions

- `collectData()` — รวบรวมข้อมูลจากทุก .edit-box ในทุก .slide-container
- `saveAll()` — บันทึกไปยัง localStorage
- `saveAs()` — download HTML ไฟล์ใหม่
- `exportJSON()` — download JSON
- `exportText()` — download plain text
- Auto-save ทุก 3 วินาทีหลัง input event
- `Ctrl+S` → saveAll()

## Box Label Colors (4 แบบ)

| Class | Background | Text | Use |
|---|---|---|---|
| `.box-label.gap` | #fef2f2 | #b91c1c | สิ่งที่ขาด (Gap) |
| `.box-label.sub` | #fffbeb | #92400e | การควบคุมทดแทน |
| `.box-label.action` | #dbeafe | #1e3a8a | ตำแหน่ง+วิธีแก้ไข |
| `.box-label.doc` | #ecfdf5 | #047857 | เอกสารที่ควรเพิ่ม |

## Integration with kas-htmlformat

- ใช้ `.slide-container` เป็น wrapper ตามปกติ
- `.slide-header` + `.slide-footer` + `.slide-body` เหมือนเดิม
- ภายใน `.slide-body` ใช้ `.edit-box` แทน static content
- `.split > .pbox` ยังใช้ได้ — `.edit-box` อยู่ภายใน `.pbox`
- @page landscape ยังทำงาน — print/PPTX conversion ไม่เสีย
