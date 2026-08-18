# OpenCode Go Usage API — อ้างอิง

ข้อมูล provider `opencode-go` สำหรับตรวจยอดใช้งาน (usage/credit) — เก็บไว้เผื่อ rebuild tool หรือเช็คด้วยมือ

## 1. Endpoint

```
GET https://opencode.ai/zen/go/v1/usage
Authorization: Bearer <OPENCODE_GO_API_KEY>
```

คืนค่า (ตัวอย่างจริง 2026-08-18):

```json
{
  "usage": {
    "rolling": {"status": "ok", "percent": 4,  "resetsAt": "2026-08-18T05:17:48.115Z"},
    "weekly":  {"status": "ok", "percent": 12, "resetsAt": "2026-08-24T00:00:00.115Z"},
    "monthly": {"status": "ok", "percent": 6,  "resetsAt": "2026-09-16T15:42:16.115Z"}
  }
}
```

## 2. ความหมายแต่ละ field

| field | ความหมาย |
|---|---|
| `percent` | % ของโควตาในกรอบเวลานั้น **ที่ใช้ไปแล้ว** (เพิ่มขึ้นตามการใช้งาน) |
| `status` | `"ok"` = ยังไม่เกิน limit (ค่าอื่น = เกิน/ใกล้ถึง) |
| `resetsAt` | เวลารีเซ็ตโควตา (ISO 8601 UTC — ใช้ `.replace("Z","+00:00")` แล้ว `.astimezone()` เพื่อแปลงเป็นเวลาท้องถิ่น) |

- `rolling` = โควตารอบ 5 ชั่วโมง (ตรงกับ "Requests per 5 hour" บนหน้า opencode.ai/go)
- `weekly` / `monthly` = โควตารายสัปดาห์ / รายเดือน (กรอบใหญ่กว่า limit ต่างกัน — % เทียบกับ limit ของแต่ละกรอบ)
- "ยอดคงเหลือ" = `100 - percent` (เป็นการตีความเอง — API ไม่ได้คืนค่าคงเหลือตรง ๆ)

## 3. ลักษณะแผน OpenCode Go

- Subscription **$10/เดือน** ($5 เดือนแรก) — **ไม่ใช่ credit balance** แบบเติมเงิน
- จำกัดจำนวน request ต่อกรอบเวลา **ต่อโมเดล** (เช่น DeepSeek V4 Pro ≈ 3,200 req/5 ชม., GLM-5.2 ≈ 1,050, MiniMax M3 ≈ 4,100)
- ไม่มี endpoint ที่คืนยอดเครดิตเป็นตัวเลข — ลองแล้วมีแค่ `/usage` (ส่วน `/billing`, `/credits`, `/account`, `/me`, `/api/usage` = หน้า SPA HTML ไม่ใช่ JSON API)
- `GET /v1/models` = ดูรายชื่อ model ที่เปิดให้บริการ (deepseek-v4-pro, glm-*, kimi-*, qwen-*, minimax-*, mimo-*, gpt-5.6-luna, hy3 …)

## 4. ⚠️ CORS — สำคัญ

`/usage` **ไม่ส่ง `Access-Control-Allow-Origin`** → fetch จาก browser (origin ใด ๆ รวมถึง file://) ถูก block อ่าน response ไม่ได้ (curl/urllib ฝั่ง server ไม่ติด CORS)

→ ต้องใช้ **local proxy ฝั่ง Python**: เซิร์ฟเวอร์ fetch ให้ แล้วส่งต่อให้ browser โดยเติม `Access-Control-Allow-Origin: *`

key อยู่ฝั่ง server เท่านั้น — ไม่ถูกส่งให้ browser

## 5. Tool ที่สร้างแล้ว

โฟลเดอร์ `C:\Users\ASUS\opencode-balance\`

| ไฟล์ | หน้าที่ |
|---|---|
| `opencode_balance.py` | stdlib-only, 2 โหมด: `widget` / `server` |
| `start_widget.bat` | เปิด widget ลอยจอ (pythonw, ไม่มี console) |
| `start_web.bat` | เปิด server + browser |
| `README.md` | วิธีใช้ + IP มือถือ |

- `widget` = tkinter always-on-top frameless draggable, รีเฟรช 60 วิ, แถบสี 3 อัน + "คงเหลือ X%" + รีเฟรช/ปิด
- `server` = http.server bind `0.0.0.0:8899`, serve dashboard + `/api/usage` proxy → มือถือเข้าผ่าน `http://<LAN_IP>:8899` (WiFi เดียวกัน)
- อ่าน key จาก `~/AppData/Local/hermes/.env` (`OPENCODE_GO_API_KEY=`) — fallback ใช้ env var

## 6. Reusable patterns (stdlib ล้วน ไม่ต้อง pip install)

- **tkinter widget ลอยจอ:** `root.overrideredirect(True)` + `root.attributes("-topmost", True)` + bind `<ButtonPress-1>`/`<B1-Motion>` ลากย้าย (bind ที่ title bar เท่านั้น กันชนกับปุ่ม)
- **refresh ไม่ block UI:** worker thread (fetch) → `root.after(0, callback)` กลับมาแก้ widget บน main thread + guard flag `busy` กัน fetch ซ้อน
- **proxy สำหรับ CORS-blocked API:** `http.server.BaseHTTPRequestHandler` + `urllib.request` fetch server-side, endpoint `/api/*` เติม `Access-Control-Allow-Origin: *` + `Cache-Control: no-store`
- **หา LAN IP:** `socket.socket(AF_INET, SOCK_DGRAM)` connect 8.8.8.8 → `getsockname()[0]`
- **HTTP server เงียบ:** override `log_message` เป็น `pass`

## 7. ข้อควรระวัง

- เปิด server ครั้งแรก Windows Firewall จะถาม → กด Allow (Private network) ไม่งั้นมือถือเข้าไม่ได้
- Widget/Server ที่ spawn จาก Hermes terminal session จะถูก kill เมื่อ session จบ — ใช้งานจริงต้องเปิดผ่าน `.bat` เอง
- Python 3.11 (`python`) กับ 3.14 (`python3`) มีทั้งคู่บนเครื่อง — ใช้ `python` (3.11) สำหรับ tkinter; `pythonw` ใช้เปิด widget แบบไม่มี console
