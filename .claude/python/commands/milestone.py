#!/usr/bin/env python3
"""
Milestone Report Command
生成学习进度里程碑报告的Python实现。

Generates a comprehensive milestone report based on learning progress,
comparing objectives from `objective.md` with actual learning records from `weeks/` directory.
"""

import sys
import os
import argparse
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# 添加父目录到Python路径，以便导入core模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils
from core.file_utils import FileUtils
from core.content_parser import ContentParser
from core.templates import Templates


class MilestoneAnalyzer:
    """里程碑分析器。"""

    def __init__(self):
        self.stats = {
            'video_count': 0,
            'newsletter_count': 0,
            'braindump_count': 0,
            'active_learning_days': 0,
            'project_outputs': 0,
            'total_files': 0,
            'files_with_review': 0
        }

    def get_learning_start_date(self) -> str:
        """获取学习开始日期。"""
        earliest_file_data = FileUtils.get_earliest_daily_file()
        if earliest_file_data:
            return earliest_file_data[1]
        return "2025-09-15"  # 默认开始日期

    def calculate_current_month(self) -> int:
        """计算当前学习月份。"""
        start_date = DateUtils.parse_filename_date(self.get_learning_start_date().replace('-', '_') + '.md')
        if not start_date:
            start_date = datetime(2025, 9, 15).date()

        current_date = DateUtils.get_current_date()
        months_diff = DateUtils.calculate_months_between(start_date, current_date)

        return max(months_diff + 1, 1)

    def extract_monthly_goals(self, month_num: int) -> Optional[str]:
        """从objective.md提取月度目标。"""
        objective_file = "objective.md"
        if not FileUtils.file_exists(objective_file):
            return None

        content = FileUtils.read_file(objective_file)
        if not content:
            return None

        # 根据月份范围提取相应的目标
        if month_num <= 3:
            # 月 1-3: 基础巩固 + 快速产出
            pattern = r'月 1–3（基础巩固 \+ 快速产出）：(.*?)(?=月 4–6|$)'
        elif month_num <= 6:
            # 月 4-6: 进阶能力 + 用户/业务理解
            pattern = r'月 4–6（进阶能力 \+ 用户.*?）：(.*?)(?=月 7–9|$)'
        elif month_num <= 9:
            # 月 7-9: 扩大影响 + 学术/行业深度
            pattern = r'月 7–9（扩大影响 \+ 学术.*?）：(.*?)(?=月 10–12|$)'
        else:
            # 月 10-12: 包装、面试准备、跳槽/转岗
            pattern = r'月 10–12（包装、面试准备.*?）：(.*?)(?=四、每月|$)'

        import re
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    def aggregate_learning_content(self) -> Dict[str, int]:
        """聚合学习内容统计。"""
        daily_files = FileUtils.find_daily_files()
        learning_days = set()

        for file_path in daily_files:
            self.stats['total_files'] += 1

            content = FileUtils.read_file(file_path)
            if not content:
                continue

            sections = ContentParser.extract_all_sections(content)
            filename = os.path.basename(file_path)

            # 统计各类内容
            if sections.get('video'):
                self.stats['video_count'] += 1
                learning_days.add(filename[:10])

            if sections.get('newsletter'):
                self.stats['newsletter_count'] += 1
                learning_days.add(filename[:10])

            if sections.get('braindump'):
                self.stats['braindump_count'] += 1
                learning_days.add(filename[:10])

            if sections.get('output'):
                # 检查项目输出关键词
                output_content = sections['output']
                project_keywords = ['项目', '产品', '案例', 'demo', 'mvp', '实现', '开发', '搭建']
                if any(keyword in output_content.lower() for keyword in project_keywords):
                    self.stats['project_outputs'] += 1

            # 检查是否有review
            if ContentParser.has_section(content, 'review'):
                review_content = ContentParser.extract_section(content, 'review')
                if review_content and review_content.strip():
                    self.stats['files_with_review'] += 1

        self.stats['active_learning_days'] = len(learning_days)
        return self.stats

    def evaluate_learning_habits(self) -> str:
        """评估学习习惯。"""
        start_date = DateUtils.parse_filename_date(self.get_learning_start_date().replace('-', '_') + '.md')
        if not start_date:
            start_date = datetime(2025, 9, 15).date()

        current_date = DateUtils.get_current_date()
        days_since_start = DateUtils.calculate_days_between(start_date, current_date) + 1

        # 计算学习频率
        learning_frequency_pct = (self.stats['active_learning_days'] * 100 // days_since_start) if days_since_start > 0 else 0

        # 计算总结完成率
        review_completion_pct = (self.stats['files_with_review'] * 100 // max(self.stats['total_files'], 1))

        evaluation = [
            "## 📈 学习习惯评估\n",
            "### 一致性评估\n",
            f"- **学习频率**: {learning_frequency_pct}% ({self.stats['active_learning_days']}/{days_since_start} 天)\n"
        ]

        if learning_frequency_pct >= 80:
            evaluation.append("  - ✅ 学习频率很高，保持良好习惯\n")
        elif learning_frequency_pct >= 60:
            evaluation.append("  - ⚠️ 学习频率中等，可以进一步提升\n")
        else:
            evaluation.append("  - ❌ 学习频率偏低，需要建立更规律的学习习惯\n")

        # 内容平衡度评估
        total_content = self.stats['video_count'] + self.stats['newsletter_count'] + self.stats['braindump_count']
        evaluation.append("- **内容平衡度**:\n")

        if total_content > 0:
            video_pct = self.stats['video_count'] * 100 // total_content
            newsletter_pct = self.stats['newsletter_count'] * 100 // total_content
            braindump_pct = self.stats['braindump_count'] * 100 // total_content

            evaluation.extend([
                f"  - 视频学习: {video_pct}% ({self.stats['video_count']})\n",
                f"  - 文章阅读: {newsletter_pct}% ({self.stats['newsletter_count']})\n",
                f"  - 思考记录: {braindump_pct}% ({self.stats['braindump_count']})\n"
            ])

            # 检查平衡性
            if all(count > 0 for count in [self.stats['video_count'], self.stats['newsletter_count'], self.stats['braindump_count']]):
                evaluation.append("  - ✅ 内容类型分布均衡\n")
            else:
                if self.stats['video_count'] == 0:
                    evaluation.append("  - ⚠️ 缺少视频学习，建议增加实践教程观看\n")
                if self.stats['newsletter_count'] == 0:
                    evaluation.append("  - ⚠️ 缺少文章阅读，建议关注行业动态\n")
                if self.stats['braindump_count'] == 0:
                    evaluation.append("  - ⚠️ 缺少思考记录，建议增加反思和总结\n")
        else:
            evaluation.append("  - ❌ 缺少学习内容记录\n")

        evaluation.extend([
            "\n### 质量评估\n",
            f"- **总结习惯**: {review_completion_pct}% ({self.stats['files_with_review']}/{self.stats['total_files']} 天)\n"
        ])

        if review_completion_pct >= 80:
            evaluation.append("  - ✅ 每日总结习惯很好\n")
        elif review_completion_pct >= 50:
            evaluation.append("  - ⚠️ 总结习惯需要加强\n")
        else:
            evaluation.append("  - ❌ 缺少每日总结，建议使用 /daily-review 命令\n")

        # 实践转化评估
        evaluation.append("- **实践转化**: ")
        if self.stats['project_outputs'] >= 5:
            evaluation.append("项目实践活动丰富\n  - ✅ 理论学习向实践转化良好\n")
        elif self.stats['project_outputs'] > 0:
            evaluation.append("有一定的项目实践\n  - ⚠️ 可以增加更多实际项目开发\n")
        else:
            evaluation.append("缺少项目实践记录\n  - ❌ 建议将学习内容应用到具体项目中\n")

        return ''.join(evaluation)

    def analyze_gaps_and_recommendations(self, current_month: int, monthly_goals: str) -> str:
        """分析差距并生成建议。"""
        analysis = ["## ⚠️ 差距分析\n\n"]

        if not monthly_goals:
            analysis.append("- 当前阶段目标不明确，建议明确当前月份的具体目标\n")
        else:
            analysis.extend([
                "- 对照当前月份目标，分析实际完成情况：\n",
                "```\n",
                monthly_goals,
                "\n```\n"
            ])

        analysis.extend([
            "\n## 🚀 改进建议\n\n",
            "### 基于学习习惯的改进建议\n\n"
        ])

        # 基于统计数据生成具体建议
        start_date = DateUtils.parse_filename_date(self.get_learning_start_date().replace('-', '_') + '.md')
        if not start_date:
            start_date = datetime(2025, 9, 15).date()

        current_date = DateUtils.get_current_date()
        days_since_start = DateUtils.calculate_days_between(start_date, current_date) + 1
        learning_frequency_pct = (self.stats['active_learning_days'] * 100 // days_since_start) if days_since_start > 0 else 0

        if learning_frequency_pct < 60:
            analysis.extend([
                f"- **提高学习频率**: 目前学习频率为 {learning_frequency_pct}%，建议：\n",
                "  - 设置固定的学习时间段（如每日早晨或晚上）\n",
                "  - 使用 /daily-start 命令创建每日学习记录\n",
                "  - 即使学习时间有限，也要保持记录的连续性\n\n"
            ])

        if self.stats['video_count'] < 3:
            analysis.append("- **增加视频学习**: 建议每周观看 2-3 个技术相关视频教程\n")

        if self.stats['newsletter_count'] < 5:
            analysis.append("- **增加文章阅读**: 建议订阅 AI/技术相关 newsletter，保持行业敏感度\n")

        if self.stats['braindump_count'] < self.stats['active_learning_days']:
            analysis.extend([
                "- **加强深度思考**: 每日学习后，在 braindump 部分记录：\n",
                "  - 学到了什么新知识\n",
                "  - 如何与之前的知识连接\n",
                "  - 可以应用到哪些实际场景\n\n"
            ])

        if self.stats['project_outputs'] < 2:
            analysis.extend([
                "- **增加实践项目**: 将学习内容转化为实际输出：\n",
                "  - 搭建简单的 demo 或 MVP\n",
                "  - 写技术博客或总结文档\n",
                "  - 参与开源项目或社区讨论\n\n"
            ])

        review_completion_pct = (self.stats['files_with_review'] * 100 // max(self.stats['total_files'], 1))
        if review_completion_pct < 80:
            analysis.extend([
                f"- **完善每日总结**: 当前总结完成率 {review_completion_pct}%，建议：\n",
                "  - 每日结束时使用 /daily-review 命令\n",
                "  - 回顾当天的学习收获和不足\n",
                "  - 规划第二天的学习重点\n\n"
            ])

        analysis.extend([
            "### 下一步行动\n\n",
            "- 定期使用 /milestone 命令（建议每周一次）监控学习习惯\n",
            "- 根据评估结果调整学习策略和时间分配\n",
            "- 寻找学习伙伴或加入相关社群，增加交流和反馈\n",
            "- 设定具体的月度/周度学习目标，并跟踪完成情况\n"
        ])

        return ''.join(analysis)

    def identify_achievements(self) -> str:
        """识别主要成就。"""
        achievements = ["## ✅ 主要成就\n\n"]
        found_achievements = False

        daily_files = FileUtils.find_daily_files()

        for file_path in daily_files:
            content = FileUtils.read_file(file_path)
            if not content:
                continue

            review_content = ContentParser.extract_section(content, 'review')
            if not review_content:
                continue

            # 查找成就关键词
            achievement_keywords = ['完成', '学会', '掌握', '实现', '搭建', '成功', '达成']
            achievement_lines = []

            for line in review_content.split('\n'):
                if any(keyword in line for keyword in achievement_keywords):
                    achievement_lines.append(line.strip())

            if achievement_lines:
                filename = os.path.basename(file_path)
                file_date = filename.replace('_', '-').replace('.md', '')
                achievements.append(f"**{file_date}:**\n")
                for line in achievement_lines[:3]:  # 限制每天最多3条
                    achievements.append(f"- {line}\n")
                achievements.append("\n")
                found_achievements = True

        if not found_achievements:
            achievements.extend([
                "- 继续记录每日学习成果，形成可展示的成就记录\n",
                "- 将学习内容转化为具体的项目输出或技能证明\n"
            ])

        return ''.join(achievements)


def parse_arguments():
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description='Generate milestone report')
    parser.add_argument('--save', help='Save report to file')
    parser.add_argument('--month', type=int, help='Target month number')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='Output format')

    return parser.parse_args()


def main():
    """主函数，执行milestone命令逻辑。"""
    try:
        args = parse_arguments()

        # 创建分析器
        analyzer = MilestoneAnalyzer()

        # 获取当前月份
        current_month = args.month if args.month else analyzer.calculate_current_month()

        # 获取学习开始日期
        start_date = analyzer.get_learning_start_date()
        current_date = DateUtils.format_chinese_date(DateUtils.get_current_date())

        print("=== Starting milestone report generation ===", file=sys.stderr)
        print(f"Current month: {current_month}", file=sys.stderr)
        print(f"Start date: {start_date}, Current date: {current_date}", file=sys.stderr)

        # 提取月度目标
        print("Extracting monthly goals...", file=sys.stderr)
        monthly_goals = analyzer.extract_monthly_goals(current_month)

        # 聚合学习内容
        print("Aggregating learning content...", file=sys.stderr)
        stats = analyzer.aggregate_learning_content()

        print(f"Stats: videos={stats['video_count']}, newsletters={stats['newsletter_count']}, "
              f"braindumps={stats['braindump_count']}, days={stats['active_learning_days']}, "
              f"projects={stats['project_outputs']}", file=sys.stderr)

        # 生成报告各部分
        print("Generating report sections...", file=sys.stderr)

        # 报告标题和基本信息
        report_content = [
            f"# Milestone Report - {current_date}\n\n",
            "## 🎯 当前阶段\n\n",
            f"- **计划月份**: 月 {current_month}\n",
            f"- **学习开始日期**: {start_date}\n"
        ]

        if monthly_goals:
            report_content.extend([
                "- **主要目标**:\n",
                f"```\n{monthly_goals}\n```\n"
            ])
        else:
            report_content.append("- **主要目标**: 当前月份目标待明确\n")

        report_content.extend([
            "\n## 📊 学习统计\n\n",
            f"- **总学习天数**: {stats['active_learning_days']} 天\n",
            f"- **视频学习**: {stats['video_count']} 个视频/教程\n",
            f"- **文章阅读**: {stats['newsletter_count']} 篇文章/通讯\n",
            f"- **思考记录**: {stats['braindump_count']} 次记录\n",
            f"- **项目产出**: {stats['project_outputs']} 项相关活动\n\n"
        ])

        # 添加主要成就
        achievements = analyzer.identify_achievements()
        report_content.append(achievements)
        report_content.append("\n")

        # 添加学习习惯评估
        habits_evaluation = analyzer.evaluate_learning_habits()
        report_content.append(habits_evaluation)
        report_content.append("\n")

        # 添加差距分析和建议
        gap_analysis = analyzer.analyze_gaps_and_recommendations(current_month, monthly_goals)
        report_content.append(gap_analysis)

        # 生成最终报告
        final_report = ''.join(report_content)

        # 输出报告
        if args.save:
            FileUtils.write_file(args.save, final_report)
            print(f"Milestone report saved to: {args.save}")
        else:
            print(final_report)

        print("=== Milestone report generation completed ===", file=sys.stderr)

    except Exception as e:
        print(f"Error generating milestone report: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()