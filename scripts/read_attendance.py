import csv
from datetime import datetime, timedelta
from collections import defaultdict


# ============================================================
# 1. File paths
# ============================================================

INPUT_FILE = "sample_data/attendance_test_invalid.csv"
OUTPUT_FILE = "sample_data/attendance_processed.csv"
ERROR_OUTPUT_FILE = "sample_data/attendance_errors.csv"


# ============================================================
# 2. Load attendance data
# ============================================================

def load_attendance_data(file_path):
    records = []
    errors = []
    seen_records = set()

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):

            employee_code = row.get(
                "employee_code",
                ""
            ).strip()

            timestamp_text = row.get(
                "timestamp",
                ""
            ).strip()

            # ------------------------------------------------
            # Kiểm tra Employee Code
            # ------------------------------------------------

            if not employee_code:

                errors.append({
                    "row": row_number,
                    "employee_code": "",
                    "date": None,
                    "error_type": "INVALID_DATA",
                    "message": "Thiếu Employee Code"
                })

                continue

            # ------------------------------------------------
            # Kiểm tra Timestamp
            # ------------------------------------------------

            if not timestamp_text:

                errors.append({
                    "row": row_number,
                    "employee_code": employee_code,
                    "date": None,
                    "error_type": "INVALID_TIMESTAMP",
                    "message": "Thiếu Timestamp"
                })

                continue

            # ------------------------------------------------
            # Parse Timestamp
            # ------------------------------------------------

            try:

                timestamp = datetime.strptime(
                    timestamp_text,
                    "%Y-%m-%d %H:%M:%S"
                )

            except ValueError:

                errors.append({
                    "row": row_number,
                    "employee_code": employee_code,
                    "date": None,
                    "error_type": "INVALID_TIMESTAMP",
                    "message": (
                        f"Timestamp không hợp lệ: "
                        f"{timestamp_text}"
                    )
                })

                continue

            # ------------------------------------------------
            # Kiểm tra duplicate
            # ------------------------------------------------

            duplicate_key = (
                employee_code,
                timestamp
            )

            if duplicate_key in seen_records:

                errors.append({
                    "row": row_number,
                    "employee_code": employee_code,
                    "date": timestamp.date(),
                    "error_type": "DUPLICATE",
                    "message": "Bản ghi chấm công bị trùng"
                })

                continue

            seen_records.add(duplicate_key)

            # ------------------------------------------------
            # Lưu record hợp lệ
            # ------------------------------------------------

            records.append({
                "employee_code": employee_code,
                "timestamp": timestamp
            })

    return records, errors


# ============================================================
# 3. Group attendance by employee + date
# ============================================================

def group_attendance(records):
    grouped = defaultdict(list)

    for record in records:

        key = (
            record["employee_code"],
            record["timestamp"].date()
        )

        grouped[key].append(
            record["timestamp"]
        )

    return grouped


# ============================================================
# 4. Process attendance
# ============================================================

def process_attendance(grouped):

    attendance_results = []
    errors = []

    for (
        employee_code,
        work_date
    ), timestamps in grouped.items():

        # ----------------------------------------------------
        # Luôn sắp xếp punch theo thời gian
        # ----------------------------------------------------

        timestamps.sort()

        punch_count = len(timestamps)

        # ----------------------------------------------------
        # Kết quả attendance của một nhân viên / một ngày
        # ----------------------------------------------------

        attendance_result = {
            "employee_code": employee_code,
            "date": work_date,
            "check_in": None,
            "check_out": None,
            "intervals": [],
            "working_time": timedelta(),
            "status": "VALID"
        }

        total_working_time = timedelta()

        # ----------------------------------------------------
        # Không có punch
        # ----------------------------------------------------

        if punch_count == 0:

            attendance_result["status"] = "ERROR"

            errors.append({
                "employee_code": employee_code,
                "date": work_date,
                "error_type": "MISSING_CHECK_IN",
                "message": "Không có CHECK-IN"
            })

            attendance_results.append(
                attendance_result
            )

            continue

        # ----------------------------------------------------
        # CHECK-IN đầu tiên
        # ----------------------------------------------------

        attendance_result["check_in"] = timestamps[0]

        # ----------------------------------------------------
        # Ghép từng cặp CHECK-IN / CHECK-OUT
        #
        # Ví dụ:
        #
        # 08:00
        # 12:00
        # 13:00
        # 17:00
        #
        # => 08:00 -> 12:00
        # => 13:00 -> 17:00
        # ----------------------------------------------------

        for index in range(
            0,
            punch_count - 1,
            2
        ):

            check_in = timestamps[index]
            check_out = timestamps[index + 1]

            working_time = (
                check_out - check_in
            )

            # ------------------------------------------------
            # Kiểm tra CHECK-OUT trước CHECK-IN
            # ------------------------------------------------

            if working_time < timedelta():

                errors.append({
                    "employee_code": employee_code,
                    "date": work_date,
                    "error_type": "INVALID_DATA",
                    "message": (
                        "CHECK-OUT xảy ra "
                        "trước CHECK-IN"
                    )
                })

                attendance_result["status"] = "ERROR"

                continue

            # ------------------------------------------------
            # Lưu khoảng làm việc
            # ------------------------------------------------

            interval = {
                "check_in": check_in,
                "check_out": check_out,
                "working_time": working_time
            }

            attendance_result["intervals"].append(
                interval
            )

            # ------------------------------------------------
            # Cộng tổng thời gian
            # ------------------------------------------------

            total_working_time += working_time

            # ------------------------------------------------
            # CHECK-OUT cuối cùng
            # ------------------------------------------------

            attendance_result["check_out"] = check_out

        # ----------------------------------------------------
        # Kiểm tra số punch lẻ
        #
        # Ví dụ:
        # 08:00
        # 12:00
        # 13:00
        #
        # 13:00 chưa có CHECK-OUT
        # ----------------------------------------------------

        if punch_count % 2 != 0:

            last_punch = timestamps[-1]

            errors.append({
                "employee_code": employee_code,
                "date": work_date,
                "error_type": "MISSING_CHECK_OUT",
                "message": (
                    "Thiếu CHECK-OUT "
                    f"sau {last_punch.strftime('%H:%M:%S')}"
                )
            })

            attendance_result["status"] = "ERROR"

        # ----------------------------------------------------
        # Gán tổng thời gian
        # ----------------------------------------------------

        attendance_result["working_time"] = (
            total_working_time
        )

        attendance_results.append(
            attendance_result
        )

    return attendance_results, errors


# ============================================================
# 5. Export attendance results
# ============================================================

def export_attendance_results(
    output_file,
    attendance_results
):

    with open(
        output_file,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "employee_code",
            "date",
            "check_in",
            "check_out",
            "working_time",
            "status",
            "intervals"
        ])

        for result in attendance_results:

            check_in = ""

            if result["check_in"] is not None:

                check_in = (
                    result["check_in"].strftime(
                        "%H:%M:%S"
                    )
                )

            check_out = ""

            if result["check_out"] is not None:

                check_out = (
                    result["check_out"].strftime(
                        "%H:%M:%S"
                    )
                )

            # ------------------------------------------------
            # Chuyển intervals thành chuỗi để export CSV
            # ------------------------------------------------

            intervals_text = []

            for interval in result["intervals"]:

                intervals_text.append(
                    (
                        f"{interval['check_in'].strftime('%H:%M:%S')}"
                        f" -> "
                        f"{interval['check_out'].strftime('%H:%M:%S')}"
                        f" "
                        f"({interval['working_time']})"
                    )
                )

            writer.writerow([
                result["employee_code"],
                result["date"],
                check_in,
                check_out,
                result["working_time"],
                result["status"],
                " | ".join(intervals_text)
            ])


# ============================================================
# 6. Export attendance errors
# ============================================================

def export_attendance_errors(
    output_file,
    errors
):

    with open(
        output_file,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "row",
            "employee_code",
            "date",
            "error_type",
            "message"
        ])

        for error in errors:

            writer.writerow([
                error.get("row", ""),
                error.get("employee_code", ""),
                error.get("date", ""),
                error.get("error_type", ""),
                error.get("message", "")
            ])


# ============================================================
# 7. Main program
# ============================================================

def main():

    print("=" * 60)
    print("ATTENDANCE DATA PROCESSING")
    print("=" * 60)

    # --------------------------------------------------------
    # Đọc dữ liệu
    # --------------------------------------------------------

    records, load_errors = load_attendance_data(
        INPUT_FILE
    )

    print(
        f"\nSố record hợp lệ: {len(records)}"
    )

    print(
        f"Số lỗi khi đọc dữ liệu: "
        f"{len(load_errors)}"
    )

    # --------------------------------------------------------
    # Group dữ liệu
    # --------------------------------------------------------

    grouped = group_attendance(
        records
    )

    # --------------------------------------------------------
    # Xử lý attendance
    # --------------------------------------------------------

    attendance_results, processing_errors = (
        process_attendance(grouped)
    )

    # --------------------------------------------------------
    # Tổng hợp lỗi
    # --------------------------------------------------------

    errors = (
        load_errors +
        processing_errors
    )

    print(
        f"Số lỗi khi xử lý: "
        f"{len(processing_errors)}"
    )

    print(
        f"Tổng số lỗi: "
        f"{len(errors)}"
    )

    # --------------------------------------------------------
    # Danh sách lỗi
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DANH SÁCH LỖI")
    print("=" * 60)

    if errors:

        for error in errors:

            print(
                f"{error.get('employee_code', '')} | "
                f"{error.get('date', '')} | "
                f"{error['error_type']} | "
                f"{error['message']}"
            )

    else:

        print("Không có lỗi.")

    # --------------------------------------------------------
    # Attendance results
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # In các khoảng làm việc
        # ----------------------------------------------------

        for interval in result["intervals"]:

            print(
                f"    "
                f"{interval['check_in'].strftime('%H:%M:%S')}"
                f" -> "
                f"{interval['check_out'].strftime('%H:%M:%S')}"
                f" = "
                f"{interval['working_time']}"
            )

    # --------------------------------------------------------
    # Export attendance results
    # --------------------------------------------------------

    export_attendance_results(
        OUTPUT_FILE,
        attendance_results
    )

    # --------------------------------------------------------
    # Export attendance errors
    # --------------------------------------------------------

    export_attendance_errors(
        ERROR_OUTPUT_FILE,
        errors
    )

    # --------------------------------------------------------
    # Thông báo
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("ĐÃ XUẤT FILE")
    print("=" * 60)

    print(
        f"File kết quả: {OUTPUT_FILE}"
    )

    print(
        f"File lỗi: {ERROR_OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()