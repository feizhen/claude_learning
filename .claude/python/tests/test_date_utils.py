#!/usr/bin/env python3
"""
Tests for date_utils module.
"""

import unittest
import datetime
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils


class TestDateUtils(unittest.TestCase):
    """测试DateUtils类。"""

    def setUp(self):
        """测试设置。"""
        self.test_date = datetime.date(2025, 9, 26)  # 2025年9月26日，周五

    def test_get_current_date(self):
        """测试获取当前日期。"""
        result = DateUtils.get_current_date()
        self.assertIsInstance(result, datetime.date)

    def test_get_week_range(self):
        """测试获取周范围。"""
        monday, sunday = DateUtils.get_week_range(self.test_date)

        # 2025年9月26日是周五，所以周一是9月22日，周日是9月28日
        expected_monday = datetime.date(2025, 9, 22)
        expected_sunday = datetime.date(2025, 9, 28)

        self.assertEqual(monday, expected_monday)
        self.assertEqual(sunday, expected_sunday)

    def test_format_week_folder_name(self):
        """测试格式化周文件夹名称。"""
        monday = datetime.date(2025, 9, 22)
        sunday = datetime.date(2025, 9, 28)

        result = DateUtils.format_week_folder_name(monday, sunday)
        expected = "2025_0922-0928"

        self.assertEqual(result, expected)

    def test_format_daily_filename(self):
        """测试格式化日记文件名。"""
        result = DateUtils.format_daily_filename(self.test_date)
        expected = "2025_09_26.md"

        self.assertEqual(result, expected)

    def test_format_header_date(self):
        """测试格式化头部日期。"""
        result = DateUtils.format_header_date(self.test_date)
        expected = "0926"

        self.assertEqual(result, expected)

    def test_parse_filename_date(self):
        """测试解析文件名日期。"""
        # 测试正常文件名
        result = DateUtils.parse_filename_date("2025_09_26.md")
        expected = datetime.date(2025, 9, 26)
        self.assertEqual(result, expected)

        # 测试不带扩展名的文件名
        result = DateUtils.parse_filename_date("2025_09_26")
        expected = datetime.date(2025, 9, 26)
        self.assertEqual(result, expected)

        # 测试无效文件名
        result = DateUtils.parse_filename_date("invalid_filename.md")
        self.assertIsNone(result)

    def test_get_date_n_days_ago(self):
        """测试获取N天前的日期。"""
        result = DateUtils.get_date_n_days_ago(7, self.test_date)
        expected = datetime.date(2025, 9, 19)

        self.assertEqual(result, expected)

    def test_get_date_n_weeks_ago(self):
        """测试获取N周前的日期。"""
        result = DateUtils.get_date_n_weeks_ago(2, self.test_date)
        expected = datetime.date(2025, 9, 12)

        self.assertEqual(result, expected)

    def test_is_date_in_range(self):
        """测试检查日期是否在范围内。"""
        start_date = datetime.date(2025, 9, 20)
        end_date = datetime.date(2025, 9, 30)

        # 在范围内
        self.assertTrue(DateUtils.is_date_in_range(self.test_date, start_date, end_date))

        # 不在范围内
        out_of_range_date = datetime.date(2025, 10, 1)
        self.assertFalse(DateUtils.is_date_in_range(out_of_range_date, start_date, end_date))

    def test_calculate_days_between(self):
        """测试计算天数差异。"""
        start_date = datetime.date(2025, 9, 20)
        end_date = datetime.date(2025, 9, 26)

        result = DateUtils.calculate_days_between(start_date, end_date)
        expected = 6

        self.assertEqual(result, expected)

    def test_calculate_months_between(self):
        """测试计算月数差异。"""
        start_date = datetime.date(2025, 7, 15)
        end_date = datetime.date(2025, 9, 26)

        result = DateUtils.calculate_months_between(start_date, end_date)
        expected = 2

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()