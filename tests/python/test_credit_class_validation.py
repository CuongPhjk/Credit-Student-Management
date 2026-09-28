from datetime import date
import unittest

from frontend.pages.credit_class_page import (
    academic_year_is_current_or_future,
    current_academic_year,
)


class CreditClassAcademicYearValidationTest(unittest.TestCase):
    def test_current_academic_year_changes_in_august(self):
        self.assertEqual(current_academic_year(date(2026, 7, 31)), "2025-2026")
        self.assertEqual(current_academic_year(date(2026, 8, 1)), "2026-2027")

    def test_rejects_past_academic_year(self):
        today = date(2026, 9, 25)
        self.assertFalse(
            academic_year_is_current_or_future("2025-2026", today)
        )

    def test_accepts_current_and_future_academic_years(self):
        today = date(2026, 9, 25)
        self.assertTrue(
            academic_year_is_current_or_future("2026-2027", today)
        )
        self.assertTrue(
            academic_year_is_current_or_future("2027-2028", today)
        )

    def test_rejects_invalid_format(self):
        today = date(2026, 9, 25)
        self.assertFalse(
            academic_year_is_current_or_future("2026-2028", today)
        )


if __name__ == "__main__":
    unittest.main()
