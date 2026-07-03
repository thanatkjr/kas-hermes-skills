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

### 🔥 Double-click จบ! (ง่ายสุด)

1. ดาวน์โหลด [`install.bat`](https://raw.githubusercontent.com/thanatkjr/kas-hermes-skills/master/install.bat) ไปไว้ที่ Desktop
2. **Double-click** `install.bat`
3. รอจนขึ้น `ติดตั้งแล้ว 3 skills`
4. Restart Hermes หรือใช้ `/reload-skills`

### 🔄 เมื่อมีอัปเดต

Double-click `install.bat` อีกครั้ง — ระบบจะ pull เวอร์ชั่นล่าสุดจาก GitHub แล้วติดตั้งให้อัตโนมัติ

> 💡 ไม่ต้องแก้ `install.bat` ใหม่เมื่อเพิ่ม skill! มันจะหา SKILL.md **ทั้งหมด** ใน repo เอง

---

## 📁 โครงสร้าง Repo

```
├── install.bat                ← Double-click ติดตั้ง!
├── README.md
├── kas-master-context/
│   ├── SKILL.md
│   └── references/
├── kas-model-routing/
│   └── SKILL.md
└── productivity/
    └── kas-ia-report-helper/
        └── SKILL.md
```