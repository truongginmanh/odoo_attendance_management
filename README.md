# Odoo Attendance Management

## 1. Tên dự án
Đọc dữ liệu máy chấm công và quản lý thời gian làm việc nhân viên trên Odoo.

## 2. Mục tiêu
Xây dựng hệ thống trên Odoo để:
- Đọc dữ liệu từ máy chấm công.
- Chuẩn hóa dữ liệu chấm công.
- Mapping mã nhân viên từ máy chấm công với nhân viên trên Odoo.
- Đồng bộ dữ liệu chấm công vào Odoo.
- Quản lý Check-in / Check-out.
- Tính thời gian làm việc của nhân viên.
- Theo dõi trạng thái đồng bộ.
- Xử lý dữ liệu lỗi và dữ liệu trùng.
- Cung cấp các màn hình và báo cáo liên quan.

## 3. Phạm vi dự án

### 3.1. Dữ liệu chấm công
Hệ thống tiếp nhận:
- Device ID
- Employee Code
- Timestamp

### 3.2. Quản lý nhân viên
Hệ thống hỗ trợ:

- Mapping Employee Code với nhân viên Odoo.
- Kiểm tra nhân viên chưa được mapping.
- Kiểm tra mã nhân viên bị trùng.

### 3.3. Quản lý chấm công
Hệ thống xử lý:

- Check-in
- Check-out
- Nhiều lần chấm trong ngày
- Dữ liệu trùng
- Dữ liệu thiếu Check-out
- Dữ liệu không hợp lệ

### 3.4. Quản lý thời gian làm việc

Hệ thống tính:
- Thời gian Check-in
- Thời gian Check-out
- Working Hours
- Trạng thái dữ liệu

### 3.5. Đồng bộ dữ liệu

Hệ thống hỗ trợ:
- Import dữ liệu
- Đồng bộ dữ liệu
- Chống dữ liệu trùng
- Log quá trình đồng bộ
- Xử lý lỗi
- Retry dữ liệu lỗi

## 4. Kiến trúc dự kiến
Attendance Device
        |
        v
Data Source
(CSV / API)
        |
        v
Python Data Processor
        |
        v
Raw Attendance
        |
        v
Employee Mapping
        |
        v
Odoo Attendance
        |
        v
Working Time
        |
        v
Reports

## 5. Công nghệ

- Python
- Odoo
- PostgreSQL
- XML
- Git / GitHub
- VS Code

## 6. Cấu trúc project

odoo_attendance_management/
│
├── addon/
│   └── attendance_management/
│
├── scripts/
│
├── tests/
│
├── sample_data/
│
├── docs/
│
├── README.md
└── .gitignore

## 7. Trạng thái

Development