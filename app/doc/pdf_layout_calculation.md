# PDF Layout Calculation - Technical Documentation

## ปัญหาเดิม
การคำนวณ layout แบบ hard-code:
```python
if grid_size <= 6: return (3, 3, 150)  # ❌ ไม่ได้คำนวณจากขนาดจริง
```

## วิธีแก้ไขที่ถูกต้อง

### 1. ข้อมูลพื้นฐาน
- **A4 Size:** 595 × 842 points (Portrait)
- **Margin:** 50 points
- **Available Space:** 495 × 742 points

### 2. กำหนดขนาด Cell
```python
MIN_CELL_SIZE = 20 points  # ขั้นต่ำเพื่อความชัดเจน
MAX_CELL_SIZE = 40 points  # สูงสุดสำหรับตารางเล็ก
```

### 3. ขั้นตอนการคำนวณ

#### Step 1: กำหนด Ideal Cell Size
```python
if grid_size <= 6:
    ideal_cell_size = 40  # ตารางเล็ก ใช้ cell ใหญ่
elif grid_size <= 9:
    ideal_cell_size = 30
else:
    ideal_cell_size = 20  # ตารางใหญ่ ใช้ cell เล็ก
```

#### Step 2: คำนวณขนาดตาราง
```python
puzzle_size = grid_size × ideal_cell_size

ตัวอย่าง:
- 6×6: 6 × 40 = 240 points
- 9×9: 9 × 30 = 270 points
- 12×12: 12 × 20 = 240 points
```

#### Step 3: คำนวณจำนวนตารางที่พอดี
```python
spacing = puzzle_size × 0.1  # เว้นระยะ 10%

cols = available_width / (puzzle_size + spacing)
rows = available_height / (puzzle_size + spacing)

ตัวอย่าง 6×6:
- puzzle_size = 240
- spacing = 24
- cols = 495 / (240 + 24) = 1.87 → 1 col
- rows = 742 / (240 + 24) = 2.81 → 2 rows
```

#### Step 4: ปรับขนาดให้พอดีพื้นที่
```python
actual_width = (available_width - spacing × (cols - 1)) / cols
actual_height = (available_height - spacing × (rows - 1)) / rows

final_puzzle_size = min(actual_width, actual_height)
```

#### Step 5: ตรวจสอบ Cell Size
```python
final_cell_size = final_puzzle_size / grid_size

if final_cell_size < MIN_CELL_SIZE:
    # ลดจำนวนตารางต่อหน้า
    if cols > rows:
        cols -= 1
    else:
        rows -= 1
    # คำนวณใหม่
```

## ผลลัพธ์

### 6×6 Grid
- **Ideal Cell:** 40 points
- **Puzzle Size:** 240 points
- **Layout:** 1×2 (2 puzzles/page)
- **Actual Cell:** ~35 points

### 9×9 Grid
- **Ideal Cell:** 30 points
- **Puzzle Size:** 270 points
- **Layout:** 1×2 (2 puzzles/page)
- **Actual Cell:** ~30 points

### 12×12 Grid
- **Ideal Cell:** 20 points
- **Puzzle Size:** 240 points
- **Layout:** 1×2 (2 puzzles/page)
- **Actual Cell:** ~20 points

## ข้อดีของวิธีใหม่

1. ✅ **คำนวณอัตโนมัติ** - ไม่ต้อง hard-code
2. ✅ **ใช้พื้นที่เต็มที่** - ปรับขนาดให้พอดี A4
3. ✅ **รักษาสัดส่วน** - Cell เป็นสี่เหลี่ยมจัตุรัส
4. ✅ **อ่านง่าย** - Cell ไม่เล็กเกินไป (≥20 points)
5. ✅ **ยืดหยุ่น** - รองรับทุกขนาดตาราง (6-15)

## Code Reference
```python
# ใน app/services/pdf_service.py
def _calculate_layout(self, grid_size, page_width, page_height, margin):
    # คำนวณจากขนาดจริง
    # ดูโค้ดเต็มในไฟล์
```
