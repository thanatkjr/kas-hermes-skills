---
name: kas-markitdown
description: "Use when user uploads or attaches any file (PDF, DOCX, PPTX, XLSX, HTML, images, audio) — smart-convert to Markdown with the optimal engine per format. PDF: pymupdf for Thai (clean, no artifacts) + OCR fallback for scans. Office: markitdown. Images: OCR. Token-efficient. KAS skill."
version: 2.0.0
author: KAS (Kandit Advisory Services)
license: MIT
metadata:
  hermes:
    tags: [file-conversion, markitdown, pymupdf, ocr, tesseract, token-saving, document-processing, KAS]
    related_skills: [token-efficient, kas-guard]
---

# KAS Smart File → Markdown Converter

แปลงไฟล์ที่ user upload/แนบเป็น Markdown ด้วย engine ที่เหมาะสมที่สุดต่อรูปแบบ — **pymupdf สำหรับ PDF (ภาษาไทยสะอาด ไม่มี cid artifacts)**, markitdown สำหรับ Office, OCR สำหรับรูปภาพและ PDF scan

## Overview

Skill นี้ใช้ **smart routing** — เลือก engine ที่ดีที่สุดตามประเภทไฟล์ ไม่ใช่ one-size-fits-all:

| ฟอร์แมต | Engine | คุณภาพ | เหตุผล |
|---------|--------|:---:|------|
| **PDF (text)** | pymupdf | 95% | ไทยสะอาด ไม่มี (cid:xxx) artifacts |
| **PDF (scan)** | pymupdf + tesseract OCR | 70-85% | OCR ภาษาไทย+อังกฤษ |
| **DOCX** | markitdown | 90-95% | mammoth backend — โครงสร้างดี |
| **XLSX** | markitdown | 85-90% | ได้ตาราง แต่เสียสูตร |
| **PPTX** | markitdown | 70-80% | ได้ข้อความ เสีย layout |
| **HTML** | markitdown | 95% | ข้อความ+ลิงก์ |
| **Images** | pytesseract OCR | 70-85% | ไทย+อังกฤษ |
| **Audio** | markitdown | 60-80% | speechrecognition transcribe |

## When to Use

**ใช้ทันทีเมื่อ user แนบไฟล์ที่ไม่ใช่ plain text:**
- `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`
- `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff` (OCR)
- `.mp3`, `.wav`, `.m4a` (transcribe)
- `.zip` (extract แล้วแปลงทีละไฟล์)

**ไม่ต้องใช้กับ:**
- Plain text: `.txt`, `.md`, `.py`, `.js`, `.ts`, `.yaml`, `.yml`, `.json`, `.toml`, `.cfg`, `.ini`, `.env` → `read_file` โดยตรง
- ไฟล์ที่ใช้ `vision_analyze` ดีกว่า (เช่น รูปภาพที่ต้องการวิเคราะห์ layout/สี/องค์ประกอบ — ไม่ใช่ OCR)

## How It Works

```
User uploads file
       │
       ▼
smart_convert.py (scripts/smart_convert.py)
       │
       ├── .pdf ──→ pymupdf extract text
       │              ├── chars/page ≥ 50 → TEXT-BASED → pymupdf (clean Thai!) ✅
       │              └── chars/page < 50 → SCANNED → tesseract OCR 🔍
       │
       ├── .docx, .pptx, .xlsx, .html → markitdown ✅
       │
       ├── .png, .jpg, .bmp, .tiff → pytesseract OCR 🔍
       │                                 └── fallback: markitdown (EXIF)
       │
       └── .mp3, .wav, .m4a → markitdown (transcribe)
       │
       ▼
Output: <filename>.md → read with read_file
```

## Usage (Step-by-Step)

### Step 1: Run the smart converter

ใช้ `execute_code` รัน script — **ห้ามใช้ `read_file` กับไฟล์ binary โดยตรง**

```python
import subprocess, json, os

# Set PATH for tesseract (Windows)
env = os.environ.copy()
env["PATH"] = env.get("PATH", "") + r";C:\Program Files\Tesseract-OCR"

script = r"C:\Users\ASUS\AppData\Local\hermes\skills\productivity\kas-markitdown\scripts\smart_convert.py"

result = subprocess.run(
    ["python", script, r"path/to/file.pdf"],
    capture_output=True, text=True, env=env, timeout=120
)
info = json.loads(result.stdout)
print(json.dumps(info, ensure_ascii=False, indent=2))
```

### Step 2: Read the converted Markdown

```python
# ✅ CORRECT: read converted .md
read_file(info["output_path"], offset=1, limit=200)

# ❌ WRONG: read raw PDF/DOCX — NEVER
read_file("path/to/file.pdf")
```

### Step 3 (optional): Vision analysis for images

ถ้า user ต้องการวิเคราะห์ layout/สี/องค์ประกอบของรูปภาพ (นอกเหนือจาก OCR):
- ใช้ `vision_analyze` โดยตรงกับไฟล์รูปต้นฉบับ
- OCR เหมาะสำหรับ *อ่านข้อความ* จากรูป — ไม่ใช่การวิเคราะห์ visual

## Quick Decision Reference

```
ไฟล์แนบ → ดูนามสกุล:
  ├── .pdf                    → smart_convert.py (pymupdf ± OCR)
  ├── .docx, .pptx, .xlsx     → smart_convert.py (markitdown)
  ├── .html                   → smart_convert.py (markitdown)
  ├── .png, .jpg, .bmp, .tiff → smart_convert.py (OCR)
  ├── .mp3, .wav, .m4a        → smart_convert.py (transcribe)
  ├── .zip                    → smart_convert.py (extract+convert)
  └── .txt, .md, .py, .js, ... → read_file โดยตรง (plain text)
```

## Key Advantages

| markitdown-only | KAS-markitdown (smart routing) |
|---|---|
| PDF ไทย: 290 cid artifacts ❌ | PDF ไทย: **0 artifacts** ✅ |
| PDF scan: แทบไม่ได้ข้อความ | PDF scan: **OCR อัตโนมัติ** ✅ |
| รูปภาพ: EXIF metadata | รูปภาพ: **OCR ไทย+อังกฤษ** ✅ |
| One-size-fits-all | **เลือก engine ที่ดีที่สุดต่อฟอร์แมต** |

## Dependencies

ติดตั้งครั้งเดียว:

```bash
uv pip install "markitdown[all]" pymupdf pytesseract pillow

# Windows: ติดตั้ง Tesseract OCR engine
winget install UB-Mannheim.TesseractOCR --accept-package-agreements
```

Script จะ auto-check และติดตั้ง dependencies ที่ขาดเอง

## Common Pitfalls

1. **อ่าน raw PDF/DOCX ด้วย read_file** — เสีย token มหาศาล รัน smart_convert.py ก่อนเสมอ
2. **ลืม set PATH สำหรับ tesseract** — บน Windows ต้องเพิ่ม `C:\Program Files\Tesseract-OCR` ใน PATH
3. **OCR ภาษาไทยไม่ได้** — ต้องมี `tha.traineddata` ใน `C:\Program Files\Tesseract-OCR\tessdata\` (มากับ installer แล้ว)
4. **markitdown 0.1.6 → 0.1.5** — `[all]` dependencies อาจ downgrade markitdown แต่ไม่มีผลต่อฟีเจอร์ที่ใช้
5. **แปลง PDF scan แต่ไม่ได้ OCR** — ระบบจะตรวจจับอัตโนมัติ (chars/page < 50) และใช้ OCR แทน
6. **ไฟล์ใหญ่ (>50MB)** — OCR อาจใช้เวลานาน แสดงความคืบหน้าให้ user ทราบ

## Verification Checklist

- [ ] `smart_convert.py` รันสำเร็จ — ได้ JSON output พร้อม output_path
- [ ] `output_chars > 0` — มีเนื้อหาจริง ไม่ใช่ empty
- [ ] PDF: `method` เป็น `pymupdf` (text-based) หรือ `pymupdf-ocr` (scanned)
- [ ] DOCX/XLSX/PPTX: `method` เป็น `markitdown`
- [ ] `read_file` ใช้กับ .md output — **ไม่ใช้กับไฟล์ต้นฉบับ**
