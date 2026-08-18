# RCM Database — Full Schema Reference

โครงสร้างข้อมูลที่สมบูรณ์ของ RCM Database (MCP Cloudflare) — ใช้เป็น reference เวลาดึงข้อมูลจาก `get_process_rcm`, `get_activity`, หรือ `get_risk_detail`

> Source: MCP Cloudflare `rcm-mcp-server.thanatkjr.workers.dev`
> DB Version: 4 | Updated: 2026-08-17
> Totals: 10 processes, 848 activities, 3,502 risks, 7,435 controls, 14,894 tests

---

## Data Hierarchy

```
DATABASE (1 JSON file)
└── PROCESS (10: R, P, IC, OP, ELC, AF, FA, HR, IT, SHE)
    └── ACTIVITY (848 total)
        ├── activity_code       : string  (e.g., "R-ELEC-001")
        ├── process_code        : string  (e.g., "R")
        ├── activity_name       : string  (Thai)
        ├── sector_code         : string  (UNVS, ELEC, MACH, FOOD, etc.)
        ├── risk_scan[12]       : array   ← 12-category presence grid
        └── risks[]             : array
            ├── risk_code       : string  (e.g., "R-ELEC-001.R1")
            ├── activity_code   : string
            ├── risk_name       : string  (Thai)
            ├── risk_category   : string  (12 categories)
            ├── poison          : string  (โลภะ | โทสะ | โมหะ)
            ├── indicator_code  : string
            ├── indicator_name  : string  (KRI description)
            ├── validation_code : string
            ├── validations[]   : array of {code, text}
            ├── policy_code     : string
            ├── policies[]      : array of {code, text}
            ├── procedure_code  : string
            ├── procedures[]    : array of {code, text}
            ├── report_code     : string
            ├── report_name     : string
            └── controls[]      : array
                ├── control_code       : string
                ├── risk_code          : string
                ├── control_name       : string  (Thai)
                ├── control_category   : string  (Authorisation, Segregation of Duties, etc.)
                ├── control_method     : string  (Manual Control, System Control, etc.)
                ├── control_nature     : string  (Preventive, Detective, Corrective)
                ├── question_code      : string
                ├── question_text      : string  (Thai — interview question)
                └── tests[]            : array of {test_code, test_name}
```

---

## 🔴 CRITICAL: Tests & Questions are at CONTROL level, NOT risk level

```python
# ❌ WRONG — will always return empty
for risk in activity["risks"]:
    tests = risk.get("tests", [])        # → []
    questions = risk.get("questions", []) # → []

# ✅ CORRECT — iterate controls inside each risk
for risk in activity["risks"]:
    for control in risk["controls"]:
        tests = control["tests"]          # → [{test_code, test_name}, ...] (2 per control)
        question = control["question_text"] # → string (1 per control)
```

---

## 12 Risk Categories (risk_scan grid)

Every activity has a `risk_scan` array scanning for presence of 12 risk types:

| # | Category | Status Values | Thai Note |
|---|----------|---------------|-----------|
| 1 | Operational Risk | มี / N/A | |
| 2 | Reporting Risk | มี / N/A | |
| 3 | Compliance Risk | มี / N/A | |
| 4 | Fraud Risk | มี / N/A | |
| 5 | Technology Risk | มี / N/A | |
| 6 | Customer Risk | มี / N/A | |
| 7 | Reputational Risk | มี / N/A | |
| 8 | Human Resource Risk | มี / N/A | |
| 9 | Supply Chain Risk | มี / N/A | |
| 10 | Strategic Risk | มี / N/A | |
| 11 | Financial Risk | มี / N/A | |
| 12 | Emerging Risk | มี / N/A | |

N/A entries have `risk_code: null` and a note like "ไม่ใช่ความเสี่ยงต้นทางที่ material ของกิจกรรมนี้"

---

## Poison Values

3 ค่าเท่านั้น — **ไม่มี Active/Passive/polarity** (ตาม OKAS QC Guard R5):

| Value | Meaning | สีใน UI |
|-------|---------|---------|
| โลภะ | ความอยากได้ (Greed) | 🟡 ส้มอ่อน |
| โทสะ | ความโกรธ/ไม่พอใจ (Aversion) | 🔴 แดง |
| โมหะ | ความหลง/ไม่รู้ (Delusion) | ⚫ ม่วง |

---

## Sector Codes (used with `get_process_rcm`)

> ⚠️ DB v4 มี **31 sector codes** (นับรวม UNVS) — ตารางเก่า (v2) มีแค่ 14 codes และมี typo `LOGY`→`LOGI` อย่าใช้อ้างอิง
> ✅ **ชื่อไทย confirm แล้ว** (Admin: Thanat, 2026-08-17) — mapping code → ชื่อไทย + 9 หมวด ดูได้ที่ `references/sector-codes.md`
> ไม่มี field `sector_name` ใน DB — มีแค่ `sector_code` (code สั้น) → ชื่อไทยต้อง mapping จาก sector-codes.md

| Code | Activities | Code | Activities |
|------|:----------:|------|:----------:|
| UNVS | 292 | PERS | 20 |
| HLTH | 33 | CONS | 19 |
| TOUR | 30 | INSU | 19 |
| ENGY | 27 | MINE | 19 |
| FOOD | 25 | FRAN | 18 |
| GOVT | 23 | PROP | 18 |
| LOGI | 23 | AGRI | 17 |
| MEDA | 22 | MACH | 17 |
| AUTO | 21 | PACK | 16 |
| PETR | 21 | SECU | 15 |
| REIT | 21 | FASH | 15 |
| BANK | 20 | COMM | 14 |
| | | PAPR | 14 |
| | | ELEC | 13 |
| | | PROF | 13 |
| | | ICT | 12 |
| | | STEL | 12 |
| | | CMAT | 11 |
| | | HOME | 8 |

หมายเหตุ: `sector_code` ปรากฏใน field ของ activity object (`get_process_overview` คืนแค่ 4 field: `activity_code`, `activity_name`, `sector_code`, `risks`). ไม่มี MCP tool ชื่อ `list_sectors` — ใช้ `references/sector-codes.md` (31 codes + ชื่อไทย + 9 หมวด) ได้เลย ไม่ต้อง derive ใหม่ทุกครั้ง

---

## MCP Tools Coverage

| Tool | Returns | Notes |
|------|---------|-------|
| `get_process_rcm` | Activity → Risk → Control → Test + Question | **Best for bulk RCM** — one call per process+sector. Includes all risk-level fields (poison, indicator, policies, procedures, validations, report) |
| `get_activity` | Single activity with full tree | Use when you need one specific activity |
| `get_risk_detail` | Single risk with all sub-fields | Use for deep-dive on specific risk |
| `get_process_overview` | Activity list (codes + names) | Lightweight — use for browsing |
| `search_risks` | Risk search results | Keyword search across all risks |

---

## Coverage Guarantees (verified 2026-08-09, 1,294 risks)

| Field | Coverage | Notes |
|-------|:--------:|-------|
| `poison` | 100% | Every risk has one of 3 values |
| `indicator_name` | 100% | KRI present for all risks |
| `validations` | 100% | 2 items per risk |
| `policies` | 100% | 2 items per risk |
| `procedures` | 100% | 2 items per risk |
| `report_name` | 100% | Report name present for all risks |
| `controls[].tests` | 100% | 2 tests per control |
| `controls[].question_text` | 100% | 1 question per control |
