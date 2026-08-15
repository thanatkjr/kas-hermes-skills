# RCM HTML Template v3 — 8 Columns + Resize + Column Toggle + Expandable Detail

เทมเพลตสำหรับสร้าง RCM HTML แบบ interactive เต็มรูปแบบ — พัฒนาจาก session SICT (2026-08-09)

## Column Layout (8 columns)

| # | Column | Source | Editable | Hideable | Width |
|---|--------|--------|:---:|:---:|------:|
| 0 | # | auto-increment | ❌ | 🔒 | 45px |
| 1 | กิจกรรม | `activity_code: activity_name` merged | ✅ | 🔒 | 200px |
| 2 | ความเสี่ยง + ▶ expand | `risk_name` | ✅ | 🔒 | 280px |
| 3 | การควบคุมที่ควรมี | `control_name` | ✅ | ✅ | 280px |
| 4 | Policy | `risk.policies[]` (joined) | ✅ | ✅ | 280px |
| 5 | Procedure | `risk.procedures[]` (joined) | ✅ | ✅ | 280px |
| 6 | KRI | `risk.indicator_name` | ✅ | ✅ | 250px |
| 7 | วิธีการตรวจสอบ | `control.tests[]` (joined) | ✅ | ✅ | 350px |

### Differences from v2 (9-column)
- ❌ Removed: "ชื่อกิจกรรม" (merged into กิจกรรม as "code: name")
- ❌ Removed: "ประเภทความเสี่ยง" (risk category tags)
- ❌ Removed: "คำถามสัมภาษณ์" (moved to expandable detail)
- ❌ Removed: "ลักษณะควบคุม" (control nature)
- ✅ Added: Policy, Procedure, KRI as main columns
- ✅ Added: Column resize, column toggle

## Key Features

### 1. Column Resize
Drag right edge of any `<th>` header to resize column. Implementation:
```html
<th data-col="N">Column Name<span class="resize-handle" onmousedown="startResize(event,this)"></span></th>
```
```javascript
function startResize(e, handle) {
  resizingTh = handle.parentElement;
  resizingCol = parseInt(resizingTh.getAttribute('data-col'));
  startX = e.pageX;
  startW = resizingTh.offsetWidth;
  document.addEventListener('mousemove', doResize);
  document.addEventListener('mouseup', stopResize);
}
function doResize(e) {
  const newW = Math.max(50, startW + e.pageX - startX);
  resizingTh.style.width = newW + 'px';
  document.querySelectorAll('td[data-col="' + resizingCol + '"]').forEach(td => {
    td.style.width = newW + 'px';
  });
}
```

### 2. Column Toggle
Dropdown menu with checkboxes — columns 0-2 mandatory (locked 🔒), 3-7 toggleable:
```html
<div class="col-toggle-wrap">
  <button class="col-toggle-btn" onclick="toggleColMenu()">⚙️ คอลัมน์ ▾</button>
  <div class="col-toggle-menu" id="colMenu">
    <label class="mandatory"><input type="checkbox" checked disabled> # 🔒</label>
    <!-- ... -->
  </div>
</div>
```
```css
th.col-hidden, td.col-hidden { display: none; }
```

### 3. Expandable Detail Row (per risk)
Click ▶ button next to risk name to show detail row with:
- 🔴 Poison (โลภะ/โทสะ/โมหะ) — color-coded badge
- 📈 Report (รายงานที่เกี่ยวข้อง)
- 📎 Validation (หลักฐานการตรวจสอบ, 2 items)
- ❓ คำถามสัมภาษณ์ (from controls, N items)

Detail row is injected via JS after page load, placed after each risk's last control row:
```javascript
function injectDetailRows() {
  // Group rows by data-risk-code
  // Insert <tr class="detail-row"> after last row of each risk group
}
```

### 4. Sheet Tabs
9 process tabs with row count badges — sticky below toolbar:
```html
<div class="sheet-tabs">
  <div class="sheet-tab active" onclick="switchProcess('R')" data-proc="R">
    P1 รายได้ <span class="badge">373</span>
  </div>
</div>
```

### 5. Data Attributes on Rows
Every `<tr>` carries data attributes for search:
```html
<tr data-proc="R" data-act="R-ELEC-001" data-risk="การคำนวณ..."
    data-ctrl="การทบทวนและอนุมัติ..." data-test="จากระบบ ERP..."
    data-risk-code="R-ELEC-001.R1">
```

## Rowspan Pattern
กิจกรรม (col 1) uses rowspan across all control rows of the same activity:
```python
if gi == 0:
    html.append(f'<td rowspan="{span}" class="act-merge" data-col="1" contenteditable="true">{act_display}</td>')
```

## Data Extraction (CRITICAL)

### Risk-level fields (per risk, same for all controls)
```python
for risk in act.get("risks", []):
    pols = [p.get("text","") for p in risk.get("policies",[])]  # list
    procs = [pr.get("text","") for pr in risk.get("procedures",[])]  # list
    ind = risk.get("indicator_name","")  # string
    poison = risk.get("poison","")  # string
    report = risk.get("report_name","")  # string
    validations = [v.get("text","") for v in risk.get("validations",[])]  # list
```

### Control-level fields (per control within risk)
```python
for ctrl in risk.get("controls", []):
    ctrl_name = ctrl.get("control_name","")
    tests = "\n\n".join([t.get("test_name","") for t in ctrl.get("tests",[])])
    q_text = ctrl.get("question_text","")
```

## CSS Snippets

### Resize Handle
```css
table.rcm thead th { position: relative; }
table.rcm thead th .resize-handle {
  position: absolute; right: 0; top: 0; bottom: 0;
  width: 6px; cursor: col-resize; z-index: 20;
}
table.rcm thead th .resize-handle:hover { background: rgba(255,255,255,0.3); }
```

### Column Toggle Menu
```css
.col-toggle-wrap { position: relative; display: inline-block; }
.col-toggle-menu {
  display: none; position: absolute; top: 100%; left: 0;
  background: white; border: 1.5px solid #c5cae9;
  border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 200; min-width: 220px; padding: 8px 0;
}
.col-toggle-menu.show { display: block; }
.col-toggle-menu label.mandatory { color: #9e9e9e; }
```

### Detail Row Grid
```css
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}
.detail-item { background: white; border-radius: 6px; padding: 8px 12px; }
.detail-full { grid-column: 1 / -1; }
```

## Print (@media print)
```css
@media print {
  .app-header, .toolbar, .sheet-tabs { display: none; }
  tr.detail-row { display: table-row !important; }
  .expand-btn, .resize-handle { display: none; }
  th.col-hidden, td.col-hidden { display: table-cell !important; } /* show all */
  @page { size: A3 landscape; margin: 6mm; }
}
```

## File Size
Expect ~15-25 MB for 2,695 rows across 9 processes with all detail data embedded as JS.

## Build Strategy
Large HTML files cannot be built in a single `write_file` call. Use this pattern:
1. `execute_code` → build CSS header → `write_file` (overwrite)
2. `execute_code` → build body HTML → write to `_body.html`
3. `execute_code` → build detail data JS + main JS → write to `_js.html`
4. `terminal` → `cat header body js > final.html`
