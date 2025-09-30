#!/usr/bin/env python3
"""
Daily Start Command
创建每日日记文件的Python实现。

Creates a daily markdown file in the current week's folder with format `YYYY_MM_DD.md`.
"""

import sys
import os
import datetime

# 添加父目录到Python路径，以便导入core模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils
from core.file_utils import FileUtils
from core.templates import Templates


def main():
    """主函数，执行daily-start命令逻辑。"""
    try:
        # 获取当前日期
        current_date = DateUtils.get_current_date()

        # 获取当前周的周一和周日
        monday, sunday = DateUtils.get_week_range(current_date)

        # 格式化周文件夹名称
        folder_name = DateUtils.format_week_folder_name(monday, sunday)

        # 创建weeks目录和周文件夹
        weeks_dir = FileUtils.get_weeks_directory()
        week_folder = FileUtils.get_week_folder_path(folder_name)
        FileUtils.ensure_directory(week_folder)

        # 格式化日记文件名
        daily_filename = DateUtils.format_daily_filename(current_date)
        daily_file_path = FileUtils.get_daily_file_path(week_folder, daily_filename)

        # 检查文件是否已存在
        if FileUtils.file_exists(daily_file_path):
            relative_path = FileUtils.get_relative_path(daily_file_path)
            print(f"Daily file already exists: {relative_path}")
            return

        # 生成日记模板内容
        template_content = Templates.daily_journal_template(current_date)

        # 写入文件
        FileUtils.write_file(daily_file_path, template_content)

        # 输出成功消息
        relative_path = FileUtils.get_relative_path(daily_file_path)
        print(f"Created daily file: {relative_path}")

    except Exception as e:
        print(f"Error creating daily file: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()