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

1. เปิด **PowerShell** (หรือ Terminal อะไรก็ได้)
2. **Copy ทั้งบรรทัดด้านล่างนี้** (ห้าม copy แค่ URL!):

```
hermes skills tap add https://github.com/thanatkjr/kas-hermes-skills.git
```

3. วางลงใน Terminal แล้วกด Enter
4. รอสักครู่ — ระบบจะโหลด skills ให้อัตโนมัติ
5. Restart Hermes หรือใช้ `/reload-skills`

### ⚠️ ระวัง!

❌ **ผิด:** `https://github.com/thanatkjr/kas-hermes-skills.git` (เปิด browser — ไม่ได้ติดตั้ง)

✅ **ถูก:** `hermes skills tap add https://github.com/thanatkjr/kas-hermes-skills.git` (ทั้งบรรทัด)

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