# Meeting Preparation HTML — Interactive Agenda + Findings

## When to Use

When the user is preparing materials for a client meeting (e.g., เตรียมคุย GM, Board presentation) — not an interview. They provide structured agenda items incrementally, and the output is an interactive HTML document for use *during* the meeting.

**Key triggers:**
- "เตรียมคุย GM", "เตรียมประชุม", "เตรียมนำเสนอ"
- "ทำสรุปเป็น html", "ทำไฟล์สำหรับประชุม"
- User provides numbered agenda items with sub-points

**Distinction from kas-note Phase 1–5:**
- kas-note: interview recording → classification → report
- Meeting prep: agenda collection → interactive HTML with findings slots

## Workflow

### Step 1: Collect Agenda Items Incrementally

1. Ask user for topic/title (e.g., "เตรียมคุย GM — กรอบนโยบายจัดซื้อ")
2. Create a `.md` raw file immediately in the project folder: `{project}/notes_prep_{topic}_{DDMMYY}.md`
3. As user provides each agenda item:
   - **Append to .md file immediately** — do not batch
   - Acknowledge with item number + brief summary
   - The .md serves as the durable source of truth

### Step 2: Generate Interactive HTML

Create `{project}/{topic}_{DDMMYY}.html` with:

**Layout:**
- Two-column table: Left = Agenda (50%), Right = Findings Textareas (50%)
- Header with title, project name, date
- Toolbar: Save | Export HTML | Export TXT | Clear

**Left column (Agenda):**
- Numbered items with polished, professional wording
- **User prefers DETAILED content** — not brief one-liners. Each item should include:
  - Sub-items with descriptive labels (use colored badges/tags)
  - Examples and scenarios
  - Highlighted key terms (yellow highlight for critical points)
  - For process items: numbered steps with clear owner at each step
  - For policy items: scope, criteria, exceptions, enforcement

**Right column (Findings):**
- Editable `<textarea>` for each agenda item
- Label: "ข้อตรวจพบสำคัญ" (Key Findings)
- Green border + light green background when content exists
- Dashed border when empty

**JavaScript features:**
- `localStorage` auto-save/load (key = `{project}_{topic}_{DDMMYY}`)
- Export HTML: clone DOM with textarea values injected → download as `.html`
- Export TXT: compile all agenda + findings → download as `.txt`
- Clear: confirm prompt → wipe localStorage + textareas
- Auto-detect content in textareas (add `.has-content` class on input)

### Step 3: User Edits & Exports

User opens HTML → fills findings → saves → exports for sharing with meeting participants.

## Style Guidelines for Left Column

- Use `<span class="sub-label">` (green badge) for sub-section headers
- Use `<span class="highlight">` (yellow highlight) for key terms, thresholds, critical rules
- Every agenda item should answer: WHAT is the policy/rule, WHY does it matter, HOW is it implemented, WHO is responsible
- Include concrete examples (e.g., "ซื้อของจาก Vendor A — 3 ใบ PO ใบละ 19,000 บาทในวันเดียวกัน — แบบนี้คือการแบ่งซื้อ")
- For compliance items: always state the consequence (e.g., "หากไม่แจ้ง — ถือเป็นความผิดทางวินัย")

## CSS Standards

- Header: `linear-gradient(135deg, #1a3a4a 0%, #2d6a4f 100%)` — dark teal to green
- Body: `#f5f5f5` background, Sarabun/Tahoma font
- Table: white background, rounded corners, subtle shadow
- Topic numbers: green circle badges (`#2d6a4f`)
- Sub-labels: `#e8f5e9` background, `#2d6a4f` text
- Highlights: `#fff3cd` background
- Buttons: Save=green, Export=dark-teal, TXT=gray, Clear=light-gray

## Pitfalls

1. **Don't make left column too brief** — user explicitly wants rich detail, not one-liners
2. **Save .md file on EVERY chunk** — TUI can lose input on Windows
3. **Use localStorage key that includes date** — prevents collision across sessions
4. **Export HTML must embed textarea values** — clone DOM + inject values before download
5. **Don't use Phase 1–5 kas-note flow** — this is a different workflow (meeting prep ≠ interview)

## Template Placeholders

The template at `templates/meeting-prep.html` uses these placeholders — replace with actual values:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{TITLE}}` | Meeting title | `เตรียมประชุม GM — กรอบนโยบายจัดซื้อ` |
| `{{PROJECT}}` | Client/project name | `Khaolak Emerald Resort` |
| `{{DEPARTMENT}}` | Department/team | `Internal Audit` |
| `{{HEADER_EMOJI}}` | Header icon | `📋` |
| `{{DATE_THAI}}` | Date in Thai format | `22 กรกฎาคม 2569` |
| `{{FOOTER_TEXT}}` | Footer description | `Internal Audit Preparation` |
| `{{STORAGE_KEY}}` | localStorage key (include date) | `khaolak_gm_prep_220726` |
| `{{EXPORT_FILENAME}}` | Download filename (no ext) | `gm_prep_purchasing_220726` |
| `{{LABELS_JSON}}` | JSON object mapping topic IDs to labels | `{"1":"ขอบเขต...","2":"การขึ้นทะเบียน..."}` |
| `{{TABLE_ROWS}}` | HTML for each `<tr>` with agenda + textarea | See generated example below |

**TABLE_ROWS format** — each row:
```html
<tr>
  <td>
    <div class="topic-title"><span class="topic-num">{{NUM}}</span>{{TITLE}}</div>
    <div class="topic-detail">{{DETAIL_WITH_UL_OL}}</div>
  </td>
  <td>
    <div class="finding-label">ข้อตรวจพบสำคัญ</div>
    <textarea class="finding-area" data-topic="{{TOPIC_ID}}" placeholder="กรอกข้อตรวจพบ..."></textarea>
  </td>
</tr>
```
