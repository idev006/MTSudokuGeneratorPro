# Comprehensive Test Plan: Sudoku Generator Pro

## 1. Action Plan (แผนการดำเนินการ)

### วัตถุประสงค์ (Objective)
เพื่อตรวจสอบความถูกต้อง (Correctness), ประสิทธิภาพ (Performance), และความสมบูรณ์ (Completeness) ของระบบสร้างโจทย์ Sudoku ทั้ง 11 ประเภท หลังจากมีการปรับปรุงระบบ Jigsaw Template Cache

### ขอบเขตการทดสอบ (Scope)
ทดสอบการสร้างโจทย์ (Generation) และการสร้างไฟล์ PDF (PDF Rendering) สำหรับ:
1.  **Standard Types:** Classic (6x6, 9x9, 12x12)
2.  **Variant Types:** Diagonal, Windoku, Asterisk, Consecutive, Even-Odd
3.  **Jigsaw Types:** Jigsaw (6x6, 9x9), Jigsaw + Diagonal
4.  **Symbol Types:** Thai Alphabet, English Alphabet

### เครื่องมือที่ใช้ (Tools)
- Python Script (`tests/final_verification.py`) สำหรับรัน Test Case อัตโนมัติ
- `time` module สำหรับวัดความเร็ว
- `PDFService` สำหรับตรวจสอบผลลัพธ์ทางสายตา (Visual Verification)

---

## 2. Test Cases (กรณีทดสอบ)

| ID | Category | Type | Size | Expected Result | Criteria |
|----|----------|------|------|-----------------|----------|
| TC01 | Standard | Classic | 9x9 | Success (<1s) | Valid 9x9 grid, standard rules |
| TC02 | Standard | Classic | 6x6 | Success (<1s) | Valid 6x6 grid, 2x3 boxes |
| TC03 | Standard | Classic | 12x12 | Success (<2s) | Valid 12x12 grid, 3x4 boxes |
| TC04 | Variant | Diagonal | 9x9 | Success (<1s) | X-shape constraint satisfied |
| TC05 | Variant | Windoku | 9x9 | Success (<2s) | 4 extra windows satisfied |
| TC06 | Variant | Asterisk | 9x9 | Success (<1s) | Center asterisk satisfied |
| TC07 | Variant | Consecutive | 9x9 | Success (<1s) | Bars between consecutive numbers |
| TC08 | Variant | Even-Odd | 9x9 | Success (<1s) | Shaded even/odd cells |
| TC09 | Jigsaw | Jigsaw | 6x6 | Success (<0.5s) | Irregular regions (from cache) |
| TC10 | Jigsaw | Jigsaw | 9x9 | Success (<1s) | Irregular regions (from cache) |
| TC11 | Jigsaw | Jigsaw+Diagonal | 9x9 | **Success (<0.1s)** | Irregular + X-shape (from cache + permute) |
| TC12 | Symbol | Thai Alphabet | 9x9 | Success (<1s) | Uses ก-ฉ instead of 1-9 |
| TC13 | Symbol | English Alphabet | 9x9 | Success (<1s) | Uses A-I instead of 1-9 |

---

## 3. Execution Steps (ขั้นตอนการทดสอบ)
1.  สร้างไฟล์ `tests/final_verification.py`
2.  รัน Loop ทดสอบตามรายการ TC01 - TC13
3.  จับเวลาการทำงานแต่ละข้อ
4.  ตรวจสอบความถูกต้องของ Grid (เบื้องต้น)
5.  รวมผลลัพธ์ทั้งหมดลงไฟล์ PDF เดียว (`final_test_result.pdf`)
6.  บันทึก Log ผลการทดสอบลงไฟล์ Markdown (`app/doc/test_report_final.md`)

---

## 4. Problem Handling (การจัดการปัญหา)
- หากพบ Error ใน Type ใด ให้บันทึก Error Message และข้ามไป Type ถัดไป
- หากเวลาเกินเกณฑ์ (Timeout) ให้ระบุว่าเป็น Performance Issue
- หาก PDF สร้างไม่ได้ ให้ตรวจสอบ `pdf_service.py` อีกครั้ง
