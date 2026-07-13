---
name: kas-client-knowledge-base
description: ตั้งค่าและบริหารฐานข้อมูลลูกค้ากลางบน OneDrive แชร์ ให้ทีม IA หลายคนใช้ร่วมกัน — สร้างโฟลเดอร์, template, AI สรุป dashboard อัตโนมัติทั้งรายลูกค้าและภาพรวม
tags: [kas, internal-audit, onedrive, collaboration, dashboard, knowledge-base, thai]
---

# KAS Client Knowledge Base — ฐานข้อมูลลูกค้าบน OneDrive

ตั้งค่าระบบ Shared Folder บน OneDrive ให้ทีม IA ใช้ร่วมกัน โดย Hermes AI ทำหน้าที่ประมวลผลและสร้าง Dashboard/Tracker อัตโนมัติ

## 🎯 เมื่อใช้

- ผู้ใช้ต้องการสร้าง shared workspace บน OneDrive ให้ทีม IA
- ผู้ใช้พูดถึง "ฐานข้อมูลลูกค้า", "shared folder", "ทะเบียนลูกค้า", "dashboard ลูกค้า", "KAS-Clients"
- ต้องการให้ AI สรุปข้อมูลลูกค้าจากไฟล์หลายประเภท (PDF, DOCX, XLSX, MD)
- ต้องการติดตามสถานะข้อตรวจพบ (findings tracker) ข้ามปีและข้ามบริษัท
- ต้องการ cron job อัปเดต dashboard อัตโนมัติ

## 🏗️ โครงสร้างที่ตั้งค่า

```
<KAS-Clients root>/          ← โฟลเดอร์แชร์ OneDrive (ทุกคน Edit ได้)
├── README.md                ← คู่มือให้ทีมอ่าน
├── _Templates/              ← Template ให้ทีม copy ใช้
│   ├── ข้อมูลพื้นฐาน-模板.md
│   └── findings-log.xlsx
├── _Dashboard/              ← AI สรุปภาพรวม (auto-generated)
│   └── ภาพรวมลูกค้า.md
└── <ชื่อบริษัท>/            ← 1 โฟลเดอร์ต่อ 1 ลูกค้า
    ├── ข้อมูลพื้นฐาน.md     ← น้องๆ กรอก
    ├── รายงาน/              ← อัปโหลด PDF/DOCX
    ├── ข้อตรวจพบ/
    │   └── findings-log.xlsx
    └── Dashboard-<ชื่อ>.md   ← 🤖 AI สรุปให้
```

## 📝 Workflow

### Phase 1: ตั้งค่าโครงสร้าง
1. หา OneDrive root ที่ถูกต้อง — ใช้ `search_files` หา `OneDrive*` ใต้ `$HOME`
2. สร้างโครงสร้างตามข้างบน — `mkdir -p` ทีเดียว
3. สร้าง `README.md` ที่ root: อธิบายวิธีใช้, ข้อตกลงทีม, โครงสร้าง
4. สร้าง templates ใน `_Templates/`:
   - `ข้อมูลพื้นฐาน-模板.md` — markdown template สำหรับข้อมูลบริษัท (ดู references/client-info-template.md)
   - `findings-log.xlsx` — Excel template สำหรับ log ข้อตรวจพบ (ใช้ openpyxl สร้าง, ดู scripts/create-findings-template.py)

### Phase 2: สร้าง client ตัวอย่าง
1. สร้างโฟลเดอร์ `KAS-Clients/<ชื่อบริษัท>/` พร้อม sub-folders: `รายงาน/`, `ข้อตรวจพบ/`
2. Copy `ข้อมูลพื้นฐาน-模板.md` → `ข้อมูลพื้นฐาน.md` แล้วกรอกข้อมูลสมมติที่ realistic
3. Copy `findings-log.xlsx` ไปที่ `ข้อตรวจพบ/`
4. แสดงผลโครงสร้างด้วย `find ... -type f | sort`

### Phase 3: AI สรุป Dashboard
1. อ่าน `ข้อมูลพื้นฐาน.md` ด้วย `read_file`
2. อ่าน `findings-log.xlsx` (ใช้ openpyxl ใน execute_code)
3. สร้าง `Dashboard-<ชื่อ>.md` ที่ประกอบด้วย:
   - **ภาพรวมบริษัท** — ตารางสรุป key facts
   - **พัฒนาการด้านการควบคุมภายใน** — สรุป findings trend (H/M/L) รายปี
   - **ความเสี่ยงที่ต้องติดตาม** — top risks + สถานะ
   - **สรุปข้อตรวจพบ** — open vs closed, by risk level
   - **คำแนะนำจาก AI** — insights จากข้อมูล
4. สร้าง `_Dashboard/ภาพรวมลูกค้า.md` — ตารางสรุปทุกบริษัท + high risk open findings + กำหนดการ

### Phase 4 (optional): Cron job
- สั่ง `cronjob action='create'` เพื่อ scan ทุกเช้า
- ใช้ `workdir` ชี้ไปที่ `KAS-Clients/`
- ให้ regenerate `_Dashboard/ภาพรวมลูกค้า.md`

## ⚠️ ข้อควรระวัง (Pitfalls)

- **อย่าใช้ `C:\Users\<hostname>\`** — หาโฟลเดอร์จาก `$HOME` เสมอ เพราะชื่อ user จริงอาจต่างจาก hostname
- **OneDrive อาจใช้ชื่อ `OneDrive` หรือ `OneDrive - CompanyName`** — ต้อง search ก่อน
- **Sync conflicts** — ถ้าสองคนเขียนไฟล์เดียวกัน OneDrive สร้าง conflict copy (`filename-<user>-conflict.docx`) — เตือนผู้ใช้
- **findings-log.xlsx** — ต้องใช้ `openpyxl` (ไม่ใช่ pandas) เพื่อรักษา formatting, freeze panes, autofilter
- **Thai ใน xlsx** — ใช้ฟอนต์ `Angsana New` เป็น default
- **อย่าลบไฟล์คนอื่น** — ใน README ให้ระบุข้อตกลงทีมชัดเจน

## 📎 Linked Files

- `references/client-info-template.md` — เนื้อหาเต็มของ `ข้อมูลพื้นฐาน-模板.md`
- `scripts/create-findings-template.py` — สคริปต์สร้าง `findings-log.xlsx` ด้วย openpyxl
- `references/dashboard-example.md` — ตัวอย่าง dashboard ที่ AI สร้าง (for reference)
