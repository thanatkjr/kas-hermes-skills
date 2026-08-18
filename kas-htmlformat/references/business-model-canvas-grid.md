# Business Model Canvas — CSS Grid Layout

ใช้สร้าง Business Model Canvas 1 หน้าแบบ infographic ด้วย CSS Grid 5 คอลัมน์ 9 กล่อง

## Grid Structure

```
┌────────────────── HEADER (full width) ──────────────┐
│ 1.Partners │ 2.Activities │ 3.Value Prop │ 4.Customers │ 5.Revenue │
│            ├──────────────┤              ├─────────────┼───────────┤
│            │ 2.Resources  │              │ 4.Channels   │ 5.Cost    │
├────────────┴──────────────┴──────────────┴─────────────┴───────────┤
│                        FOOTER (2 cols)                              │
└────────────────────────────────────────────────────────────────────┘
```

## CSS Grid Setup

```css
.canvas {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
  grid-template-rows: auto auto auto auto auto auto;
  gap: 10px;
  padding: 16px;
  max-width: 1400px;
  margin: 0 auto;
}
```

**⚠️ CRITICAL PITFALL: ห้ามใช้ `height: 98vh` หรือ `overflow: hidden` บน .canvas หรือ .block**
- `height: 98vh` → เนื้อหาที่เกิน viewport ถูกบีบและตัด
- `overflow: hidden` → ข้อความถูกตัดโดยไม่แสดง scrollbar
- **ใช้ `auto` rows และให้ content กำหนดความสูงเอง** — Grid จะขยายตามเนื้อหา

## Block Placement

```css
.block-header    { grid-column: 1; grid-row: 2; }
.block-partner   { grid-column: 1; grid-row: 3 / 5; }  /* spans 2 rows */
.block-activities { grid-column: 2; grid-row: 2 / 4; }
.block-resources  { grid-column: 2; grid-row: 4 / 6; }
.block-value      { grid-column: 3; grid-row: 2 / 6; }  /* center, spans 4 rows */
.block-customer   { grid-column: 4; grid-row: 2 / 4; }
.block-channel    { grid-column: 4; grid-row: 4 / 6; }
.block-revenue    { grid-column: 5; grid-row: 2 / 4; }
.block-cost       { grid-column: 5; grid-row: 4 / 6; }
.block-footer     { grid-column: 1 / 3; grid-row: 6; }
```

## Color Coding by Column

ใช้ `border-top: 4px solid <color>` และ header `border-bottom: 3px solid <color>`:

| Column | Color | Hex |
|--------|-------|-----|
| Partners | Orange | #e65100 |
| Activities | Blue | #1565c0 |
| Resources | Green | #2e7d32 |
| Value Prop | Purple | #6a1b9a |
| Customers | Red | #c62828 |
| Revenue | Green | #2e7d32 |
| Cost | Red | #c62828 |

## Highlight Boxes

ใช้เน้นข้อมูลสำคัญภายในกล่อง:
```html
<div class="highlight hl-green">
  <b>รายได้รวมปี 2568: <span class="big-num">692.2</span> ล้านบาท</b> (+4.3%)
</div>
```

```css
.highlight { padding: 8px 12px; border-radius: 8px; margin: 8px 0; 
             font-size: 12px; font-weight: 600; }
.hl-blue { background: #e3f2fd; color: #1565c0; }
.hl-green { background: #e8f5e9; color: #2e7d32; }
.hl-orange { background: #fff3e0; color: #e65100; }
.hl-purple { background: #f3e5f5; color: #6a1b9a; }
.hl-red { background: #ffebee; color: #c62828; }
```

## Font Sizing

ใช้ขนาดเล็กเพื่อให้ข้อมูลพอดีใน 1 หน้า:
- Block title: `font-size: 14px`
- Bullet text: `font-size: 11px`, `line-height: 1.65`
- Tags/chips: `font-size: 10px`
- Highlight: `font-size: 12px`
- Big numbers: `font-size: 20px`, `font-weight: 800`

## Print

```css
@media print {
  body { background: white; }
  .canvas { height: auto; }
  .block { box-shadow: none; break-inside: avoid; }
}
```
