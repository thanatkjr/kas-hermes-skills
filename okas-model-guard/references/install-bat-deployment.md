# install.bat Deployment Pattern

> อัปเดต: 14 Aug 2026 — v3.0 (ไม่พึ่ง openrouter — opencode-go + Google key)

## What install.bat Does Beyond Skill Copying

Since v2, `install.bat` performs 3 post-install steps automatically:

### 1. Path Auto-Fix (PowerShell)
```batch
:: แทนที่ C:\Users\ASUS → %USERPROFILE% ในทุก SKILL.md
powershell -ExecutionPolicy Bypass -File fixskill.ps1
```
เหตุผล: SKILL.md มี hardcoded paths จากเครื่องพี่ (ASUS) → ต้อง auto-replace ให้ตรงกับเครื่องน้องแต่ละคน

### 2. Hermes Config Auto-Set
```batch
hermes config set model.provider opencode-go
hermes config set model.default deepseek-v4-pro
hermes config set moa.enabled false
hermes config set auxiliary.vision.provider gemini
hermes config set auxiliary.vision.model gemini-3.6-flash
hermes config set auxiliary.web_extract.provider opencode-go
hermes config set auxiliary.web_extract.model deepseek-v4-pro
hermes config set delegation.provider opencode-go
hermes config set delegation.model deepseek-v4-pro
```
เหตุผล:
- `model.provider=opencode-go` + `model.default=deepseek-v4-pro` — main model หลัก (subscription)
- `moa.enabled=false` — ปิด Mixture of Agents (ป้องกัน AI ตอบช้า + ลดค่าใช้จ่าย 3-5x)
- `vision=gemini native + gemini-3.6-flash` — ใช้ Google key ตรง ไม่ต้องมี openrouter
- `delegation=opencode-go + deepseek-v4-pro` — subagent ใช้ subscription ตัวเดิม
- `web_extract=opencode-go + deepseek-v4-pro` — สกัดเว็บใช้ subscription

⚠️ **Key ที่ต้องมี:**
- `OPENCODE_GO_API_KEY` — subscription OpenCode Go
- `GOOGLE_API_KEY` — search + vision (⚠️ ต้องชื่อ `GOOGLE_API_KEY` ไม่ใช่ `GOOGLE_AI_API_KEY`)

### 3. Skill Name Cleanup
ลบ skills เก่าที่เปลี่ยน prefix (xkas-* ทั้งหมด, kas-* → okas-*)

## เมื่อต้องเพิ่ม Config ใหม่

ถ้ามี model/capability ใหม่ที่ต้องการให้ทุกคนใช้งาน → เพิ่มใน install.bat step [3.5/4]:
```batch
hermes config set <key> <value> 2>nul
```

## เมื่อต้องเพิ่ม Path Fix ใหม่

เพิ่มใน PowerShell `$replacements` array:
```powershell
$replacements = @(
    @{old='C:\Users\ASUS'; new=$userPath}
    # เพิ่มเพิ่มที่นี่
)
```

## Verification

หลังจากรัน install.bat → เช็คด้วย:
```bash
hermes config get model.provider     # opencode-go
hermes config get model.default      # deepseek-v4-pro
hermes config get moa.enabled        # ต้องเป็น false
hermes config get auxiliary.vision.provider  # gemini
hermes config get delegation.provider  # opencode-go
```
