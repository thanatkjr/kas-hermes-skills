# RCM HTML Template v2 — Sheet Tabs + Risk Tags + Expandable Detail Rows

Enhanced template for multi-process RCM (3+ processes). Includes sheet-tab navigation, color-coded risk category badges, and expandable detail rows showing all 6 risk-level fields.

> Built and verified with SICT (Silicon Craft Technology) — 9 processes, 281 activities, 2,695 rows, 1,294 risks

---

## When to Use v2 vs v1

| Situation | Template |
|-----------|----------|
| 1-2 processes, simple editing | v1 (`references/rcm-html-template.md`) |
| 3+ processes, tab switching, client presentation | **v2** |
| Print A3 landscape per process | v2 (`@media print` page-break per process) |
| Export to PPTX 16:9 | v2 (kas-htmlformat borders) |

---

## v2 Feature Checklist

- [ ] **Sheet Tabs** — `<div class="sheet-tab">` per process with row count badges
- [ ] **Expand/Collapse All** — `📖 แสดงทุก Process` / `📕 แสดง Process เดียว`
- [ ] **Risk Category Badges** — 12 color-coded `<span class="risk-cat-tag">` per row
- [ ] **Rowspan** — Activity code + name merged across control rows
- [ ] **9-Column Main Table** — #, กิจกรรม, ชื่อกิจกรรม, ประเภท, ความเสี่ยง, การควบคุม, วิธีการตรวจสอบ, คำถาม, ลักษณะ
- [ ] **▶ Expandable Detail Rows** — Click ▶ on risk name → shows Poison, KRI, Report, Policy, Procedure, Validation
- [ ] **🔽/🔼 Global Expand/Collapse** — Expand All Details / Collapse All Details buttons
- [ ] **Search + Column Filter** — 6-column dropdown + text search + result counter
- [ ] **Sticky Header** — All 3 bars (app-header, toolbar, sheet-tabs) sticky
- [ ] **Save + Print** — 💾 Blob download / 🖨️ A3 landscape
- [ ] **Print shows all details** — `@media print { tr.detail-row { display: table-row !important; } }`

---

## CSS Architecture

### 3-Layer Sticky System

```css
.app-header  { position: sticky; top: 0;    z-index: 100; }
.toolbar     { position: sticky; top: 58px; z-index: 99;  }
.sheet-tabs  { position: sticky; top: 104px; z-index: 98;  }
```

### Risk Category Tag Colors

```css
.cat-Operational { background: #ef6c00; }  /* orange */
.cat-Fraud       { background: #c62828; }  /* red */
.cat-Compliance  { background: #1565c0; }  /* blue */
.cat-Reporting   { background: #2e7d32; }  /* green */
.cat-Technology  { background: #6a1b9a; }  /* purple */
.cat-Financial   { background: #00695c; }  /* teal */
.cat-Strategic   { background: #37474f; }  /* dark grey */
.cat-Human       { background: #ad1457; }  /* pink */
.cat-Supply      { background: #e65100; }  /* deep orange */
.cat-Customer    { background: #00838f; }  /* cyan */
.cat-Reputational{ background: #4e342e; }  /* brown */
.cat-Emerging    { background: #311b92; }  /* deep purple */
```

### Detail Row Grid

```css
tr.detail-row { display: none; }
tr.detail-row.show { display: table-row; }
td.detail-cell { background: #f0f4ff; border-bottom: 2px solid #3949ab; }

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 20px;
}
.detail-item { /* 1-column card for Poison, KRI, Report */ }
.detail-full { grid-column: 1 / -1; /* full-width for Policy, Procedure, Validation */ }
```

### Poison Badges

```css
.poison-badge { border-radius: 12px; font-weight: 700; }
.poison-โลภะ { background: #fff3e0; color: #e65100; }
.poison-โทสะ { background: #fce4ec; color: #c62828; }
.poison-โมหะ { background: #f3e5f5; color: #6a1b9a; }
```

---

## Data Extraction Pattern

### Correct extraction (tests/questions from CONTROL level)

```python
def build_rows(data):
    rows = []
    details = {}  # risk_code → {poison, indicator, policies, procedures, validations, report}
    
    for act in data["activities"]:
        for risk in act.get("risks", []):
            rc = risk["risk_code"]
            
            # Store risk-level detail for expand rows
            details[rc] = {
                "poison": risk.get("poison", ""),
                "indicator": risk.get("indicator_name", ""),
                "policies": [p.get("text","") for p in risk.get("policies", [])],
                "procedures": [p.get("text","") for p in risk.get("procedures", [])],
                "validations": [v.get("text","") for v in risk.get("validations", [])],
                "report": risk.get("report_name", ""),
            }
            
            controls = risk.get("controls", [])
            for ci, ctrl in enumerate(controls):
                # Tests from CONTROL level (NOT risk level!)
                test_names = [t.get("test_name","") for t in ctrl.get("tests", [])]
                test_text = "\n\n".join(test_names)
                
                # Question from CONTROL level
                question = ctrl.get("question_text", "")
                
                rows.append({
                    "risk_code": rc,
                    "ctrl_name": ctrl.get("control_name", ""),
                    "ctrl_nature": ctrl.get("control_nature", ""),
                    "test_name": test_text,
                    "q_text": question,
                    "is_first": (ci == 0),
                    # ... other fields
                })
    
    return rows, details
```

---

## JS Architecture

### Detail Row Injection (run on DOMContentLoaded)

```javascript
function injectDetailRows() {
  processOrder.forEach(pc => {
    const tbody = document.getElementById('panel-' + pc).querySelector('tbody');
    const rows = tbody.querySelectorAll('tr:not(.detail-row)');
    
    // Group rows by risk_code
    const riskGroups = {};
    rows.forEach(row => {
      const rcode = row.getAttribute('data-risk-code');
      if (!rcode) return;
      if (!riskGroups[rcode]) riskGroups[rcode] = [];
      riskGroups[rcode].push(row);
    });
    
    // Insert detail row after each risk group's LAST row
    Object.entries(riskGroups).forEach(([rcode, groupRows]) => {
      const lastRow = groupRows[groupRows.length - 1];
      const detailRow = buildDetailRow(pc, rcode);
      lastRow.after(detailRow);
    });
  });
}
```

### Detail Row Builder (creates grid with all 6 fields)

```javascript
function buildDetailRow(pc, rcode) {
  const d = detailStore[pc + '|' + rcode];
  const tr = document.createElement('tr');
  tr.className = 'detail-row';
  tr.id = 'detail-' + pc + '-' + rcode;
  
  const td = document.createElement('td');
  td.colSpan = 9;
  td.className = 'detail-cell';
  
  let h = '<div class="detail-grid">';
  // Row 1: Poison | KRI | Report (3 cards in 2-column grid)
  h += '<div class="detail-item"><div class="label">🔴 Poison</div>...</div>';
  h += '<div class="detail-item"><div class="label">📊 KRI</div>...</div>';
  h += '<div class="detail-item"><div class="label">📈 Report</div>...</div>';
  // Full-width rows: Policy, Procedure, Validation
  h += '<div class="detail-full"><div class="label">📋 Policy</div>...</div>';
  h += '<div class="detail-full"><div class="label">📝 Procedure</div>...</div>';
  h += '<div class="detail-full"><div class="label">📎 Validation</div>...</div>';
  h += '</div>';
  
  td.innerHTML = h;
  tr.appendChild(td);
  return tr;
}
```

### Detail Data Store (embedded as JS object)

```javascript
const detailStore = {};
detailStore["R|R-ELEC-001.R1"] = {
  "poison": "โมหะ",
  "indicator": "อัตราส่วนของ Sales Order ที่มีการแก้ไขราคา...",
  "policies": ["บริษัทกำหนดให้การจัดทำและแก้ไข BOM...", "..."],
  "procedures": ["ฝ่ายวิศวกรรมจัดทำและรับรอง BOM...", "..."],
  "validations": ["ตรวจสอบว่า BOM ที่ใช้คำนวณราคาขาย...", "..."],
  "report": "รายงาน BOM Cost vs. Selling Price Variance Analysis รายเดือน"
};
// ...1,294 entries total
```

---

## Print CSS

```css
@media print {
  .app-header, .toolbar, .sheet-tabs { display: none; }
  .process-panel { display: block !important; page-break-after: always; }
  .process-panel:last-child { page-break-after: auto; }
  .scroll-outer { overflow: visible; max-height: none; }
  table.rcm thead th { position: static; }
  tr.detail-row { display: table-row !important; }  /* force show all details */
  .expand-btn { display: none; }
  @page { size: A3 landscape; margin: 6mm; }
}
```

---

## File Size Expectations

| Components | Typical Size |
|-----------|:---:|
| 9 processes, ~2,700 rows | 15-20 MB |
| Detail data (1,294 risks × 6 fields) | ~1.6 MB (JS) |
| Body HTML (table rows) | ~6.5 MB |
| Total HTML | ~20 MB |

---

## Verified With

- **SICT (Silicon Craft Technology)** — 9 processes, 281 activities, 2,695 rows, 1,294 risks
- All 6 detail fields populated for 100% of risks
- Tab switching, search, expand/collapse, save, print — all verified working
