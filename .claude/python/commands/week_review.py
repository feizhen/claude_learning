#!/usr/bin/env python3
"""
Week Review Command
生成周总结的Python实现。

Reviews all daily files in the current week's folder and creates
a comprehensive weekly summary in `week_review.md`.
"""

import sys
import os
from typing import List, Dict, Optional

# 添加父目录到Python路径，以便导入core模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils
from core.file_utils import FileUtils
from core.content_parser import ContentParser
from core.templates import Templates


class WeeklyReviewGenerator:
    """周总结生成器。"""

    def __init__(self, week_folder: str, monday: str, sunday: str, folder_name: str):
        self.week_folder = week_folder
        self.monday = monday
        self.sunday = sunday
        self.folder_name = folder_name

    def find_daily_files(self) -> List[str]:
        """查找本周的所有日记文件。"""
        if not FileUtils.directory_exists(self.week_folder):
            return []

        daily_files = FileUtils.get_files_in_directory(self.week_folder, "????_??_??.md")
        return sorted(daily_files)

    def process_daily_file(self, file_path: str) -> Dict[str, any]:
        """处理单个日记文件。"""
        filename = os.path.basename(file_path)

        # 解析日期
        file_date = DateUtils.parse_filename_date(filename)
        if not file_date:
            return None

        display_date = DateUtils.format_display_date(file_date)

        # 读取文件内容
        content = FileUtils.read_file(file_path)
        if not content:
            return None

        # 提取各个章节内容
        sections = ContentParser.extract_all_sections(content)

        # 过滤空内容并格式化
        formatted_sections = {}
        for section_name, section_content in sections.items():
            if section_content and section_content.strip():
                # 清理内容（移除日期分隔符等）
                cleaned_content = self._clean_section_content(section_content)
                if cleaned_content:
                    formatted_sections[section_name] = cleaned_content

        return {
            'date': file_date,
            'display_date': display_date,
            'filename': filename,
            'sections': formatted_sections
        }

    def _clean_section_content(self, content: str) -> str:
        """清理章节内容。"""
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # 跳过日期分隔符行
            if line.strip().startswith('=== 2') or line.strip() == '':
                continue
            # 跳过comment行
            if line.strip().startswith('<!-- Review will be added'):
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def generate_daily_summaries(self, daily_files_data: List[Dict]) -> str:
        """生成每日摘要部分。"""
        if not daily_files_data:
            return "No daily journal entries found for this week.\n\n"

        summaries = ["## Daily Summaries\n\n"]

        for day_data in daily_files_data:
            summaries.append(f"### {day_data['display_date']}\n\n")

            sections = day_data['sections']

            # 按顺序处理各个章节
            section_order = ['video', 'newsletter', 'braindump', 'output', 'review']
            section_titles = {
                'video': 'Videos/Learning:',
                'newsletter': 'Newsletter/Reading:',
                'braindump': 'Ideas/Thoughts:',
                'output': 'Learning Output:',
                'review': 'Daily Review:'
            }

            for section_name in section_order:
                if section_name in sections:
                    summaries.append(f"**{section_titles[section_name]}**\n")
                    summaries.append(f"{sections[section_name]}\n\n")

            summaries.append("---\n\n")

        return ''.join(summaries)

    def generate_weekly_insights_section(self) -> str:
        """生成周度洞察部分。"""
        return """
## Weekly Insights

<!-- Add your weekly reflections, key learnings, and insights here -->

## Action Items for Next Week

<!-- Add action items and goals for the upcoming week -->

"""

    def generate_review(self) -> str:
        """生成完整的周总结。"""
        # 查找本周的日记文件
        daily_files = self.find_daily_files()

        # 处理每个日记文件
        daily_files_data = []
        for file_path in daily_files:
            day_data = self.process_daily_file(file_path)
            if day_data:
                daily_files_data.append(day_data)

        # 生成模板开头
        monday_date = DateUtils.parse_filename_date(f"{self.folder_name.split('_')[0]}_01_01.md")
        if not monday_date:
            # fallback: 使用当前周一
            monday_date, _ = DateUtils.get_week_range()

        sunday_date = monday_date + DateUtils.calculate_days_between(monday_date, monday_date) + 6

        review_content = Templates.week_review_template(
            monday_date, sunday_date, self.folder_name
        )

        # 生成每日摘要
        daily_summaries = self.generate_daily_summaries(daily_files_data)

        # 生成周度洞察部分
        weekly_insights = self.generate_weekly_insights_section()

        # 组合完整内容
        full_content = review_content + daily_summaries + weekly_insights

        return full_content


def main():
    """主函数，执行week-review命令逻辑。"""
    try:
        # 获取当前日期
        current_date = DateUtils.get_current_date()

        # 获取当前周的周一和周日
        monday, sunday = DateUtils.get_week_range(current_date)

        # 格式化周文件夹名称
        folder_name = DateUtils.format_week_folder_name(monday, sunday)
        week_folder = FileUtils.get_week_folder_path(folder_name)

        # 检查周文件夹是否存在
        if not FileUtils.directory_exists(week_folder):
            relative_path = FileUtils.get_relative_path(week_folder)
            print(f"Week folder does not exist: {relative_path}")
            print("Please run /week-start first to create the weekly folder.")
            sys.exit(1)

        # 生成周总结文件路径
        review_file = os.path.join(week_folder, "week_review.md")

        print(f"Generating weekly review for: {FileUtils.get_relative_path(week_folder)}")

        # 创建周总结生成器
        generator = WeeklyReviewGenerator(
            week_folder,
            DateUtils.format_display_date(monday),
            DateUtils.format_display_date(sunday),
            folder_name
        )

        # 查找日记文件
        daily_files = generator.find_daily_files()

        if daily_files:
            print("Found daily files to review:")
            for file_path in daily_files:
                print(f"  {FileUtils.get_relative_path(file_path)}")
        else:
            print("No daily files found in", FileUtils.get_relative_path(week_folder))

        # 生成周总结内容
        review_content = generator.generate_review()

        # 写入文件
        FileUtils.write_file(review_file, review_content)

        print(f"Weekly review created: {FileUtils.get_relative_path(review_file)}")
        print("Please review and add your weekly insights and action items.")

    except Exception as e:
        print(f"Error generating weekly review: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()