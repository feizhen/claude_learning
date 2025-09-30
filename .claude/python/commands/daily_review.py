#!/usr/bin/env python3
"""
Daily Review Command
分析当前日期的日记文件并生成每日总结的Python实现。

Reviews the current day's markdown file content and updates the `## review` section
with a comprehensive summary including learning habits analysis and content insights.
"""

import sys
import os
import datetime
from typing import Dict, Optional

# 添加父目录到Python路径，以便导入core模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils
from core.file_utils import FileUtils
from core.content_parser import ContentParser
from core.templates import Templates


class DailyReviewAnalyzer:
    """每日总结分析器。"""

    def __init__(self, file_content: str):
        self.content = file_content
        self.sections = ContentParser.extract_all_sections(file_content)

    def analyze_learning_habits(self) -> Dict[str, any]:
        """分析学习习惯。"""
        video_content = self.sections.get('video', '')
        newsletter_content = self.sections.get('newsletter', '')
        braindump_content = self.sections.get('braindump', '')
        output_content = self.sections.get('output', '')

        # 计算内容多样性
        content_diversity = 0
        content_details = []

        if video_content:
            content_diversity += 1
            content_details.append("✅ 视频学习：包含实用的学习视频内容")
        else:
            content_details.append("⚪ 视频学习：今日未观看学习视频")

        if newsletter_content:
            content_diversity += 1
            content_details.append("✅ 阅读输入：关注行业动态和知识更新")
        else:
            content_details.append("⚪ 阅读输入：今日未进行阅读学习")

        if braindump_content:
            content_diversity += 1
            braindump_lines = ContentParser.count_section_items(self.content, 'braindump')
            if braindump_lines >= 3:
                content_details.append(f"✅ 深度思考：记录了丰富的思考和洞察 ({braindump_lines} 条)")
            else:
                content_details.append(f"⚠️ 深度思考：有思考记录但相对较少 ({braindump_lines} 条)")
        else:
            content_details.append("⚪ 深度思考：今日缺少思考和洞察记录")

        if output_content:
            content_diversity += 1
            content_details.append("✅ 学习输出：有实际的学习成果产出")
        else:
            content_details.append("⚪ 学习输出：今日未产生学习输出")

        # 计算评分
        habits_score = content_diversity * 25

        # 生成学习状态评价
        if content_diversity >= 3:
            status = "🎯 **学习状态**: 今日学习内容均衡，输入输出兼备，学习习惯良好"
        elif content_diversity >= 2:
            status = "📈 **学习状态**: 今日学习有一定成效，建议补充缺失的学习维度"
        else:
            status = "🔄 **学习状态**: 今日学习内容较少，建议明日加强学习投入"

        return {
            'score': habits_score,
            'diversity': content_diversity,
            'details': content_details,
            'status': status
        }

    def extract_content_insights(self) -> str:
        """提取内容洞察。"""
        insights = []

        # 提取视频学习重点
        video_content = self.sections.get('video', '')
        if video_content:
            insights.append("**视频学习重点:**")
            lines = video_content.split('\n')
            video_items = [line for line in lines if line.strip().startswith('-')][:3]
            for item in video_items:
                insights.append(item)
            insights.append("")

        # 提取思考洞察
        braindump_content = self.sections.get('braindump', '')
        if braindump_content:
            lines = braindump_content.split('\n')
            key_insights = [line for line in lines if any(keyword in line for keyword in
                           ['洞察', '发现', '体验', '感受', '总结', '思考'])][:3]
            if key_insights:
                insights.append("**关键洞察:**")
                for insight in key_insights:
                    if insight.strip() and not insight.strip().startswith('='):
                        insights.append(f"- {insight.strip()}")
                insights.append("")

        # 提取项目进展
        output_content = self.sections.get('output', '')
        if output_content:
            insights.append("**学习成果:**")
            lines = output_content.split('\n')[:3]
            for line in lines:
                if line.strip() and not line.strip().startswith('='):
                    insights.append(f"- {line.strip()}")
            insights.append("")

        return '\n'.join(insights) if insights else "今日学习内容较为基础，建议增加思考和总结的深度。"

    def generate_recommendations(self, diversity: int) -> str:
        """生成改进建议。"""
        recommendations = ["**明日建议:**"]

        if not self.sections.get('video'):
            recommendations.append("- 📹 考虑观看1-2个技术相关视频或教程")

        if not self.sections.get('newsletter'):
            recommendations.append("- 📰 阅读行业newsletter或技术文章")

        if not self.sections.get('braindump') or len(self.sections.get('braindump', '').split('\n')) < 3:
            recommendations.append("- 💭 增加深度思考，记录更多洞察和想法")

        if not self.sections.get('output'):
            recommendations.append("- 📝 尝试将学习内容转化为具体输出")

        # 基于内容的特定建议
        braindump_content = self.sections.get('braindump', '')
        if braindump_content and '产品' in braindump_content:
            recommendations.append("- 🚀 继续深化产品思维和用户体验思考")

        if self.sections.get('output') and any(keyword in self.sections.get('output', '') for keyword in ['项目', 'WayToAce']):
            recommendations.append("- 🎯 持续推进项目关键功能开发")

        return '\n'.join(recommendations)


def main():
    """主函数，执行daily-review命令逻辑。"""
    try:
        # 获取当前日期
        current_date = DateUtils.get_current_date()

        # 获取当前周的周一和周日
        monday, sunday = DateUtils.get_week_range(current_date)

        # 格式化周文件夹名称和日记文件路径
        folder_name = DateUtils.format_week_folder_name(monday, sunday)
        week_folder = FileUtils.get_week_folder_path(folder_name)
        daily_filename = DateUtils.format_daily_filename(current_date)
        daily_file_path = FileUtils.get_daily_file_path(week_folder, daily_filename)

        # 检查日记文件是否存在
        if not FileUtils.file_exists(daily_file_path):
            relative_path = FileUtils.get_relative_path(daily_file_path)
            print(f"Daily file does not exist: {relative_path}")
            print("Please run /daily-start first to create the daily file.")
            sys.exit(1)

        # 读取文件内容
        content = FileUtils.read_file(daily_file_path)
        if not content:
            print("Failed to read daily file content.")
            sys.exit(1)

        relative_path = FileUtils.get_relative_path(daily_file_path)
        print(f"Reading and analyzing content from: {relative_path}")

        # 检查是否已有review章节
        if ContentParser.has_section(content, 'review'):
            print(f"Review section already exists in {relative_path}")
            print("Current content:")
            existing_review = ContentParser.extract_section(content, 'review')
            print(existing_review)
            print()

            # 询问是否重新生成（在实际使用中可能需要交互式输入）
            # 这里为了简化，直接重新生成
            print("Regenerating review section...")
            content = ContentParser.remove_section(content, 'review')

        # 分析内容
        analyzer = DailyReviewAnalyzer(content)

        # 检查是否有内容可分析
        if not any(analyzer.sections.values()):
            review_content = Templates.daily_review_template(
                "**今日学习记录为空**\n\n建议明日开始记录学习内容。",
                "",
                "",
                "建议明日记录：\n- 📹 观看的学习视频\n- 📰 阅读的文章和资讯\n- 💭 思考和洞察记录\n- 📝 学习输出和项目进展"
            )
        else:
            # 分析学习习惯
            habits_analysis = analyzer.analyze_learning_habits()

            # 生成活动总结
            activity_summary = []
            if analyzer.sections.get('video'):
                activity_summary.append("- **视频学习**: 观看了技术相关视频和教程内容")

            if analyzer.sections.get('newsletter'):
                newsletter_items = ContentParser.extract_checkbox_items(content, 'newsletter')[1]
                activity_summary.append(f"- **文章阅读**: 完成了 {newsletter_items} 项阅读任务")

            if analyzer.sections.get('braindump'):
                braindump_items = ContentParser.count_section_items(content, 'braindump')
                activity_summary.append(f"- **深度思考**: 记录了 {braindump_items} 条思考和洞察")

            if analyzer.sections.get('output'):
                activity_summary.append("- **学习输出**: 产生了具体的学习成果和项目进展")

            activity_summary_text = '\n'.join(activity_summary) if activity_summary else "今日暂无学习活动记录"

            # 生成习惯分析文本
            habits_text = f"学习习惯评估 ({habits_analysis['score']}/100分):\n"
            habits_text += '\n'.join([f"- {detail}" for detail in habits_analysis['details']])
            habits_text += f"\n\n{habits_analysis['status']}"

            # 提取内容洞察
            insights = analyzer.extract_content_insights()

            # 生成建议
            recommendations = analyzer.generate_recommendations(habits_analysis['diversity'])

            # 生成review内容
            review_content = Templates.daily_review_template(
                activity_summary_text,
                habits_text,
                insights,
                recommendations
            )

        # 添加review章节到文件
        updated_content = content + review_content

        # 写入更新后的内容
        FileUtils.write_file(daily_file_path, updated_content)

        print()
        print("✅ Successfully added comprehensive daily review to", FileUtils.get_relative_path(daily_file_path))
        print()
        print("Review includes:")
        print("- 📊 Learning habits analysis with scoring")
        print("- 🧠 Key insights extraction from content")
        print("- 📈 Personalized recommendations for tomorrow")
        print("- 🎯 Activity progress tracking")

    except Exception as e:
        print(f"Error generating daily review: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()