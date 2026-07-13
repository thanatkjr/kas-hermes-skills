# Synchronize / Merge Reference

Detailed instructions for Phase 5: ผสาน (Synchronize).

## Overview

Merge multiple KAS Note HTML files from different team members who recorded notes on the same/similar topic into one unified merged note.

## Step 1: Discover Source Notes

1. Ask user: **Project/Company** and **Topic keyword**
2. Scan `C:\Users\ASUS\Documents\IA_Notes\{Company}/` for `*_note.html` files
3. Filter by topic keyword in filename
4. Show list to user → confirm which to include (minimum 2)

## Step 2: Extract Data from Each Note

For each note HTML file:
1. Read the HTML
2. Parse the `<table id="analysis-table">` to extract rows
3. For each row, extract: row number, raw text, category (selected option value)
4. Also extract metadata: recorder name, recorder code, date, interviewee

## Step 3: Align Rows Across Notes

Use Python's `difflib.SequenceMatcher` to compute similarity between every pair of rows across all notes.

**Algorithm:**
```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# For each row in note A, find best match in note B
# Pair rows where similarity >= 0.75
# Unmatched rows become standalone entries
```

**Alignment rules:**
- Greedy matching: for each row in the first note, find the best match in other notes
- A row can only be matched once
- Similarity threshold: 0.75 (75%)
- After all matches, remaining unmatched rows are added as-is

## Step 4: Classify Each Row Group

### Unified (≥75% similar across ALL versions)
- Merge content into ONE version
- Use the clearest/most complete wording
- If wordings differ slightly but meaning is same → use the most detailed version
- Mark as 🟢 "สอดคล้องกันทุกรายการ"
- Category: use the majority classification; if tie, use the first note's classification

### Conflicting (<75% similar in at least one pair)
- Mark as 🔴 "ข้อมูลไม่ตรงกัน"
- Show all versions in comparison table
- Each version tagged with source recorder code
- Highlight differing parts

## Step 5: Generate Merged Note HTML

Use template `templates/merged-note.html`.

### {{SOURCE_LIST}} format:
```html
<li>📝 <span class="source-tag">THAN</span> 20260712_1130_การจัดซื้อ_note.html — ผู้จัดการบัญชี</li>
<li>📝 <span class="source-tag">SOMS</span> 20260712_1400_การจัดซื้อ_note.html — ผู้จัดการคลัง</li>
```

### {{MERGED_ROWS}} format:

**Unified row:**
```html
<tr class="row-unified">
  <td class="col-num">1</td>
  <td>
    <span class="badge-unified">🟢 สอดคล้อง</span>
    <div contenteditable="true">merged content here</div>
    <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:4px">
      ที่มา: <span class="source-tag">THAN</span> <span class="source-tag">SOMS</span>
    </div>
  </td>
  <td>
    <select class="cat-select">
      <option value="PR" style="color:#2563eb" selected>🔵 PR — ขั้นตอนปฏิบัติ</option>
    </select>
  </td>
  <td><span class="badge-unified">🟢 สอดคล้อง</span></td>
</tr>
```

**Conflict row:**
```html
<tr class="row-conflict">
  <td class="col-num">2</td>
  <td>
    <span class="badge-conflict">🔴 ข้อมูลไม่ตรงกัน</span>
    <div style="margin-top:8px">
      <strong>⚠️ ความแตกต่างระหว่างแหล่งข้อมูล:</strong>
      <table class="compare-table">
        <tr>
          <th style="width:20%">แหล่งที่มา</th>
          <th>เนื้อหา</th>
        </tr>
        <tr>
          <td><span class="source-tag">THAN</span> ผจก.บัญชี</td>
          <td>budget capex เคยมี แต่ปี 69 ไม่ได้ทำ</td>
        </tr>
        <tr>
          <td><span class="source-tag">SOMS</span> ผจก.คลัง</td>
          <td>budget capex ยังมีอยู่ แต่ลดลงจากปีก่อน 30%</td>
        </tr>
      </table>
      <p style="margin-top:8px;color:var(--red);font-size:0.85rem">
        🔴 <strong>จุดที่ขัดแย้ง:</strong> "ไม่ได้ทำ" vs "ยังมีอยู่แต่ลดลง" — 
        ข้อมูลเกี่ยวกับการจัดทำ budget capex ในปี 2569 ไม่ตรงกัน
      </p>
    </div>
  </td>
  <td>
    <select class="cat-select">
      <option value="I" style="color:#ef4444" selected>🔴 I — สิ่งผิดปกติ</option>
    </select>
  </td>
  <td><span class="badge-conflict">🔴 ขัดแย้ง</span></td>
</tr>
```

## Step 6: Present to User & Resolve Conflicts

After generating the merged note:

1. Show summary: "{N} รายการสอดคล้อง, {M} รายการขัดแย้ง"
2. Path to merged note HTML
3. For each conflict, ask user which version to keep:
   ```
   ข้อมูลส่วน "budget capex" มีความเห็นต่าง:
   1. THAN: "ไม่ได้ทำ"
   2. SOMS: "ยังมีอยู่แต่ลดลง 30%"
   
   ต้องการยึดตาม version ใด? (1, 2, หรือระบุเนื้อหาเอง)
   ```

**Key principle:** User does NOT have to pick one entire file as "correct". They can choose per-conflict, or write their own compromise text.

## Step 7: Finalize Merged Report

After all conflicts resolved → user says "ยืนยันผสาน":

1. Read the updated merged note HTML
2. Generate final merged report:
   `{YYYYMMDD}_{HHMM}_{Topic}_MERGED_{RECORDER}_report.html`
3. Same 10-section structure but add "📂 แหล่งที่มา" section listing all source notes
4. Add `source-merged` badge on content that came from merge

## Conflict Resolution — User Options

For each conflict row, the user can:
- **Pick a version:** "use THAN" or "use SOMS"
- **Combine:** "keep both but note discrepancy" — adds footnote
- **Write custom:** user provides their own text
- **Flag for follow-up:** mark as "ต้องสอบถามเพิ่มเติม"

## After Resolution

- Update the merged note HTML with choices
- Generate merged report
- All source attribution preserved in appendix
