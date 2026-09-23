# Database Design - Attendance Management

## 1. Project

Đọc dữ liệu máy chấm công và quản lý thời gian làm việc nhân viên trên Odoo.

## 2. Database Architecture

Project sử dụng:

- Odoo built-in model: hr.employee
- Custom model: attendance.employee.mapping
- Custom model: attendance.raw
- Custom model: attendance.processed
- Custom model: attendance.error

## 3. Data Flow

Machine
    ↓
Raw Attendance
    ↓
Employee Mapping
    ↓
Processed Attendance
    ↓
Reports

Nếu dữ liệu có lỗi:

Processed Attendance
    ↓
Attendance Error

# 4. Model: Employee Mapping

## 4.1. Technical Information

- Model: `attendance.employee.mapping`
- Table: `attendance_employee_mapping`
- Description: Ánh xạ mã nhân viên từ máy chấm công với nhân viên trong Odoo.

## 4.2. Fields

| Field | Label | Odoo Type | PostgreSQL Type | Required | Default | Index | Unique |
|---|---|---|---|---|---|---|---|
| `name` | Mapping Name | Char | VARCHAR | Yes | — | No | No |
| `employee_code` | Employee Code | Char | VARCHAR | Yes | — | Yes | No |
| `employee_id` | Employee | Many2one | INTEGER | Yes | — | Yes | No |
| `device_id` | Device | Char | VARCHAR | No | — | Yes | No |
| `active` | Active | Boolean | BOOLEAN | Yes | True | No | No |
| `note` | Note | Text | TEXT | No | — | No | No |

## 4.3. Relationships

`employee_id`:

- Type: Many2one
- Related model: `hr.employee`
- Meaning: Nhân viên Odoo tương ứng với mã nhân viên trên máy chấm công.

Relationship:

hr.employee 1 ───── N attendance.employee.mapping

# 5. Model: Raw Attendance

## 5.1. Technical Information

- Model: `attendance.raw`
- Table: `attendance_raw`
- Description: Lưu dữ liệu chấm công nguyên bản nhận từ máy chấm công trước khi xử lý.

## 5.2. Fields

| Field | Label | Odoo Type | PostgreSQL Type | Required | Default | Index | Unique |
|---|---|---|---|---|---|---|---|
| `employee_code` | Employee Code | Char | VARCHAR | Yes | — | Yes | No |
| `timestamp` | Timestamp | Datetime | TIMESTAMP | Yes | — | Yes | No |
| `device_id` | Device | Char | VARCHAR | No | — | Yes | No |
| `source` | Source | Selection | VARCHAR | Yes | `manual` | Yes | No |
| `import_date` | Import Date | Datetime | TIMESTAMP | Yes | Now | Yes | No |
| `processed` | Processed | Boolean | BOOLEAN | Yes | False | Yes | No |
| `mapping_id` | Employee Mapping | Many2one | INTEGER | No | — | Yes | No |
| `note` | Note | Text | TEXT | No | — | No | No |

## 5.3. Relationships

`mapping_id`:

- Type: Many2one
- Related model: `attendance.employee.mapping`
- Meaning: Mapping được sử dụng để xác định nhân viên tương ứng.

Relationship:

attendance.employee.mapping 1 ───── N attendance.raw

# 6. Model: Processed Attendance

## 6.1. Technical Information

- Model: `attendance.processed`
- Table: `attendance_processed`
- Description: Lưu kết quả chấm công sau khi xử lý dữ liệu Raw Attendance.

## 6.2. Fields

| Field | Label | Odoo Type | PostgreSQL Type | Required | Default | Index | Unique |
|---|---|---|---|---|---|---|---|
| `employee_id` | Employee | Many2one | INTEGER | Yes | — | Yes | No |
| `employee_code` | Employee Code | Char | VARCHAR | Yes | — | Yes | No |
| `work_date` | Work Date | Date | DATE | Yes | — | Yes | No |
| `check_in` | Check In | Datetime | TIMESTAMP | No | — | Yes | No |
| `check_out` | Check Out | Datetime | TIMESTAMP | No | — | Yes | No |
| `working_time` | Working Time | Float | DOUBLE PRECISION | Yes | 0.0 | No | No |
| `status` | Status | Selection | VARCHAR | Yes | `valid` | Yes | No |
| `note` | Note | Text | TEXT | No | — | No | No |

## 6.3. Relationships

`employee_id`:

- Type: Many2one
- Related model: `hr.employee`
- Meaning: Nhân viên sở hữu bản ghi chấm công.

Relationship:

hr.employee 1 ───── N attendance.processed

## 6.4. Constraints

### Unique Constraint

`employee_id + work_date` phải duy nhất.

Mục đích:

Một nhân viên chỉ có một bản ghi Processed Attendance trong một ngày.

# 7. Model: Attendance Error

## 7.1. Technical Information

- Model: `attendance.error`
- Table: `attendance_error`
- Description: Lưu các lỗi phát sinh trong quá trình xử lý dữ liệu chấm công.

## 7.2. Fields

| Field | Label | Odoo Type | PostgreSQL Type | Required | Default | Index | Unique |
|---|---|---|---|---|---|---|---|
| `employee_id` | Employee | Many2one | INTEGER | No | — | Yes | No |
| `employee_code` | Employee Code | Char | VARCHAR | Yes | — | Yes | No |
| `work_date` | Work Date | Date | DATE | Yes | — | Yes | No |
| `error_type` | Error Type | Selection | VARCHAR | Yes | — | Yes | No |
| `message` | Error Message | Text | TEXT | Yes | — | No | No |
| `raw_attendance_id` | Raw Attendance | Many2one | INTEGER | No | — | Yes | No |
| `processed_attendance_id` | Processed Attendance | Many2one | INTEGER | No | — | Yes | No |
| `resolved` | Resolved | Boolean | BOOLEAN | Yes | False | Yes | No |

## 7.3. Relationships

`employee_id`:

- Type: Many2one
- Related model: `hr.employee`

`raw_attendance_id`:

- Type: Many2one
- Related model: `attendance.raw`

`processed_attendance_id`:

- Type: Many2one
- Related model: `attendance.processed`

## 7.4. Error Types

Các loại lỗi dự kiến:

- `MISSING_CHECK_IN`
- `MISSING_CHECK_OUT`
- `INVALID_MAPPING`
- `DUPLICATE`
- `INVALID_TIMESTAMP`

# 8. Entity Relationship Diagram

```text
                         hr.employee
                              │
                         1    │    N
                              │
                              ▼
                  Employee Mapping
                              │
                         1    │    N
                              │
                              ▼
                     Raw Attendance
                              │
                              │ processing
                              ▼
                  Processed Attendance
                              │
                              │
                              ▼
                    Attendance Error