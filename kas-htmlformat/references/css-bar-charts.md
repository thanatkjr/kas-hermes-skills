# Pure CSS Bar Charts (Chart.js Fallback)

ใช้เมื่อ Chart.js CDN ไม่โหลด (file:// protocol, CORS, network issues) — สร้างกราฟแท่งด้วย HTML/CSS ล้วน

## Why Chart.js Fails on file://
- `file://` protocol blocks CDN fetch (CORS หรือ network restriction)
- หรือ Chart.js โหลดสำเร็จแต่ canvas มีขนาด 0px → แท่งกราฟถูกบีบอัดไปกองที่มุมซ้าย
- แก้ด้วย `setTimeout` + `resize()` อาจไม่ช่วย — ใช้ Pure CSS ดีกว่า

## Stacked Bar Chart (Relative 100%)

```html
<div class="stack-row">
  <div class="stack-col">
    <div class="stack-label">2566</div>
    <div class="stack-total">669.1 ลบ.</div>
    <div class="stack-bar-wrap">
      <div class="stack-seg" style="height:21.1%;background:#2e7d32;">กำไร 21.1%</div>
      <div class="stack-seg" style="height:24.0%;background:#ff9800;">SG&A 24.0%</div>
      <div class="stack-seg" style="height:54.1%;background:#ef5350;">ต้นทุน 54.1%</div>
    </div>
  </div>
  <!-- repeat for each year -->
</div>
```

```css
.stack-row { display: flex; }
.stack-col { flex: 1; text-align: center; }
.stack-bar-wrap { height: 260px; display: flex; flex-direction: column-reverse; border-left: 1px solid #ddd; border-bottom: 1px solid #ddd; }
.stack-seg { width: 100%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: white; }
.stack-label { font-size: 13px; font-weight: 700; margin-top: 8px; }
.stack-total { font-size: 11px; color: #757575; margin-top: 2px; }
```

## Horizontal Bar Chart (YoY Growth %)

- ใช้ `width: X%` บน `bar-fill` div — scale ตามค่า % เทียบกับค่าสูงสุด
- negative growth: ใช้สีแดง (`#c62828`) — positive: สีเขียว (`#2e7d32`)

## Comparison Bars (A vs B)

```html
<div class="cmp-row">
  <div class="cmp-label">Current Ratio</div>
  <div class="cmp-bars">
    <div class="cmp-bar" style="width:57%;background:#1565c0;">2567: 3.45</div>
    <div class="cmp-bar" style="width:100%;background:#0d47a1;">2568: 6.04 ▲</div>
  </div>
</div>
```

## Benefits
- No external dependencies — ทำงาน 100% บน file://
- Print ได้ทันที (CSS @media print)
- แก้ไขตัวเลขได้โดยตรงใน HTML
- ไม่ต้อง debug Canvas sizing
