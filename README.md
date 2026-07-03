# KAS Hermes Skills

ชุด Skills สำหรับงานตรวจสอบภายใน (Internal Audit) บน Hermes Agent

## 📦 Skills ที่มี

| Skill | รายละเอียด |
|-------|-----------|
| `kas-master-context` | สร้าง Master Context สำหรับกระบวนการทางธุรกิจ — ขั้นตอนปฏิบัติงาน, ประเมินความเสี่ยง, ควบคุม, วิธีตรวจสอบ |
| `kas-model-routing` | ตั้งค่า Model Routing — DeepSeek V4 Pro หลัก, Gemini Flash สำหรับงานอ่านเอกสาร |
| `kas-ia-report-helper` | ช่วยร่างรายงานตรวจสอบภายในภาษาไทย ตามกรอบ 5C's |

## 🚀 วิธีติดตั้ง

### ครั้งแรก (สำหรับน้องในทีม)

เปิด Terminal แล้วพิมพ์:

```bash
hermes skills tap add https://github.com/thanatkjr/kas-hermes-skills.git
```

จากนั้น restart Hermes หรือใช้ `/reload-skills`

### เมื่อมีอัปเดต

```bash
hermes skills update
```

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