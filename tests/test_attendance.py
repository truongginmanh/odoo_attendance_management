import csv
import tempfile
import unittest
from datetime import datetime, timedelta

from scripts.read_attendance import (
    load_attendance_data,
    group_attendance,
    process_attendance,
    export_attendance_errors,
)


class TestAttendance(unittest.TestCase):

    # ========================================================
    # Test 1: Đọc dữ liệu hợp lệ
    # ========================================================

    def test_load_valid_records(self):
        records, errors = load_attendance_data(
            "sample_data/attendance_valid.csv"
        )

        self.assertEqual(len(records), 32)
        self.assertEqual(len(errors), 0)

    # ========================================================
    # Test 2: Phát hiện bản ghi bị trùng
    # ========================================================

    def test_duplicate_record(self):
        rows = [
            ["employee_code", "timestamp"],
            ["NV001", "2026-09-01 08:00:00"],
            ["NV001", "2026-09-01 08:00:00"],
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            writer = csv.writer(file)
            writer.writerows(rows)
            file_path = file.name

        records, errors = load_attendance_data(file_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0]["error_type"],
            "DUPLICATE"
        )

    # ========================================================
    # Test 3: Phát hiện timestamp không hợp lệ
    # ========================================================

    def test_invalid_timestamp(self):
        rows = [
            ["employee_code", "timestamp"],
            ["NV001", "2026-99-99 25:70:00"],
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            writer = csv.writer(file)
            writer.writerows(rows)
            file_path = file.name

        records, errors = load_attendance_data(file_path)

        self.assertEqual(len(records), 0)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0]["error_type"],
            "INVALID_TIMESTAMP"
        )

    # ========================================================
    # Test 4: Phát hiện dữ liệu không hợp lệ
    # ========================================================

    def test_invalid_data(self):
        rows = [
            ["employee_code", "timestamp"],
            ["", "2026-09-01 08:00:00"],
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            writer = csv.writer(file)
            writer.writerows(rows)
            file_path = file.name

        records, errors = load_attendance_data(file_path)

        self.assertEqual(len(records), 0)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0]["error_type"],
            "INVALID_DATA"
        )

    # ========================================================
    # Test 5: Phát hiện thiếu CHECK-OUT
    # ========================================================

    def test_missing_check_out(self):
        records = [
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 8, 0, 0
                ),
            }
        ]

        grouped = group_attendance(records)

        results, errors = process_attendance(grouped)

        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0]["error_type"],
            "MISSING_CHECK_OUT"
        )
        self.assertEqual(
            results[0]["status"],
            "ERROR"
        )

    # ========================================================
    # Test 6: Tính thời gian làm việc
    # ========================================================

    def test_working_time(self):
        records = [
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 8, 0, 0
                ),
            },
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 17, 0, 0
                ),
            },
        ]

        grouped = group_attendance(records)

        results, errors = process_attendance(grouped)

        self.assertEqual(len(errors), 0)

        self.assertEqual(
            results[0]["working_time"],
            timedelta(hours=9)
        )

        self.assertEqual(
            results[0]["status"],
            "VALID"
        )

    # ========================================================
    # Test 7: Nhiều lần chấm công trong một ngày
    # ========================================================

    def test_multiple_punches(self):
        records = [
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 8, 0, 0
                ),
            },
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 12, 0, 0
                ),
            },
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 13, 0, 0
                ),
            },
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 17, 0, 0
                ),
            },
        ]

        grouped = group_attendance(records)

        results, errors = process_attendance(grouped)

        # ----------------------------------------------------
        # Kiểm tra không có lỗi
        # ----------------------------------------------------

        self.assertEqual(len(errors), 0)

        # ----------------------------------------------------
        # Kiểm tra CHECK-IN đầu tiên
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["check_in"],
            datetime(2026, 9, 1, 8, 0, 0)
        )

        # ----------------------------------------------------
        # Kiểm tra CHECK-OUT cuối cùng
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["check_out"],
            datetime(2026, 9, 1, 17, 0, 0)
        )

        # ----------------------------------------------------
        # Kiểm tra tổng thời gian làm việc
        #
        # 08:00 -> 12:00 = 4 giờ
        # 13:00 -> 17:00 = 4 giờ
        #
        # Tổng = 8 giờ
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["working_time"],
            timedelta(hours=8)
        )

        # ----------------------------------------------------
        # Kiểm tra trạng thái
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["status"],
            "VALID"
        )

        # ----------------------------------------------------
        # Kiểm tra số khoảng làm việc
        # ----------------------------------------------------

        self.assertEqual(
            len(results[0]["intervals"]),
            2
        )

        # ----------------------------------------------------
        # Kiểm tra khoảng làm việc thứ nhất
        #
        # 08:00 -> 12:00
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["intervals"][0]["check_in"],
            datetime(2026, 9, 1, 8, 0, 0)
        )

        self.assertEqual(
            results[0]["intervals"][0]["check_out"],
            datetime(2026, 9, 1, 12, 0, 0)
        )

        self.assertEqual(
            results[0]["intervals"][0]["working_time"],
            timedelta(hours=4)
        )

        # ----------------------------------------------------
        # Kiểm tra khoảng làm việc thứ hai
        #
        # 13:00 -> 17:00
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["intervals"][1]["check_in"],
            datetime(2026, 9, 1, 13, 0, 0)
        )

        self.assertEqual(
            results[0]["intervals"][1]["check_out"],
            datetime(2026, 9, 1, 17, 0, 0)
        )

        self.assertEqual(
            results[0]["intervals"][1]["working_time"],
            timedelta(hours=4)
        )

    # ========================================================
    # Test 8: Xuất file lỗi
    # ========================================================

    def test_export_attendance_errors(self):
        errors = [
            {
                "row": 34,
                "employee_code": "NV001",
                "date": "2026-09-01",
                "error_type": "DUPLICATE",
                "message": "Bản ghi chấm công bị trùng"
            },
            {
                "row": 35,
                "employee_code": "NV006",
                "date": "",
                "error_type": "INVALID_TIMESTAMP",
                "message": "Timestamp không hợp lệ"
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False
        ) as file:

            file_path = file.name

        export_attendance_errors(
            file_path,
            errors
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        self.assertIn(
            "error_type",
            content
        )

        self.assertIn(
            "DUPLICATE",
            content
        )

        self.assertIn(
            "INVALID_TIMESTAMP",
            content
        )

    # ========================================================
    # Test 9: Nhiều punch nhưng thiếu CHECK-OUT cuối ngày
    # ========================================================

    def test_missing_check_out_after_multiple_punches(self):
        records = [
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 8, 0, 0
                ),
            },
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 12, 0, 0
                ),
            },
            {
                "employee_code": "NV001",
                "timestamp": datetime(
                    2026, 9, 1, 13, 0, 0
                ),
            },
        ]

        grouped = group_attendance(records)

        results, errors = process_attendance(grouped)

        # ----------------------------------------------------
        # Kiểm tra có đúng 1 kết quả attendance
        # ----------------------------------------------------

        self.assertEqual(
            len(results),
            1
        )

        # ----------------------------------------------------
        # Kiểm tra có đúng 1 lỗi
        # ----------------------------------------------------

        self.assertEqual(
            len(errors),
            1
        )

        # ----------------------------------------------------
        # Kiểm tra loại lỗi
        # ----------------------------------------------------

        self.assertEqual(
            errors[0]["error_type"],
            "MISSING_CHECK_OUT"
        )

        # ----------------------------------------------------
        # Kiểm tra trạng thái
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["status"],
            "ERROR"
        )

        # ----------------------------------------------------
        # Kiểm tra tổng thời gian làm việc
        #
        # 08:00 -> 12:00 = 4 giờ
        # 13:00 chưa có CHECK-OUT
        #
        # => Chỉ tính 4 giờ hoàn chỉnh
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["working_time"],
            timedelta(hours=4)
        )

        # ----------------------------------------------------
        # Kiểm tra số khoảng làm việc hoàn chỉnh
        # ----------------------------------------------------

        self.assertEqual(
            len(results[0]["intervals"]),
            1
        )

        # ----------------------------------------------------
        # Kiểm tra khoảng làm việc
        #
        # 08:00 -> 12:00
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["intervals"][0]["check_in"],
            datetime(
                2026, 9, 1, 8, 0, 0
            )
        )

        self.assertEqual(
            results[0]["intervals"][0]["check_out"],
            datetime(
                2026, 9, 1, 12, 0, 0
            )
        )

        self.assertEqual(
            results[0]["intervals"][0]["working_time"],
            timedelta(hours=4)
        )

        # ----------------------------------------------------
        # Kiểm tra CHECK-IN đầu tiên
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["check_in"],
            datetime(
                2026, 9, 1, 8, 0, 0
            )
        )

        # ----------------------------------------------------
        # CHECK-OUT cuối cùng hợp lệ là 12:00
        # Punch 13:00 đang chờ CHECK-OUT
        # ----------------------------------------------------

        self.assertEqual(
            results[0]["check_out"],
            datetime(
                2026, 9, 1, 12, 0, 0
            )
        )

if __name__ == "__main__":
    unittest.main()