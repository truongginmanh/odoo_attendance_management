import csv
from datetime import datetime, timedelta
from collections import defaultdict


# ============================================================
# 1. Đường dẫn file dữ liệu chấm công
# ============================================================

file_path = "sample_data/attendance_sample.csv"


# ============================================================
# 2. Đọc dữ liệu từ file CSV
# ============================================================

records = []

with open(file_path, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        timestamp = datetime.strptime(
            row["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

        record = {
            "employee_code": row["employee_code"],
            "timestamp": timestamp
        }

        records.append(record)


# ============================================================
# 3. Sắp xếp dữ liệu
# ============================================================

records.sort(
    key=lambda x: (
        x["employee_code"],
        x["timestamp"]
    )
)


# ============================================================
# 4. Group theo nhân viên + ngày
# ============================================================

grouped = defaultdict(list)

for record in records:
    key = (
        record["employee_code"],
        record["timestamp"].date()
    )

    grouped[key].append(record["timestamp"])


# ============================================================
# 5. Danh sách kết quả và danh sách lỗi
# ============================================================

attendance_results = []
errors = []


# ============================================================
# 6. Xử lý dữ liệu chấm công
# ============================================================

for (employee_code, work_date), timestamps in grouped.items():

    print(f"\n{employee_code} - {work_date}")

    # --------------------------------------------------------
    # 6.1. Số lần quẹt
    # --------------------------------------------------------

    punch_count = len(timestamps)

    print(f"  Số lần quẹt: {punch_count}")

    # --------------------------------------------------------
    # 6.2. Tạo kết quả chấm công
    # --------------------------------------------------------

    attendance_result = {
        "employee_code": employee_code,
        "date": work_date,
        "check_in": None,
        "check_out": None,
        "working_time": timedelta(),
        "status": "VALID"
    }

    # --------------------------------------------------------
    # 6.3. Tổng thời gian làm việc
    # --------------------------------------------------------

    total_working_time = timedelta()

    # --------------------------------------------------------
    # 6.4. Kiểm tra số lần quẹt
    # --------------------------------------------------------

    if punch_count % 2 != 0:

        error = {
            "employee_code": employee_code,
            "date": work_date,
            "error_type": "MISSING_CHECK_OUT",
            "message": "Thiếu CHECK-OUT"
        }

        errors.append(error)

        attendance_result["status"] = "ERROR"

        print(
            "  ⚠ CẢNH BÁO: "
            "Số lần quẹt là số lẻ - có thể thiếu CHECK-OUT"
        )

    # --------------------------------------------------------
    # 6.5. Xác định Check-in / Check-out
    # --------------------------------------------------------

    for index in range(0, len(timestamps), 2):

        # ----------------------------------------------------
        # Check-in
        # ----------------------------------------------------

        check_in = timestamps[index]

        print(
            f"  {check_in} -> CHECK-IN"
        )

        # Lưu Check-in đầu tiên
        if attendance_result["check_in"] is None:
            attendance_result["check_in"] = check_in

        # ----------------------------------------------------
        # Kiểm tra Check-out
        # ----------------------------------------------------

        if index + 1 < len(timestamps):

            check_out = timestamps[index + 1]

            print(
                f"  {check_out} -> CHECK-OUT"
            )

            # Lưu Check-out
            attendance_result["check_out"] = check_out

            # Tính thời gian của ca
            working_time = check_out - check_in

            print(
                f"    Thời gian ca: {working_time}"
            )

            # Cộng vào tổng thời gian
            total_working_time += working_time

        else:

            # ------------------------------------------------
            # Thiếu Check-out
            # ------------------------------------------------

            print(
                "    ⚠ THIẾU CHECK-OUT"
            )

    # --------------------------------------------------------
    # 6.6. Lưu tổng thời gian
    # --------------------------------------------------------

    attendance_result["working_time"] = total_working_time

    # --------------------------------------------------------
    # 6.7. Thêm kết quả vào danh sách
    # --------------------------------------------------------

    attendance_results.append(attendance_result)

    # --------------------------------------------------------
    # 6.8. In tổng thời gian
    # --------------------------------------------------------

    print(
        f"  Tổng thời gian làm việc: "
        f"{total_working_time}"
    )


# ============================================================
# 7. In danh sách lỗi
# ============================================================

print("\n" + "=" * 60)
print("DANH SÁCH LỖI")
print("=" * 60)

if errors:

    for error in errors:

        print(
            f"{error['employee_code']} | "
            f"{error['date']} | "
            f"{error['error_type']} | "
            f"{error['message']}"
        )

else:

    print("Không có lỗi.")


# ============================================================
# 8. In Attendance Results
# ============================================================

print("\n" + "=" * 60)
print("ATTENDANCE RESULTS")
print("=" * 60)

for result in attendance_results:

    print(
        f"{result['employee_code']} | "
        f"{result['date']} | "
        f"Check-in: {result['check_in']} | "
        f"Check-out: {result['check_out']} | "
        f"Working time: {result['working_time']} | "
        f"Status: {result['status']}"
    )
    
# ============================================================
# 9. Xuất Attendance Results ra CSV
# ============================================================

output_file = "sample_data/attendance_processed.csv"

with open(
    output_file,
    "w",
    encoding="utf-8",
    newline=""
) as file:

    writer = csv.writer(file)

    # Header
    writer.writerow([
        "employee_code",
        "date",
        "check_in",
        "check_out",
        "working_time",
        "status"
    ])

    # Data
    for result in attendance_results:

        check_in = ""

        if result["check_in"] is not None:
            check_in = result["check_in"].strftime(
                "%H:%M:%S"
            )

        check_out = ""

        if result["check_out"] is not None:
            check_out = result["check_out"].strftime(
                "%H:%M:%S"
            )

        writer.writerow([
            result["employee_code"],
            result["date"],
            check_in,
            check_out,
            result["working_time"],
            result["status"]
        ])


print("\n" + "=" * 60)
print("ĐÃ XUẤT FILE")
print("=" * 60)

print(
    f"File: {output_file}"
)