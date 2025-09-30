"""
Date utilities for learning journal commands.
日期工具模块，提供跨平台的日期计算功能。
"""

import datetime
from typing import Tuple, Optional


class DateUtils:
    """日期工具类，提供学习日记系统所需的各种日期计算功能。"""

    @staticmethod
    def get_current_date() -> datetime.date:
        """获取当前日期。"""
        return datetime.date.today()

    @staticmethod
    def get_week_range(target_date: Optional[datetime.date] = None) -> Tuple[datetime.date, datetime.date]:
        """
        获取指定日期所在周的周一和周日。

        Args:
            target_date: 目标日期，默认为今天

        Returns:
            (周一日期, 周日日期)
        """
        if target_date is None:
            target_date = DateUtils.get_current_date()

        # 获取星期几 (0=周一, 6=周日)
        weekday = target_date.weekday()

        # 计算周一
        monday = target_date - datetime.timedelta(days=weekday)

        # 计算周日
        sunday = monday + datetime.timedelta(days=6)

        return monday, sunday

    @staticmethod
    def format_week_folder_name(monday: datetime.date, sunday: datetime.date) -> str:
        """
        格式化周文件夹名称为 YYYY_MMDD-MMDD 格式。

        Args:
            monday: 周一日期
            sunday: 周日日期

        Returns:
            格式化的文件夹名称
        """
        year = monday.year
        monday_str = monday.strftime("%m%d")
        sunday_str = sunday.strftime("%m%d")

        return f"{year}_{monday_str}-{sunday_str}"

    @staticmethod
    def format_daily_filename(target_date: datetime.date) -> str:
        """
        格式化日记文件名为 YYYY_MM_DD.md 格式。

        Args:
            target_date: 目标日期

        Returns:
            格式化的文件名
        """
        return target_date.strftime("%Y_%m_%d.md")

    @staticmethod
    def format_header_date(target_date: datetime.date) -> str:
        """
        格式化日记头部日期为 MMDD 格式。

        Args:
            target_date: 目标日期

        Returns:
            格式化的头部日期
        """
        return target_date.strftime("%m%d")

    @staticmethod
    def format_display_date(target_date: datetime.date) -> str:
        """
        格式化显示日期为 Month DD 格式。

        Args:
            target_date: 目标日期

        Returns:
            格式化的显示日期
        """
        return target_date.strftime("%B %d")

    @staticmethod
    def format_chinese_date(target_date: datetime.date) -> str:
        """
        格式化中文日期为 YYYY年MM月DD日 格式。

        Args:
            target_date: 目标日期

        Returns:
            格式化的中文日期
        """
        return target_date.strftime("%Y年%m月%d日")

    @staticmethod
    def parse_filename_date(filename: str) -> Optional[datetime.date]:
        """
        从文件名解析日期 (YYYY_MM_DD.md 格式)。

        Args:
            filename: 文件名

        Returns:
            解析出的日期，如果格式不匹配则返回None
        """
        try:
            # 移除.md后缀
            if filename.endswith('.md'):
                filename = filename[:-3]

            # 解析日期部分
            parts = filename.split('_')
            if len(parts) == 3:
                year, month, day = map(int, parts)
                return datetime.date(year, month, day)
        except (ValueError, IndexError):
            pass

        return None

    @staticmethod
    def get_date_n_days_ago(n_days: int, reference_date: Optional[datetime.date] = None) -> datetime.date:
        """
        获取N天前的日期。

        Args:
            n_days: 天数
            reference_date: 参考日期，默认为今天

        Returns:
            N天前的日期
        """
        if reference_date is None:
            reference_date = DateUtils.get_current_date()

        return reference_date - datetime.timedelta(days=n_days)

    @staticmethod
    def get_date_n_weeks_ago(n_weeks: int, reference_date: Optional[datetime.date] = None) -> datetime.date:
        """
        获取N周前的日期。

        Args:
            n_weeks: 周数
            reference_date: 参考日期，默认为今天

        Returns:
            N周前的日期
        """
        n_days = n_weeks * 7
        return DateUtils.get_date_n_days_ago(n_days, reference_date)

    @staticmethod
    def is_date_in_range(target_date: datetime.date, start_date: datetime.date, end_date: datetime.date) -> bool:
        """
        检查目标日期是否在指定范围内。

        Args:
            target_date: 目标日期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            是否在范围内
        """
        return start_date <= target_date <= end_date

    @staticmethod
    def calculate_days_between(start_date: datetime.date, end_date: datetime.date) -> int:
        """
        计算两个日期之间的天数。

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            天数差异
        """
        return (end_date - start_date).days

    @staticmethod
    def calculate_months_between(start_date: datetime.date, end_date: datetime.date) -> int:
        """
        计算两个日期之间的月数。

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            月数差异
        """
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)