---
name: kas-note
description: Use when the user wants to record interview/meeting notes for internal audit work — collecting raw data piece by piece, classifying into audit categories (Policy/Procedure/Incident/Risk/General Info/Other), generating editable HTML notes, and compiling structured reports. Also supports merging multiple note versions (Synchronize). Triggers on phrases like "เริ่มบันทึก", "note taking", "interview notes", "บันทึกการสัมภาษณ์", "ผสาน", "sync", or any audit note-taking request. Protected by KAS guard.
version: 2.0.0
author: Thanat Kerdcharoen (KAS)
license: Proprietary — KAS Internal Use Only
platforms: [windows]
metadata:
  hermes:
    tags: [kas, internal-audit, note-taking, interview, classification, report, sync]
    related_skills: [kas-guard, kas-master-context]
---

# KAS Note — Internal Audit Interview Notes

## Overview

A structured 5-phase workflow for recording internal audit interview notes. Raw client information is collected piece-by-piece into a durable `.txt` file (crash-safe), classified into 6 audit categories, presented in an editable HTML note, compiled into a professional structured report, with an additional **Synchronize** phase for merging multiple note versions from different team members.

**Default notes directory:** `C:\Users\ASUS\Documents\IA_Notes\`

## File Naming Convention

| File Type | Pattern | Example |
|-----------|---------|---------|
| Raw TXT | `{YYYYMMDD}_{HHMM}_{Topic}_raw.txt` | `20260712_1130_การจัดซื้อ_raw.txt` |
| Note HTML | `{YYYYMMDD}_{HHMM}_{Topic}_note.html` | `20260712_1130_การจัดซื้อ_note.html` |
| Report HTML | `{YYYYMMDD}_{HHMM}_{Topic}_{RECORDER}_report.html` | `20260712_1130_การจัดซื้อ_THAN_report.html` |

> `{RECORDER}` = 4-character English abbreviation of recorder's name (default: `THAN` for Thanat)

> Notes directory: `C:\Users\ASUS\Documents\IA_Notes\{Company}/`

## Phase 1: Start Recording (เริ่มบันทึก)

**Trigger:** "เริ่มบันทึก", "note:", "บันทึกการสัมภาษณ์", "interview notes"

### Step 1: Gather Metadata
Ask the user (minimal — prefer quick defaults):

1. **หัวข้อ (Topic):** e.g., "การสั่งซื้อวัตถุดิบ"
2. **Project/บริษัท (Company):** If in a Hermes Project, assume that. Otherwise ask.
3. **ผู้ให้สัมภาษณ์ (Interviewee):** Name + position (optional)
4. **ชื่อย่อผู้บันทึก 4 ตัว (Recorder):** Default `THAN` — ask only if different person

### Step 2: Create Raw TXT File

Use current datetime for filename. Create at:
`C:\Users\ASUS\Documents\IA_Notes\{Company}/{YYYYMMDD}_{HHMM}_{Topic}_raw.txt`

Header format:
```
============================================
บันทึกการสัมภาษณ์ / Interview Notes
============================================
วันที่บันทึก : {DD MMMM YYYY} เวลา {HH:MM} น.
วันที่สัมภาษณ์: {DD MMMM YYYY} (ถ้าต่างจากวันที่บันทึก)
หัวข้อ       : {Topic}
บริษัท       : {Company}
ผู้ให้สัมภาษณ์: {Interviewee}
ผู้บันทึก    : {Full Name} ({RECORDER})
============================================

--- ข้อมูลดิบ (Raw Data) ---

```

### Step 3: Confirm
"✅ พร้อมบันทึกครับ — หัวข้อ: **{Topic}** | บริษัท: **{Company}** | Note: `{filename}`"

## Phase 2: Recording (ระหว่างบันทึก)

**CRITICAL:** Agent MUST NOT analyze, comment, or engage with content.

For EVERY user message during recording:
1. **Append** raw text verbatim to the TXT file
2. **Respond ONLY:** "บันทึกแล้วรอประมวลผลครับ"

**Stop signals:** "จบบันทึก", "พอแล้ว", "วิเคราะห์", "end recording", "done", "analyze"

## Phase 3: Classification & Note (ตารางวิเคราะห์ข้อมูล)

### Step 1: Read Raw Data
Extract all lines after `--- ข้อมูลดิบ (Raw Data) ---`

### Step 2: Split into Segments
Each sentence/paragraph/statement = one row. Number sequentially.

### Step 3: Classify

| Code | Category | Description |
|------|----------|-------------|
| **P** | นโยบาย (Policy) | กรอบ/แนวทางตัดสินใจ, ควรทำ/ห้ามทำ/ต้องทำ, อำนาจตัดสินใจ |
| **PR** | ขั้นตอนปฏิบัติ (Procedure) | รายละเอียดขั้นตอนปฏิบัติงานในกิจกรรม/กระบวนการ |
| **I** | สิ่งผิดปกติ (Incident) | เหตุการณ์ผิดปกติที่เคยเกิด/กำลังเกิด — อาจเป็นข้อตรวจพบ |
| **R** | ความเสี่ยง (Risk) | เหตุการณ์ที่อาจเกิดและกระทบองค์กร |
| **G** | ข้อมูลทั่วไป (General Info) | ข้อมูลองค์กร, กฎหมาย, สัญญาสำคัญ |
| **O** | อื่นๆ (Other) | ไม่เข้าพวกข้างต้น |

### Step 4: Generate Note HTML

Create `{YYYYMMDD}_{HHMM}_{Topic}_note.html` from `templates/analysis-table.html`.

**3-column table (all editable):** # | ข้อมูลดิบ | ประเภท (dropdown with colored icons)

> Dropdown MUST show colored icon badges matching the legend — see template.

### Step 5: Respond

"✅ **Note พร้อมแล้ว** — {N} รายการ | `{filename}`
เปิดไฟล์ใน browser เพื่อตรวจสอบ/แก้ไข → กด **Confirm & Save** → กลับมาพิมพ์ **'ยืนยัน'**"

## Phase 4: Confirm & Enhance (รายงานฉบับสมบูรณ์)

**Trigger:** "ยืนยัน", "confirm", "enhance", "จัดทำรายงาน"

### Step 1: Read Note HTML
Parse the table to get final classifications (user may have edited).

### Step 2: Generate Report

Create `{YYYYMMDD}_{HHMM}_{Topic}_{RECORDER}_report.html` from `templates/final-report.html`.

**10-section structure:**
1. **Header** — date/time, recorder
2. **Company & Topic** — + related notes in same project
3. **Interviewee** (if any)
4. **Policy** — สิ่งที่ต้องทำ/ควรทำ, ห้ามทำ, กรอบตัดสินใจ, อำนาจตัดสินใจ
5. **Procedure** — 🟢 มั่นใจสูง / 🔵 มั่นใจปานกลาง / 🔴 AI เสริม (ส่วนที่ขาด)
6. **Incidents & Risks**
7. **Key Internal Controls** — 🟢/🔵/🔴 same color scheme
8. **General Info**
9. **Other**
10. **Appendix** — all raw data verbatim

### Step 3: Respond
Report path + summary.

## Phase 5: Synchronize / ผสาน

**Trigger:** "ผสาน", "sync", "synchronize", "merge notes"

Merges multiple note HTML files (from different team members) on similar topics into one unified version.

### Step 5.1: Discover Notes to Merge

1. Ask user: **Project/Company** and **Topic keyword**
2. Find all `*_note.html` files in `C:\Users\ASUS\Documents\IA_Notes\{Company}/` matching the topic
3. List found notes → ask user to confirm which ones to include

### Step 5.2: Extract & Align Data

Read each note HTML, extract table rows (raw text + category).

**Alignment strategy:** Use Python's `difflib.SequenceMatcher` to match rows across versions:
- Pair rows by highest similarity score
- Unmatched rows become separate entries

### Step 5.3: Compare & Classify

For each aligned row group:

**≥75% similar across all versions:**
- Merge into ONE unified version (pick clearest/most complete wording)
- Mark as 🟢 "สอดคล้องกันทุกรายการ"

**<75% similar (conflicting):**
- Mark as 🔴 "ข้อมูลไม่ตรงกัน" 
- Show ALL versions in a comparison table
- Flag specific differences

### Step 5.4: Generate Merged Note

Create `{YYYYMMDD}_{HHMM}_{Topic}_merged_note.html` from `templates/merged-note.html`.

**Structure:**
- Header: project, topic, list of source notes with recorders
- For unified rows: single row with merged content + 🟢 badge
- For conflicting rows: expandable comparison table showing each version side-by-side with recorder name, highlighted differences
- All rows have editable category dropdown

### Step 5.5: Resolve Conflicts

Show the merged note to user. For each conflict:
- Ask: "ข้อมูลส่วนนี้มีความเห็นต่าง — ต้องการยึดตาม version ใด?"
- User picks which version(s) to keep
- Agent updates the merged note

### Step 5.6: Finalize

After all conflicts resolved → user says "ยืนยัน" → generate final merged report:
`{YYYYMMDD}_{HHMM}_{Topic}_MERGED_{RECORDER}_report.html`

Use same 10-section structure but add a "แหล่งที่มา" (Sources) section listing all original notes.

## State Tracking

- No raw file → Phase 1
- Raw exists, no note HTML → Phase 2 or ready for Phase 3
- Note HTML exists, no report → Ready for Phase 4
- Report exists → Done (offer new recording or sync)
- Multiple notes, user says "ผสาน" → Phase 5

## Common Pitfalls

1. **Responding to content during Phase 2** — MUST only say "บันทึกแล้วรอประมวลผลครับ"
2. **Not preserving original wording** — raw data must be verbatim
3. **Skipping the note phase** — always generate editable note before report
4. **Wrong file naming** — always use `{YYYYMMDD}_{HHMM}` not `{YYYY-MM-DD}`
5. **Forgetting RECORDER in report filename** — always append 4-char code
6. **Merging notes from different topics** — only merge notes with matching topic keywords
7. **Losing source attribution in merge** — always preserve which note each piece came from

## Verification Checklist

- [ ] File names follow `{YYYYMMDD}_{HHMM}_...` convention
- [ ] Report filename includes `_{RECORDER}_`
- [ ] Phase 2: only "บันทึกแล้วรอประมวลผลครับ" responses
- [ ] Note HTML dropdown shows colored icon badges
- [ ] Phase 5 merge preserves source attribution
- [ ] Conflict table shows all versions side-by-side
- [ ] Thai language throughout (labels, headings)
