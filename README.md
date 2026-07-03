# KAS Hermes Skills

ชุด Skills สำหรับงานตรวจสอบภายใน (Internal Audit) บน Hermes Agent

## 📦 Skills ที่มี

| Skill | รายละเอียด |
|-------|-----------|
| `kas-master-context` | สร้าง Master Context สำหรับกระบวนการทางธุรกิจ — ขั้นตอนปฏิบัติงาน, ประเมินความเสี่ยง, ควบคุม, วิธีตรวจสอบ |
| `kas-model-routing` | ตั้งค่า Model Routing — DeepSeek V4 Pro หลัก, Gemini Flash สำหรับงานอ่านเอกสาร |
| `kas-ia-report-helper` | ช่วยร่างรายงานตรวจสอบภายในภาษาไทย ตามกรอบ 5C's |

---

## 🚀 วิธีติดตั้ง (สำหรับน้องในทีม)

### 🔥 One-liner (Git Bash / PowerShell)

Copy ทั้งบล็อกด้านล่าง วางแล้วกด Enter (ติดตั้ง 3 skills รวดเดียว):

**📌 Git Bash:**
```bash
for url in master/kas-master-context master/kas-model-routing master/productivity/kas-ia-report-helper; do hermes skills install "https://raw.githubusercontent.com/thanatkjr/kas-hermes-skills/$url/SKILL.md"; done
```

**📌 PowerShell:**
```powershell
"kas-master-context","kas-model-routing","productivity/kas-ia-report-helper" | ForEach-Object { hermes skills install "https://raw.githubusercontent.com/thanatkjr/kas-hermes-skills/master/$_/SKILL.md" }
```

### ติดตั้งทีละตัว (cmd / Terminal ไหนก็ได้)

```
hermes skills install https://raw.githubusercontent.com/thanatkjr/kas-hermes-skills/master/kas-master-context/SKILL.md
hermes skills install https://raw.githubusercontent.com/thanatkjr/kas-hermes-skills/master/kas-model-routing/SKILL.md
hermes skills install https://raw.githubusercontent.com/thanatkjr/kas-hermes-skills/master/productivity/kas-ia-report-helper/SKILL.md
```

หลังติดตั้งเสร็จ → `hermes skills list` เช็คว่ามีครบ 3 ตัว → restart Hermes หรือ `/reload-skills`

### 🔄 เมื่อมีอัปเดต

```
hermes skills update
```

---

## 📁 โครงสร้าง Repo

```
├── kas-master-context/
│   ├── SKILL.md
│   └── references/
├── kas-model-routing/
│   └── SKILL.md
└── productivity/
    └── kas-ia-report-helper/
        └── SKILL.md
```