#!/usr/bin/env python3
"""
Daily Start Script - Python版本

创建每日日记文件，提供比bash版本更好的稳定性和错误处理。
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_week_folder_name():
    """计算当前周的文件夹名称 (YYYY_MMDD-MMDD)"""
    today = datetime.now()

    # 获取本周一的日期 (weekday(): Monday=0, Sunday=6)
    days_to_monday = today.weekday()
    monday = today - timedelta(days=days_to_monday)
    sunday = monday + timedelta(days=6)

    # 格式化文件夹名称
    monday_str = monday.strftime("%m%d")
    sunday_str = sunday.strftime("%m%d")
    year = monday.strftime("%Y")

    folder_name = f"{year}_{monday_str}-{sunday_str}"

    print(f"今天是星期{today.weekday() + 1}")
    print(f"本周一: {monday.strftime('%Y-%m-%d')}")
    print(f"本周日: {sunday.strftime('%Y-%m-%d')}")
    print(f"周文件夹: {folder_name}")

    return folder_name


def create_daily_file():
    """创建每日日记文件"""
    try:
        # 获取当前工作目录
        current_dir = Path.cwd()
        print(f"工作目录: {current_dir}")

        # 计算周文件夹名称
        folder_name = get_week_folder_name()
        week_folder = current_dir / "weeks" / folder_name

        # 创建周文件夹
        week_folder.mkdir(parents=True, exist_ok=True)
        print(f"目录已创建/存在: {week_folder}")

        # 创建每日文件名
        today = datetime.now()
        daily_filename = today.strftime("%Y_%m_%d.md")
        daily_file = week_folder / daily_filename

        print(f"目标文件: {daily_file}")

        # 检查文件是否已存在
        if daily_file.exists():
            print(f"每日文件已存在: {daily_file}")
            print(f"文件信息: {daily_file.stat()}")
            return True

        # 创建日记模板内容
        header_date = today.strftime("%m%d")
        template_content = f"""# {header_date} Journal

## video


## newsletter

[] AI Valley

[] The Keyword

## braindump


## output


"""

        # 写入文件
        daily_file.write_text(template_content, encoding='utf-8')

        print(f"✓ 成功创建每日文件: {daily_file}")
        print(f"文件信息: {daily_file.stat()}")

        return True

    except Exception as e:
        print(f"错误: 创建每日文件时发生异常: {e}", file=sys.stderr)
        return False


def main():
    """主函数"""
    print("=== Daily Start - Python版本 ===")

    success = create_daily_file()

    if success:
        print("\n✓ 每日文件创建完成")
        return 0
    else:
        print("\n✗ 每日文件创建失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())