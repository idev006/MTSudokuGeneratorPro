# SudokuMaster Gen - Knowledge Base & Developer Guide

เอกสารนี้รวบรวมปัญหาที่พบ (Issues), วิธีแก้ไข (Solutions), และเทคนิค (Techniques) ที่ใช้ในการพัฒนาโปรเจคนี้ เพื่อเป็นแหล่งเรียนรู้และอ้างอิงสำหรับนักพัฒนาท่านอื่น

---

## 1. Project Initialization & Setup

### 1.1 Git & Virtual Environment Exclusion
**Problem:** การนำไฟล์ Virtual Environment (`venv`, `Lib`, `Scripts`) ขึ้น Git ทำให้ Repository มีขนาดใหญ่เกินจำเป็นและอาจเกิด conflict เมื่อไปรันบนเครื่องอื่น
**Solution:** สร้างไฟล์ `.gitignore` ที่ครอบคลุมไฟล์ระบบและ Python environment
**Technique:** ใช้ Pattern มาตรฐานสำหรับ Python:
```gitignore
# Virtual Environment
Lib/
Scripts/
pyvenv.cfg
# Python artifacts
__pycache__/
*.pyc
```

### 1.2 Project Structure Design
**Concept:** การแยกส่วนประกอบระบบตั้งแต่ต้น (Separation of Concerns)
**Technique:** ใช้โครงสร้างแบบ Modular
*   `app/core`: สมอง (Logic ล้วนๆ ห้ามมี UI)
*   `app/mvvm`: หน้าตา (UI และ State)
*   `app/services`: คนงาน (I/O, Multiprocessing)
**Benefit:** ทำให้สามารถทดสอบ Core Logic ได้โดยไม่ต้องเปิดโปรแกรมหน้าจอ และเปลี่ยน UI ได้โดยไม่ต้องแก้ Logic

---

## 2. Core Logic Implementation (Phase 1)

*(รอการบันทึกเมื่อเริ่ม Phase 1)*

---

## 3. Multiprocessing & Communication (Phase 2)

*(รอการบันทึกเมื่อเริ่ม Phase 2)*

---

## 4. UI & MVVM Patterns (Phase 3)

*(รอการบันทึกเมื่อเริ่ม Phase 3)*
