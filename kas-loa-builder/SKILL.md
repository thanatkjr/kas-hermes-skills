---
name: kas-loa-builder
description: "สร้างและแก้ไขไฟล์ Excel ตารางอำนาจอนุมัติ (Limit of Authority / LOA) — อ่านทุก sheet, ยุบ/เพิ่มคอลัมน์, ปรับ merged cells, แทนที่ข้อความ, highlight มุมมองเจ้าของ, บันทึกเป็นเวอร์ชันใหม่"
version: 1.0.0
author: KAS (Kandit Advisory Services)
tags: [loa, limit-of-authority, excel, openpyxl, internal-audit, corporate-governance, KAS]
related_skills: [okas-markitdown, okas-guard]
---

# KAS LOA Builder

สร้างและแก้ไขไฟล์ Excel ตารางอำนาจอนุมัติองค์กร (Limit of Authority) ด้วย Python openpyxl

## Overview

LOA files are multi-sheet Excel workbooks. Each sheet with a 10-column authority table follows this structure:

| Col | Header |
|-----|--------|
| A | ประเภทการดำเนินงาน |
| B–H | ผู้มีอำนาจอนุมัติ (7 levels) |
| I | หมายเหตุ |
| J | เอกสารประกอบการอนุมัติ |

This skill covers common LOA manipulation tasks: reading all sheets, collapsing/adding approval columns, repairing merged cells after column deletion, text replacement, and owner-perspective highlighting.

## When to Use

- User asks to modify an LOA Excel file: change columns, merge approval levels, add/remove authority tiers
- User asks to highlight rows from a specific stakeholder perspective (owner, auditor, department head)
- User asks to convert between named-role (Supervisor/Manager/GM) and level-based (L4/L5/L6) structures
- User asks to create a new version of an LOA file with structural changes

## Workflow

### Step 1: Read all sheets first

Use `okas-markitdown` smart_convert.py to convert the .xlsx to .md, then read all sheets to understand the full structure before touching the Excel file. Never modify an LOA you haven't fully read.

### Step 2: Inspect the xlsx structure with openpyxl

```python
from openpyxl import load_workbook
wb = load_workbook(path)
# Identify which sheets have the 10-column LOA table
# Check headers in row 2, columns 2-8
```

### Step 3: Make modifications

Common patterns:

**Collapsing columns** (e.g. merge Excom+BOD into Shareholder):
1. Merge values from deleted columns into the surviving column BEFORE deletion
2. Snapshot merged_cells.ranges, clear all, delete columns, re-add adjusted ranges
3. Use `col_letter_to_num` / `col_num_to_letter` helpers to shift column refs

**Key pitfall:** `ws.delete_cols()` shifts remaining columns left, but merged cell ranges become invalid. Always clear-and-rebuild merged cells:
```python
old_ranges = [str(m) for m in ws.merged_cells.ranges]
ws.merged_cells.ranges.clear()
ws.delete_cols(start_col, count)
# Re-add with adjusted column letters
for old in old_ranges:
    new = adjust_range_str(old)  # cols >= deleted_col shift left by count
    if new:
        ws.merge_cells(new)
```

**Adding columns** (not done this session, but common): use `ws.insert_cols()` then shift merged cells right.

### Step 4: Apply perspective-based highlighting

For **owner perspective**, highlight rows matching these keyword categories:
- โครงสร้างบริษัท & การควบคุม (LOA itself, subsidiaries, directors, auditors)
- งบประมาณ & การเงินใหญ่ (annual budgets, extra budget requests, financial statements)
- กู้ยืม & ภาระผูกพัน (loans, guarantees, debt restructuring)
- ลงนาม & สัญญาสำคัญ (binding contracts)
- ทรัพย์สินสำคัญ (land/building transactions)
- บัญชีธนาคาร & ผู้ลงนาม (bank accounts, cheque signatories)

The full keyword list is in `references/owner-keywords.md`.

Use `PatternFill(start_color="FFD6E4", end_color="FFD6E4", fill_type="solid")` for light pink.

### Step 5: Save as new version

Always save to a new filename (v2, v3, etc.) — never overwrite the original.

## Column Structures

Two common naming conventions in Thai LOA files:

**Named roles** (v1 Draft style):
Supervisor → Manager → GM → Executive Director → Executive Committee → BOD → Shareholder

**Level-based** (Thavorn style):
L4 (Manager) → L5 (HOD) → L6 (Division Head) → L7 (MD) → Executive Committee → BOD → Shareholder

## Sheets to expect in a complete LOA

1. วิธีการกรอกข้อมูล — instructions
2. Cover — objectives, scope, definitions, principles
3. Draft_LOA — main authority table (7 categories)
4. ระเบียบ การขาย — sales regulations
5. ระเบียบ จัดซื้อจัดจ้าง — procurement
6. ระเบียบ การเงินและการบัญชี — finance & accounting
7. ระเบียบ Fixed Asset & MT — fixed assets & maintenance
8. ระเบียบ HR — human resources
9. ระเบียบ CRM — customer relations
10. ระเบียบเทคโนโลยีและสารสนเทศ(IT) — IT
11. ระเบียบ PDPA — data privacy
12. List ระเบียบที่ต้องจัดทำเพิ่ม — pending regulations
13. ระเบียบ การซ่อมบำรุง — maintenance (separate from FA)

## Support Files

- `references/owner-keywords.md` — full keyword list for owner-perspective pink highlighting across all LOA sheet types
- `scripts/loa_utils.py` — reusable Python helpers: `adjust_merged_ranges_after_delete_cols()`, `merge_authority_values()`, `col_letter_to_num()`, `col_num_to_letter()`

## Pitfalls

1. **Merged cells break after column deletion** — `delete_cols()` shifts cells but merged ranges become stale. Always clear-and-rebuild as shown in Step 3.
2. **`unmerge_cells()` throws KeyError** when merged range references empty cells — use `ws.merged_cells.ranges.clear()` instead of iterating with unmerge.
3. **Row 2 headers may be in merged cells with Row 1** — check for `B1:H1` merged "ผู้มีอำนาจอนุมัติ" before reading row 2 values.
4. **Some sheets use (L4)-(L7) instead of named roles** — scan row 2 values to detect which convention is in use.
5. **Never modify the original file** — always save as a new version.
