#!/usr/bin/env python3
"""
Daily Review Script

Analyzes the current day's markdown file content and updates the `review` section
with comprehensive learning habits analysis and content insights.
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DailyReviewAnalyzer:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.weeks_dir = self.base_dir / "weeks"

    def get_week_folder_name(self, date: datetime) -> str:
        """Calculate the week folder name for a given date."""
        # Find Monday of the week
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)

        monday_formatted = monday.strftime("%m%d")
        sunday_formatted = sunday.strftime("%m%d")
        year = monday.strftime("%Y")

        return f"{year}_{monday_formatted}-{sunday_formatted}"

    def get_daily_file_path(self, date: datetime = None) -> Path:
        """Get the path to the daily file for a given date."""
        if date is None:
            date = datetime.now()

        week_folder = self.get_week_folder_name(date)
        daily_filename = date.strftime("%Y_%m_%d.md")

        return self.weeks_dir / week_folder / daily_filename

    def extract_section_content(self, file_content: str, section: str) -> str:
        """Extract content from a specific markdown section."""
        pattern = rf"^## {section}$(.*?)^## \w+"
        match = re.search(pattern, file_content, re.MULTILINE | re.DOTALL)

        if match:
            content = match.group(1).strip()
            return content

        # If no next section found, extract until end of file
        pattern = rf"^## {section}$(.*?)$"
        match = re.search(pattern, file_content, re.MULTILINE | re.DOTALL)

        if match:
            content = match.group(1).strip()
            return content

        return ""

    def count_items_in_section(self, content: str) -> int:
        """Count items (lines starting with -) in a section."""
        if not content:
            return 0
        return len([line for line in content.split('\n') if line.strip().startswith('- ')])

    def count_completed_todos(self, content: str) -> int:
        """Count completed todos (lines with [x])."""
        if not content:
            return 0
        return len(re.findall(r'\[x\]', content, re.IGNORECASE))

    def analyze_learning_habits(self, sections: Dict[str, str]) -> Tuple[int, str]:
        """Analyze learning habits and return score and details."""
        score = 0
        details = []
        content_diversity = 0

        # Video learning analysis
        if sections.get('video', '').strip():
            content_diversity += 1
            details.append("- ✅ 视频学习：包含实用的学习视频内容")
        else:
            details.append("- ⚪ 视频学习：今日未观看学习视频")

        # Newsletter/reading analysis
        newsletter_content = sections.get('newsletter', '')
        if newsletter_content.strip():
            content_diversity += 1
            details.append("- ✅ 阅读输入：关注行业动态和知识更新")
        else:
            details.append("- ⚪ 阅读输入：今日未进行阅读学习")

        # Braindump analysis
        braindump_content = sections.get('braindump', '')
        if braindump_content.strip():
            content_diversity += 1
            braindump_count = self.count_items_in_section(braindump_content)
            if braindump_count >= 3:
                details.append(f"- ✅ 深度思考：记录了丰富的思考和洞察 ({braindump_count} 条)")
            else:
                details.append(f"- ⚠️ 深度思考：有思考记录但相对较少 ({braindump_count} 条)")
        else:
            details.append("- ⚪ 深度思考：今日缺少思考和洞察记录")

        # Output analysis
        output_content = sections.get('output', '')
        if output_content.strip():
            content_diversity += 1
            details.append("- ✅ 学习输出：有实际的学习成果产出")
        else:
            details.append("- ⚪ 学习输出：今日未产生学习输出")

        score = content_diversity * 25

        # Learning state assessment
        if content_diversity >= 3:
            state_msg = "🎯 **学习状态**: 今日学习内容均衡，输入输出兼备，学习习惯良好"
        elif content_diversity >= 2:
            state_msg = "📈 **学习状态**: 今日学习有一定成效，建议补充缺失的学习维度"
        else:
            state_msg = "🔄 **学习状态**: 今日学习内容较少，建议明日加强学习投入"

        details_text = "\n".join(details)
        return score, f"{details_text}\n\n{state_msg}"

    def extract_content_insights(self, sections: Dict[str, str]) -> str:
        """Extract key insights from content."""
        insights = []

        # Video learning insights
        video_content = sections.get('video', '')
        if video_content:
            video_titles = re.findall(r'- \[(.*?)\]', video_content)
            if video_titles:
                insights.append("**视频学习重点:**")
                for title in video_titles[:3]:  # Limit to 3
                    insights.append(f"- {title}")
                insights.append("")

        # Braindump insights
        braindump_content = sections.get('braindump', '')
        if braindump_content:
            # Look for insights sections
            insights_match = re.search(r'insights?:(.*?)(?=\n\n|\n-|\Z)', braindump_content, re.IGNORECASE | re.DOTALL)
            if insights_match:
                insights.append("**关键洞察:**")
                insights.append(insights_match.group(1).strip())
                insights.append("")

            # Look for product thoughts
            product_thoughts = [line for line in braindump_content.split('\n')
                             if any(keyword in line for keyword in ['产品', '体验', '用户', '功能'])]
            if product_thoughts:
                insights.append("**产品思考:**")
                for thought in product_thoughts[:3]:
                    insights.append(thought)
                insights.append("")

        # WayToAce progress
        waytoace_content = sections.get('WayToAce', '')
        if waytoace_content:
            insights.append("**WayToAce 项目进展:**")
            insights.append(waytoace_content)
            insights.append("")

        # Completed todos
        todo_content = sections.get('TODO', '')
        if todo_content:
            completed_todos = [line for line in todo_content.split('\n') if '[x]' in line.lower()]
            if completed_todos:
                insights.append("**今日完成:**")
                for todo in completed_todos[:3]:
                    insights.append(todo)
                insights.append("")

        return "\n".join(insights)

    def generate_recommendations(self, sections: Dict[str, str]) -> str:
        """Generate recommendations for tomorrow."""
        recommendations = ["**明日建议:**"]

        if not sections.get('video', '').strip():
            recommendations.append("- 📹 考虑观看1-2个技术相关视频或教程")

        if not sections.get('newsletter', '').strip():
            recommendations.append("- 📰 阅读行业newsletter或技术文章")

        braindump_lines = self.count_items_in_section(sections.get('braindump', ''))
        if braindump_lines < 3:
            recommendations.append("- 💭 增加深度思考，记录更多洞察和想法")

        if not sections.get('output', '').strip():
            recommendations.append("- 📝 尝试将学习内容转化为具体输出")

        # General recommendations based on patterns
        braindump_content = sections.get('braindump', '')
        if braindump_content and '产品' in braindump_content:
            recommendations.append("- 🚀 继续深化产品思维和用户体验思考")

        if sections.get('WayToAce', ''):
            recommendations.append("- 🎯 持续推进 WayToAce 项目关键功能开发")

        return "\n".join(recommendations)

    def generate_review_content(self, sections: Dict[str, str]) -> str:
        """Generate the complete review content."""
        review_parts = []

        # Activity summary
        activities = []
        if sections.get('video', '').strip():
            activities.append("- **视频学习**: 观看了技术相关视频和教程内容")

        newsletter_content = sections.get('newsletter', '')
        if newsletter_content.strip():
            completed_count = self.count_completed_todos(newsletter_content)
            activities.append(f"- **文章阅读**: 完成了 {completed_count} 项阅读任务")

        braindump_content = sections.get('braindump', '')
        if braindump_content.strip():
            braindump_count = self.count_items_in_section(braindump_content)
            activities.append(f"- **深度思考**: 记录了 {braindump_count} 条思考和洞察")

        if sections.get('output', '').strip():
            activities.append("- **学习输出**: 产生了具体的学习成果和项目进展")

        if sections.get('WayToAce', '').strip():
            activities.append("- **项目推进**: WayToAce 项目取得新进展")

        todo_content = sections.get('TODO', '')
        if todo_content:
            completed_count = self.count_completed_todos(todo_content)
            if completed_count > 0:
                activities.append(f"- **任务完成**: 完成了 {completed_count} 项计划任务")

        if activities:
            review_parts.append("**今日学习活动总结:**")
            review_parts.append("")
            review_parts.extend(activities)
            review_parts.append("")

        # Learning habits analysis
        score, habits_analysis = self.analyze_learning_habits(sections)
        review_parts.append(f"学习习惯评估 ({score}/100分):")
        review_parts.append(habits_analysis)
        review_parts.append("")

        # Content insights
        insights = self.extract_content_insights(sections)
        if insights.strip():
            review_parts.append("**主要收获:**")
            review_parts.append(insights)

        # Recommendations
        recommendations = self.generate_recommendations(sections)
        review_parts.append(recommendations)

        return "\n".join(review_parts)

    def update_daily_review(self, date: datetime = None) -> bool:
        """Update the daily review section for the specified date."""
        daily_file = self.get_daily_file_path(date)

        if not daily_file.exists():
            print(f"Daily file does not exist: {daily_file}")
            print("Please run /daily-start first to create the daily file.")
            return False

        print(f"Reading and analyzing content from: {daily_file}")

        # Read current file content
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract sections
        sections = {
            'video': self.extract_section_content(content, 'video'),
            'newsletter': self.extract_section_content(content, 'newsletter'),
            'braindump': self.extract_section_content(content, 'braindump'),
            'output': self.extract_section_content(content, 'output'),
            'TODO': self.extract_section_content(content, 'TODO'),
            'WayToAce': self.extract_section_content(content, 'WayToAce'),
        }

        # Check if any content exists
        has_content = any(section.strip() for section in sections.values())

        if not has_content:
            review_content = """**今日学习记录为空**

建议明日开始记录学习内容，包括：
- 📹 观看的学习视频
- 📰 阅读的文章和资讯
- 💭 思考和洞察记录
- 📝 学习输出和项目进展"""
        else:
            review_content = self.generate_review_content(sections)

        # Remove existing review section if it exists
        review_pattern = r'\n## review\n.*$'
        content_without_review = re.sub(review_pattern, '', content, flags=re.DOTALL)

        # Add new review section
        new_content = content_without_review.rstrip() + f"\n\n## review\n\n{review_content}\n"

        # Write back to file
        with open(daily_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"\n✅ Successfully added comprehensive daily review to {daily_file}")
        print("\nReview includes:")
        print("- 📊 Learning habits analysis with scoring")
        print("- 🧠 Key insights extraction from content")
        print("- 📈 Personalized recommendations for tomorrow")
        print("- 🎯 Project progress tracking")

        return True


def main():
    """Main entry point for the daily review script."""
    analyzer = DailyReviewAnalyzer()

    # Parse command line arguments for custom date if needed
    target_date = datetime.now()
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {sys.argv[1]}. Use YYYY-MM-DD format.")
            return 1

    success = analyzer.update_daily_review(target_date)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())