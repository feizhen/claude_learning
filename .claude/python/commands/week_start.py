#!/usr/bin/env python3
"""
Week Start Command
创建周文件夹的Python实现。

Creates a weekly folder in the `weeks` directory with format `YYYY_MMDD1-MMDD2`
where DD1 is Monday and DD2 is Sunday of the current week.
"""

import sys
import os

# 添加父目录到Python路径，以便导入core模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils
from core.file_utils import FileUtils


def main():
    """主函数，执行week-start命令逻辑。"""
    try:
        # 获取当前日期
        current_date = DateUtils.get_current_date()

        # 获取当前周的周一和周日
        monday, sunday = DateUtils.get_week_range(current_date)

        # 格式化周文件夹名称
        folder_name = DateUtils.format_week_folder_name(monday, sunday)

        # 创建weeks目录
        weeks_dir = FileUtils.get_weeks_directory()
        FileUtils.ensure_directory(weeks_dir)

        # 获取周文件夹完整路径
        week_folder_path = FileUtils.get_week_folder_path(folder_name)

        # 检查周文件夹是否已存在
        if FileUtils.directory_exists(week_folder_path):
            relative_path = FileUtils.get_relative_path(week_folder_path)
            print(f"Weekly folder already exists: {relative_path}")
            return

        # 创建周文件夹
        FileUtils.ensure_directory(week_folder_path)

        # 输出成功消息
        relative_path = FileUtils.get_relative_path(week_folder_path)
        print(f"Created weekly folder: {relative_path}")

    except Exception as e:
        print(f"Error creating weekly folder: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()