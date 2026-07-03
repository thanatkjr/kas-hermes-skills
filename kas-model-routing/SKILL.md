---
name: kas-model-routing
description: "ตั้งค่า model routing: DeepSeek V4 Pro เป็นหลัก, Gemini Flash สำหรับ PDF/vision/delegation — ประหยัดค่าใช้จ่าย 97% สำหรับงานอ่านเอกสาร"
version: 1.0.0
author: Thanat
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [setup, model, cost-saving, routing]
---

# KAS Model Routing Setup (v3)

ตั้งค่าให้ Hermes เลือก model อัตโนมัติตามประเภทงาน:

| # | งาน | Model | ราคา/1M tok | เพราะ |
|---|---|---|---|---|
| 1 | ถามตอบทั่วไป | DeepSeek V4 Pro | $2/$8 | Q&A สั้น ต่างกันแค่เซ็นต์ |
| 2 | Slide/Infographic/Dashboard | **Gemini 2.5 Pro** | $1.25/$10 | ดีไซน์สวย ถูกกว่า Claude |
| 3 | อ่าน PDF/รูป → ทำต่อ | PDF:pymupdf → **DeepSeek V4 Pro** / Vision:Gemini Flash | $0 → $2/$8 | สกัดฟรี+วิเคราะห์ Pro |
| 4 | RCM / Audit Report | **DeepSeek V4 Pro** | $2/$8 | วิเคราะห์ภาษาไทยดี |
| 5 | Coding | **DeepSeek V4 Pro** | $2/$8 | โค้ดเก่ง ถูกกว่า Claude |

## Setup

```bash
hermes config set delegation.model google/gemini-2.5-pro
hermes config set delegation.provider openrouter
hermes config set auxiliary.vision.model google/gemini-2.5-flash
hermes config set auxiliary.vision.provider openrouter
```

จากนั้น `/reset`

## Prerequisites

- `OPENROUTER_API_KEY` ใน `.env`
- `model.provider: moa`
- `model.default: deepseek/deepseek-v4-pro`