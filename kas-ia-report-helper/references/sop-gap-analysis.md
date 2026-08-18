# SOP Gap Analysis Methodology

ใช้เมื่อผู้ใช้ต้องการตรวจสอบว่า SOP/นโยบายที่ Consult เขียน ครอบคลุม key controls ตาม Master Context ครบถ้วนหรือไม่ และตรวจสอบว่ารีวิวเวอร์ (น้อง) จับ gap ได้ครบหรือไม่

## Trigger

- "ตรวจสอบ SOP เทียบกับ Master Context"
- "review policy documents against control framework"
- "หา gap ระหว่าง SOP กับ Master Context"
- "ตรวจงานน้องที่ review SOP"

## Core Principles

1. **SOP เป็นตัวตั้งทางซ้าย** — ใช้ SOP เป็นหลักในการ mapping กลับไปหา Master Context (ห้ามใช้ MC เป็นตัวตั้ง)
2. **Cross-cutting processes ห้ามแยก** — กรอบอำนาจอนุมัติ (approval), บริหารสัญญา (contracts), รายการที่เกี่ยวโยงกัน (RPT), ประชุมผู้บริหาร (management) — กระบวนการเหล่านี้ถูก embed อยู่ใน SOP แต่ละฉบับอยู่แล้ว ไม่ต้องทำเป็นหัวข้อแยก
3. **Key controls ต้องมีใน SOP** — ไม่จำเป็นต้องเหมือน 100% แต่ key control ที่ระบุใน MC ต้องปรากฏใน SOP (หรือมี substitute control)
4. **ห้ามแต่งเอง ห้ามมโน** — ต้องอ่าน MC และ SOP โดยละเอียด การแก้ไขต้องระบุหัวข้อย่อยและประโยคที่ต้องแก้

## Methodology: 3-Layer Deep Dive

### Layer 1: Map SOP → Master Context
```
SOP sub-process (e.g., D101) → MC process (e.g., fixedAssets) → MC steps
```
- ระบุว่าแต่ละ SOP sub-process ตรงกับ MC process ไหน
- เช็คว่า SOP มีกระบวนการย่อยอะไรบ้าง (D101, E102, etc.)
- MC มีกี่ขั้นตอน แต่ละขั้นตอนต้องการอะไร

### Layer 2: Compare Control-by-Control
```
For each MC Step:
  ├── MC Control: (สิ่งที่ควรมี)
  ├── SOP Mapping: (มีใน SOP จุดไหน — D101, ❌ไม่มี, มีบางส่วน)
  └── Reviewer Status: (⚠️ จับได้ / 🔴 พลาด / — ไม่เกี่ยวข้อง)
```
ใช้ตารางเปรียบเทียบทีละ MC Step เพื่อให้เห็นภาพชัดเจน

### Layer 3: Pattern Recognition
- **Individual gaps** (รายจุด): เอกสาร missing, control missing รายข้อ — รีวิวเวอร์มักจับได้
- **Structural gaps** (เชิงโครงสร้าง): ทั้งกลุ่มกิจกรรมที่หายไปจาก SOP — รีวิวเวอร์มักพลาด

## Output Format (Restructured OAI Review)

```markdown
## 1. ชื่อเอกสาร SOP: [ชื่อ SOP]
### 1.1 [ชื่อการควบคุมที่ขาดจาก MC]
**ขั้นตอนปฏิบัติงานที่ควรเพิ่ม:**
- ควรเพิ่มใน SOP หัวข้อ [ระบุหัวข้อย่อย] ประโยค/ย่อหน้าที่ว่า "[ระบุประโยคเดิม]" โดยเพิ่ม "[ระบุข้อความใหม่]"

**เอกสารสำคัญที่ควรเพิ่ม:**
- [ชื่อเอกสาร] — ควรระบุใน SOP หัวข้อ [ระบุตำแหน่ง]
```

## Common Pitfalls

1. **ใช้ MC เป็นตัวตั้ง** → ต้องกลับด้าน ใช้ SOP เป็นตัวตั้ง
2. **แยก cross-cutting processes** → ประกาศตั้งแต่ต้นว่ากระบวนการไหนเป็น cross-cutting และจะไม่แยกวิเคราะห์
3. **อ่านแต่ OAI Review โดยไม่อ่าน SOP ต้นฉบับ** → ต้องอ่าน SOP จริงเทียบกับ MC จริงถึงจะเจอ gap ที่รีวิวเวอร์พลาด
4. **ภาษาที่ใช้ใน OAI Review** → หลีกเลี่ยงภาษาไม่เป็นทางการ คำถามปนข้อเสนอแนะ ให้ใช้ภาษาเป็นทางการและแยกส่วนชัดเจน

## Mapping Reference: Common SOP → MC Mappings

| SOP | MC Process |
|-----|-----------|
| Fixed Asset | fixedAssets |
| HR & Payroll | hr |
| Petty Cash + Cash Advance | pettyCash |
| Procurement + Inventory | procurePay |
| Sales & Revenue | salesGov + salesPrivate |
| IT | itgc + pdpa |
| Installation & O&M | installOm |
| Budget | management (partial) |
| R&D | (cross-cutting, embedded in installOm/sales) |
| Cost | (cross-cutting, embedded in procurePay/management) |
