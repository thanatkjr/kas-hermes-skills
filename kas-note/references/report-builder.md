# Report Builder Reference

Detailed instructions for the agent when building the final report HTML in Phase 4 and merged report in Phase 5.

## File Naming (IMPORTANT)

| Type | Pattern | Example |
|------|---------|---------|
| Raw TXT | `{YYYYMMDD}_{HHMM}_{Topic}_raw.txt` | `20260712_1430_การจัดซื้อ_raw.txt` |
| Note HTML | `{YYYYMMDD}_{HHMM}_{Topic}_note.html` | `20260712_1430_การจัดซื้อ_note.html` |
| Report HTML | `{YYYYMMDD}_{HHMM}_{Topic}_{RECORDER}_report.html` | `20260712_1430_การจัดซื้อ_THAN_report.html` |
| Merged Note | `{YYYYMMDD}_{HHMM}_{Topic}_merged_note.html` | `20260712_1500_การจัดซื้อ_merged_note.html` |
| Merged Report | `{YYYYMMDD}_{HHMM}_{Topic}_MERGED_{RECORDER}_report.html` | `20260712_1500_การจัดซื้อ_MERGED_THAN_report.html` |

> `{RECORDER}` = 4-char English code (default: `THAN` for Thanat)
> `{YYYYMMDD}` = e.g., `20260712` (no dashes)
> `{HHMM}` = 24-hour, e.g., `1430`

## Template Placeholders

### For final-report.html:

| Placeholder | Source |
|-------------|--------|
| `{{TOPIC}}` | From raw TXT header |
| `{{DATE}}` | "12 กรกฎาคม 2569 เวลา 14:30 น." |
| `{{RECORDER}}` | Full name (default: "Thanat Kerdcharoen") |
| `{{RECORDER_CODE}}` | 4-char code (default: "THAN") |
| `{{COMPANY}}` | From raw TXT header |
| `{{INTERVIEWEE}}` | From raw TXT header |
| `{{REPORT_ID}}` | `{YYYYMMDD}_{HHMM}_{RECORDER}` — e.g., "20260712_1430_THAN" |
| `{{GENERATED_DATE}}` | Current datetime when report is generated |
| `{{RELATED_NOTES}}` | Other notes in same project folder |
| `{{INTERVIEWEE_SECTION}}` | Section 3 HTML |
| `{{POLICY_SECTION}}` | Section 4 HTML |
| `{{PROCEDURE_SECTION}}` | Section 5 HTML |
| `{{INCIDENT_RISK_SECTION}}` | Section 6 HTML |
| `{{CONTROL_SECTION}}` | Section 7 HTML |
| `{{GENERAL_SECTION}}` | Section 8 HTML |
| `{{OTHER_SECTION}}` | Section 9 HTML |
| `{{APPENDIX}}` | Section 10 HTML |

### For analysis-table.html (Note):

| Placeholder | Description |
|-------------|-------------|
| `{{DATE}}` | Recording date/time |
| `{{TOPIC}}` | Topic |
| `{{COMPANY}}` | Company name |
| `{{INTERVIEWEE}}` | Interviewee name |
| `{{RECORDER}}` | Full name |
| `{{RECORDER_CODE}}` | 4-char code |
| `{{NOTE_ID}}` | `{YYYYMMDD}_{HHMM}` — unique note timestamp |
| `{{TABLE_ROWS}}` | Table body HTML |

### TABLE_ROWS format (each row):
```html
<tr>
  <td class="col-num">1</td>
  <td contenteditable="true">raw text here</td>
  <td>
    <select class="cat-select">
      <option value="P"  style="color:#7c3aed">🟣 P — นโยบาย</option>
      <option value="PR" style="color:#2563eb" selected>🔵 PR — ขั้นตอนปฏิบัติ</option>
      <option value="I"  style="color:#ef4444">🔴 I — สิ่งผิดปกติ</option>
      <option value="R"  style="color:#f59e0b">🟡 R — ความเสี่ยง</option>
      <option value="G"  style="color:#10b981">🟢 G — ข้อมูลทั่วไป</option>
      <option value="O"  style="color:#6b7280">⚫ O — อื่นๆ</option>
    </select>
  </td>
</tr>
```

## Building Each Section

### {{RELATED_NOTES}}
Scan `C:\Users\ASUS\Documents\IA_Notes\{Company}/` for other `*_raw.txt` files.
List with dates/topics. If none: "ยังไม่มีบันทึกอื่นใน Project นี้"

### {{INTERVIEWEE_SECTION}}
If interviewee exists:
```html
<div class="section">
  <h2>👤 ผู้รับการสัมภาษณ์</h2>
  <p><strong>ชื่อ:</strong> {name}</p>
  <p><strong>ตำแหน่ง:</strong> {position}</p>
</div>
```
If not, omit (empty string).

### {{POLICY_SECTION}}
From items classified as P. Group into:
1. ✅ สิ่งที่ต้องทำ/ควรทำ
2. 🚫 สิ่งที่ห้ามทำ
3. 🧭 กรอบการตัดสินใจ
4. ⚡ อำนาจในการตัดสินใจ

If none: `<p class="no-data">ไม่พบข้อมูลด้านนโยบายในการบันทึกนี้</p>`

### {{PROCEDURE_SECTION}}
From items classified as PR.

**Confidence colors:**
- 🟢 conf-high: ข้อมูลชัดเจน ครบถ้วน
- 🔵 conf-mid: มีข้อมูลแต่ไม่ครบถ้วน
- 🔴 conf-low: ข้อมูลไม่ชัดเจน — AI เติมเต็ม ระบุ `[AI เสริม]`

### {{INCIDENT_RISK_SECTION}}
Combine I and R items. Show incidents first, then risks.
If none: "ไม่พบข้อมูลด้านสิ่งผิดปกติหรือความเสี่ยง"

### {{CONTROL_SECTION}}
Identify key controls from procedures. Same 🟢/🔵/🔴 scheme.
For 🔴 items, add `[AI เสริม]` tag with inferred controls based on best practices.

### {{APPENDIX}}
ALL raw data items, verbatim, numbered.
