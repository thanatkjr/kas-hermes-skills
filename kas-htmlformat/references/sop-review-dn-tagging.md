# SOP Review D/N Tagging System

ใช้กับ SOP Gap Analysis HTML — ระบุว่าแต่ละ gap ถูกพบโดยใคร

## Tag Definitions

| Tag | ความหมาย | ใช้เมื่อ |
|-----|---------|--------|
| **(D)** | Duplicate | Gap นี้ถูกพบใน OAI Review ของน้องด้วย (ซ้ำกัน) |
| **(N)** | New | Gap นี้ถูกเพิ่มโดย KAS Team — น้องไม่ได้ระบุใน OAI Review |

## Format

Tag ต่อท้ายชื่อ gap ใน slide title:

```
2.1 Gap — Asset Requisition & Budget Check (D)
2.4 Gap — Depreciation Review Process (N)
```

สำหรับ paired slides (2 gaps ใน 1 slide):

```
2.6–2.7 Gap — IT Data Destruction (D) | Project Asset Classification (N)
```

## Cross-Reference Process

### Phase 1: Match AI gaps กับ OAI Review

1. อ่าน OAI Review markdown → parse section headers + bullet items
2. แยกตาม SOP โดยใช้ SOP name mapping
3. สำหรับแต่ละ gap ของ AI:
   - เทียบ keywords กับ reviewer items
   - ถ้า match ≥2 keywords → **(D)**
   - ถ้าไม่ match → **(N)**

### Phase 2: Add Reviewer-only Items

1. ตรวจสอบ reviewer items ที่ไม่มีใน AI gaps
2. เพิ่มเป็น gap ใหม่ ติด **(N)** — เป็นข้อที่ AI ไม่ได้ระบุแต่แรก
3. ใส่ reference `📌 OAI Review — [reviewer code]: [reviewer title]`

### Phase 3: Generate v2 HTML

1. ใช้ template extraction จากไฟล์ v1 (gold standard)
2. แทนที่ gap titles ด้วยชื่อสั้น + (D)/(N)
3. Clean labels: `การควบคุมทดแทน` (ห้าม emoji, ห้าม English)
4. ต่อท้ายไฟล์ด้วย appendix gaps (reviewer-only items)
5. Save เป็น `-v2.html`

## Example: SOP 03 Fixed Asset

| Gap | Tag | OAI Match |
|-----|-----|-----------|
| 2.1 Asset Requisition & Budget Check | D | D101 ✅ |
| 2.2 Project Code in Register | D | D101 ✅ |
| 2.3 Variance Approval | D | D103 ✅ |
| 2.4 Depreciation Review | N | — |
| 2.5 Warranty Check | D | D107 ✅ |
| 2.6 IT Data Destruction | D | D104 ✅ |
| 2.7–2.11 Project Asset Management | N | — |
| 2.12 Periodic Asset Movement Report | N | D102 (reviewer-only) |
| 2.13 Fixed Asset Disposal Summary | N | D105 (reviewer-only) |

## Pitfalls

- **อย่าใช้ W/N** — user เปลี่ยนเป็น D/N (Duplicate/New) เพราะ W ไม่สื่อความหมาย
- **อย่าใส่ tag ใน badge** — tag ต้องอยู่ใน title text ไม่ใช่ใน `<span class="badge">`
- **Appendix ไม่ควรแยก** — reviewer-only items ควรเป็น gap ปกติ (2.12, 2.13) ไม่ใช่ appendix แยก
- **Substitute Control label ต้องสะอาด** — `การควบคุมทดแทน` ไม่ใช่ `🔄 การควบคุมทดแทน (Substitute Control)`