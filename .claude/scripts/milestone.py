#!/usr/bin/env python3
"""
Milestone Report Script

Generates a comprehensive milestone report based on learning progress,
comparing objectives from `objective.md` with actual learning records
from `weeks/` directory.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict


class MilestoneAnalyzer:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.weeks_dir = self.base_dir / "weeks"
        self.objective_file = self.base_dir / "objective.md"

    def get_learning_start_date(self) -> datetime:
        """Calculate learning start date from earliest file in weeks/."""
        daily_files = list(self.weeks_dir.glob("*/????_??_??.md"))

        if not daily_files:
            return datetime(2025, 9, 15)  # Default start date

        # Sort by filename to get earliest
        daily_files.sort(key=lambda x: x.name)
        earliest_file = daily_files[0]

        # Extract date from filename (YYYY_MM_DD.md)
        filename = earliest_file.stem
        try:
            year, month, day = map(int, filename.split('_'))
            return datetime(year, month, day)
        except (ValueError, IndexError):
            return datetime(2025, 9, 15)

    def calculate_current_month(self) -> int:
        """Calculate which month of the learning journey we're in."""
        start_date = self.get_learning_start_date()
        current_date = datetime.now()

        # Calculate months difference
        months_diff = (current_date.year - start_date.year) * 12 + \
                     (current_date.month - start_date.month)

        # Return month number (1-based)
        return max(1, months_diff + 1)

    def extract_monthly_goals(self, month_num: int) -> str:
        """Extract goals for the current month from objective.md."""
        if not self.objective_file.exists():
            return "目标文件 objective.md 未找到"

        try:
            with open(self.objective_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Define month ranges based on learning plan structure
            if month_num <= 3:
                # Months 1-3: 基础巩固 + 快速产出
                pattern = r'月 1–3（基础巩固 \+ 快速产出）(.*?)(?=月 4–6|$)'
            elif month_num <= 6:
                # Months 4-6: 进阶能力 + 用户/业务理解
                pattern = r'月 4–6（进阶能力 \+ 用户(.*?)(?=月 7–9|$)'
            elif month_num <= 9:
                # Months 7-9: 扩大影响 + 学术/行业深度
                pattern = r'月 7–9（扩大影响 \+ 学术(.*?)(?=月 10–12|$)'
            else:
                # Months 10-12: 专业成熟 + 领导力/行业影响力
                pattern = r'月 10–12（专业成熟 \+ 领导力(.*?)$'

            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return f"未找到第 {month_num} 月的目标内容"

        except Exception as e:
            return f"读取目标文件时出错: {e}"

    def collect_learning_activities(self, target_month: Optional[int] = None) -> Dict[str, Any]:
        """Collect and analyze learning activities from daily files."""
        activities = {
            'total_days': 0,
            'active_days': 0,
            'video_learning': [],
            'reading_materials': [],
            'deep_thoughts': [],
            'outputs': [],
            'projects': [],
            'weekly_summaries': []
        }

        current_month = self.calculate_current_month()
        analysis_month = target_month if target_month else current_month

        # Get all daily files
        daily_files = list(self.weeks_dir.glob("*/????_??_??.md"))

        for file_path in daily_files:
            try:
                # Parse file date
                filename = file_path.stem
                year, month, day = map(int, filename.split('_'))
                file_date = datetime(year, month, day)

                # Calculate which learning month this file belongs to
                start_date = self.get_learning_start_date()
                file_month = (file_date.year - start_date.year) * 12 + \
                           (file_date.month - start_date.month) + 1

                # Skip files not in target month if specified
                if target_month and file_month != analysis_month:
                    continue

                activities['total_days'] += 1

                # Read and parse file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                has_content = False

                # Extract video learning
                video_section = self._extract_section(content, 'video')
                if video_section.strip():
                    has_content = True
                    video_items = self._extract_list_items(video_section)
                    activities['video_learning'].extend(video_items)

                # Extract reading materials
                newsletter_section = self._extract_section(content, 'newsletter')
                if newsletter_section.strip():
                    has_content = True
                    reading_items = self._extract_completed_items(newsletter_section)
                    activities['reading_materials'].extend(reading_items)

                # Extract deep thoughts
                braindump_section = self._extract_section(content, 'braindump')
                if braindump_section.strip():
                    has_content = True
                    thought_items = self._extract_list_items(braindump_section)
                    activities['deep_thoughts'].extend(thought_items)

                # Extract outputs
                output_section = self._extract_section(content, 'output')
                if output_section.strip():
                    has_content = True
                    output_items = self._extract_list_items(output_section)
                    activities['outputs'].extend(output_items)

                # Extract project progress
                waytoace_section = self._extract_section(content, 'WayToAce')
                if waytoace_section.strip():
                    has_content = True
                    activities['projects'].append({
                        'date': file_date.strftime('%Y-%m-%d'),
                        'content': waytoace_section.strip()
                    })

                if has_content:
                    activities['active_days'] += 1

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue

        # Collect weekly summaries
        week_reviews = list(self.weeks_dir.glob("*/week_review.md"))
        for review_file in week_reviews:
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                activities['weekly_summaries'].append({
                    'week': review_file.parent.name,
                    'content': content[:500] + "..." if len(content) > 500 else content
                })
            except Exception as e:
                print(f"Error reading week review {review_file}: {e}")

        return activities

    def _extract_section(self, content: str, section: str) -> str:
        """Extract content from a specific markdown section."""
        pattern = rf"^## {re.escape(section)}$(.*?)(?=^## |\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_list_items(self, content: str) -> List[str]:
        """Extract list items (lines starting with -)."""
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                items.append(line[2:].strip())
        return items

    def _extract_completed_items(self, content: str) -> List[str]:
        """Extract completed items (lines with [x])."""
        items = []
        for line in content.split('\n'):
            if '[x]' in line.lower():
                items.append(line.strip())
        return items

    def calculate_learning_habits_score(self, activities: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate learning habits score and analysis."""
        total_days = activities['total_days']
        active_days = activities['active_days']

        if total_days == 0:
            return {'score': 0, 'analysis': '暂无学习记录'}

        # Calculate various metrics
        activity_rate = (active_days / total_days) * 100
        video_count = len(activities['video_learning'])
        reading_count = len(activities['reading_materials'])
        thoughts_count = len(activities['deep_thoughts'])
        outputs_count = len(activities['outputs'])

        # Scoring algorithm
        score = 0
        analysis_points = []

        # Activity consistency (40 points max)
        if activity_rate >= 80:
            score += 40
            analysis_points.append(f"✅ 学习活跃度优秀: {activity_rate:.1f}% ({active_days}/{total_days}天)")
        elif activity_rate >= 60:
            score += 30
            analysis_points.append(f"🟡 学习活跃度良好: {activity_rate:.1f}% ({active_days}/{total_days}天)")
        else:
            score += 20
            analysis_points.append(f"🔄 学习活跃度需提升: {activity_rate:.1f}% ({active_days}/{total_days}天)")

        # Content diversity (30 points max)
        diversity_score = 0
        if video_count > 0:
            diversity_score += 8
            analysis_points.append(f"📹 视频学习: {video_count} 个")
        if reading_count > 0:
            diversity_score += 8
            analysis_points.append(f"📚 阅读材料: {reading_count} 项")
        if thoughts_count > 0:
            diversity_score += 7
            analysis_points.append(f"💭 深度思考: {thoughts_count} 条")
        if outputs_count > 0:
            diversity_score += 7
            analysis_points.append(f"📝 学习输出: {outputs_count} 项")

        score += diversity_score

        # Output quality (30 points max)
        if outputs_count >= 5:
            score += 30
            analysis_points.append("🎯 输出质量: 优秀 (≥5项)")
        elif outputs_count >= 3:
            score += 20
            analysis_points.append("🎯 输出质量: 良好 (3-4项)")
        elif outputs_count >= 1:
            score += 10
            analysis_points.append("🎯 输出质量: 基础 (1-2项)")
        else:
            analysis_points.append("⚠️ 缺少学习输出")

        return {
            'score': min(score, 100),
            'activity_rate': activity_rate,
            'analysis': analysis_points,
            'metrics': {
                'total_days': total_days,
                'active_days': active_days,
                'video_count': video_count,
                'reading_count': reading_count,
                'thoughts_count': thoughts_count,
                'outputs_count': outputs_count
            }
        }

    def analyze_consistency_and_balance(self, activities: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning consistency and content balance."""
        total_days = activities['total_days']
        active_days = activities['active_days']
        video_count = len(activities['video_learning'])
        reading_count = len(activities['reading_materials'])
        thoughts_count = len(activities['deep_thoughts'])
        outputs_count = len(activities['outputs'])

        analysis = {
            'consistency': {},
            'balance': {},
            'quality': {},
            'growth': {}
        }

        # Consistency assessment
        activity_rate = (active_days / total_days) * 100 if total_days > 0 else 0

        if activity_rate >= 80:
            analysis['consistency'] = {
                'rate': activity_rate,
                'status': '✅ 学习频率优秀',
                'description': f'学习频率: {activity_rate:.0f}% ({active_days}/{total_days} 天)',
                'suggestion': '继续保持规律的学习习惯'
            }
        elif activity_rate >= 60:
            analysis['consistency'] = {
                'rate': activity_rate,
                'status': '🟡 学习频率良好',
                'description': f'学习频率: {activity_rate:.0f}% ({active_days}/{total_days} 天)',
                'suggestion': '建议进一步提高学习一致性'
            }
        else:
            analysis['consistency'] = {
                'rate': activity_rate,
                'status': '❌ 学习频率偏低',
                'description': f'学习频率: {activity_rate:.0f}% ({active_days}/{total_days} 天)',
                'suggestion': '需要建立更规律的学习习惯'
            }

        # Content balance assessment
        content_types = [
            ('视频学习', video_count, 2),  # Expected 2 per week
            ('文章阅读', reading_count, 3),  # Expected 3 per week
            ('思考记录', thoughts_count, 5)   # Expected 5 per week
        ]

        weeks = max(1, total_days // 7)  # Estimate weeks
        balance_analysis = []

        for content_type, count, expected_per_week in content_types:
            expected_total = expected_per_week * weeks
            percentage = min(100, (count / expected_total * 100)) if expected_total > 0 else 0

            if percentage >= 80:
                status = '✅'
                suggestion = '保持良好的学习节奏'
            elif percentage >= 50:
                status = '🟡'
                suggestion = '建议增加此类内容的学习'
            else:
                status = '❌'
                suggestion = f'缺少{content_type}，建议关注此领域'

            balance_analysis.append({
                'type': content_type,
                'count': count,
                'percentage': f'{percentage:.0f}%',
                'status': status,
                'suggestion': suggestion
            })

        analysis['balance'] = balance_analysis

        # Quality assessment (review completion rate)
        # Estimate review completion based on active days
        review_rate = active_days / total_days * 100 if total_days > 0 else 0

        if review_rate >= 80:
            analysis['quality'] = {
                'review_rate': f'{review_rate:.0f}%',
                'status': '✅ 总结习惯优秀',
                'suggestion': '继续保持反思总结的好习惯'
            }
        elif review_rate >= 60:
            analysis['quality'] = {
                'review_rate': f'{review_rate:.0f}%',
                'status': '🟡 总结习惯良好',
                'suggestion': '建议每日使用 /daily-review 命令'
            }
        else:
            analysis['quality'] = {
                'review_rate': f'{review_rate:.0f}%',
                'status': '❌ 总结习惯需要加强',
                'suggestion': '需要建立每日回顾总结的习惯'
            }

        # Growth trajectory
        current_month = self.calculate_current_month()

        if current_month == 1:
            growth_status = '🌱 刚开始建立学习习惯，继续保持'
        elif current_month <= 3:
            growth_status = '📈 基础巩固期，逐步建立系统学习方法'
        elif current_month <= 6:
            growth_status = '🚀 技能提升期，注重实践应用'
        else:
            growth_status = '🎯 深度发展期，专注专业影响力'

        analysis['growth'] = {
            'current_month': current_month,
            'status': growth_status,
            'content_evolution': '内容记录较少，建议增加学习内容的记录' if active_days < 5 else '内容记录良好，保持学习深度'
        }

        return analysis

    def analyze_goal_gaps(self, monthly_goals: str, activities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze gaps between goals and actual progress."""
        gaps = []

        # Extract key goals from monthly goals text
        goal_keywords = {
            'LLM基础': ['llm', 'ai', 'prompt', 'chain', 'agent', '大模型'],
            '向量数据库': ['向量', 'vector', 'database', 'embedding'],
            '微调': ['微调', 'fine-tune', 'tuning', 'training'],
            '产品管理': ['prd', 'pm', 'product', 'inspired', '用户故事', 'kpi'],
            '项目实践': ['agent', '项目', 'case study', '迭代']
        }

        # Analyze content for goal-related keywords
        all_content = ' '.join(activities['video_learning'] +
                              activities['reading_materials'] +
                              activities['deep_thoughts'] +
                              activities['outputs'])
        all_content_lower = all_content.lower()

        for goal, keywords in goal_keywords.items():
            found_keywords = [kw for kw in keywords if kw.lower() in all_content_lower]
            completion_rate = len(found_keywords) / len(keywords) * 100

            if completion_rate >= 60:
                status = '✅ 进展良好'
                suggestion = '继续深入学习此领域'
            elif completion_rate >= 30:
                status = '🟡 部分完成'
                suggestion = '建议增加相关学习内容'
            else:
                status = '❌ 待开始'
                suggestion = '需要重点关注此目标'

            gaps.append({
                'goal': goal,
                'status': status,
                'completion': f'{completion_rate:.0f}%',
                'found_keywords': found_keywords,
                'suggestion': suggestion
            })

        return gaps

    def generate_recommendations(self, score_data: Dict[str, Any], activities: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        score = score_data['score']
        metrics = score_data['metrics']

        if score >= 80:
            recommendations.append("🎉 学习状态优秀！继续保持这种学习节奏")
        elif score >= 60:
            recommendations.append("📈 学习状态良好，建议进一步优化学习结构")
        else:
            recommendations.append("🔄 学习习惯需要改进，建议制定更系统的学习计划")

        # Specific recommendations based on metrics
        if metrics['video_count'] < 5:
            recommendations.append("📹 建议增加视频学习，每周观看2-3个技术/产品相关视频")

        if metrics['reading_count'] < 10:
            recommendations.append("📚 建议增加阅读量，订阅行业newsletter和技术博客")

        if metrics['thoughts_count'] < 10:
            recommendations.append("💭 建议增加深度思考记录，每天至少记录1-2个洞察")

        if metrics['outputs_count'] < 3:
            recommendations.append("📝 建议增加学习输出，将学习内容转化为文章、项目或分享")

        if score_data['activity_rate'] < 70:
            recommendations.append("⏰ 建议建立固定的学习时间，提高学习一致性")

        # Project-specific recommendations
        if activities['projects']:
            recommendations.append("🚀 继续推进 WayToAce 项目，保持产品开发动力")
        else:
            recommendations.append("💡 考虑启动一个个人项目，将学习应用到实践中")

        return recommendations

    def format_output(self, data: Dict[str, Any], output_format: str) -> str:
        """Format the milestone report in the specified format."""
        if output_format.lower() == 'json':
            return json.dumps(data, ensure_ascii=False, indent=2)

        # Default to markdown format
        report_lines = []
        current_date = datetime.now().strftime("%Y年%m月%d日")
        current_month = self.calculate_current_month()

        # Header
        report_lines.extend([
            f"# Milestone Report - {current_date}",
            "",
            "## 🎯 当前阶段",
            "",
            f"- **计划月份**: 月 {current_month}",
            f"- **学习开始日期**: {data['metadata']['learning_start_date'][:10]}",
            "- **主要目标**:",
            f"  - 技术：LLM 基础、prompt/chain/agent 基本概念、向量数据库、简单微调/指令微调概念。",
            f"  - 产品：读《Inspired》或类似 PM 经典书，学习如何写 PRD、用户故事、KPI。",
            f"  - 输出：基于你已有 agent 做一次迭代，目标是提升一个明确 KPI（如 召回率/任务成功率/用户留存），形成 case study。",
            "",
        ])

        # Learning statistics
        metrics = data['learning_habits']['metrics']
        report_lines.extend([
            "## 📊 学习统计",
            "",
            f"- **总学习天数**: {metrics['total_days']} 天",
            f"- **视频学习**: {metrics['video_count']} 个视频/教程",
            f"- **文章阅读**: {metrics['reading_count']} 篇文章/通讯",
            f"- **思考记录**: {metrics['thoughts_count']} 次记录",
            f"- **项目产出**: {metrics['outputs_count']} 项相关活动",
            "",
        ])

        # Main achievements
        activities = data['activities']
        if activities['outputs'] or activities['projects']:
            report_lines.extend([
                "## ✅ 主要成就",
                "",
            ])

            # Show recent project work
            if activities['projects']:
                for project in activities['projects'][-3:]:
                    report_lines.append(f"**{project['date']}:**")
                    report_lines.append(f"- **Project work**: {project['content']}")
                    report_lines.append("")

            # Show key outputs
            if activities['outputs']:
                recent_outputs = activities['outputs'][-3:]
                for output in recent_outputs:
                    report_lines.append(f"- {output}")
                report_lines.append("")

        # Learning habits assessment
        consistency_data = data.get('consistency_analysis', {})
        report_lines.extend([
            "## 📈 学习习惯评估",
            "",
            "### 一致性评估",
            "",
        ])

        if 'consistency' in consistency_data:
            consistency = consistency_data['consistency']
            report_lines.extend([
                f"- **学习频率**: {consistency['description']}",
                f"  - {consistency['status']}，{consistency['suggestion']}",
            ])

        if 'balance' in consistency_data:
            report_lines.extend([
                "- **内容平衡度**:",
            ])
            for balance_item in consistency_data['balance']:
                report_lines.append(f"  - {balance_item['type']}: {balance_item['percentage']} ({balance_item['count']})")
                if balance_item['status'] != '✅':
                    report_lines.append(f"  - {balance_item['status']} {balance_item['suggestion']}")

        report_lines.append("")

        # Quality assessment
        if 'quality' in consistency_data:
            quality = consistency_data['quality']
            report_lines.extend([
                "### 质量评估",
                "",
                f"- **总结习惯**: {quality['review_rate']}",
                f"  - {quality['status']}",
                f"- **深度思考**: ",
                f"有一定的思考记录，但可以更加频繁" if metrics['thoughts_count'] > 0 else "思考记录较少",
                f"  - ⚠️ {quality['suggestion']}",
                f"- **实践转化**: ",
                f"有一定的项目实践" if len(activities['projects']) > 0 else "缺少项目实践",
                f"  - ⚠️ 可以增加更多实际项目开发",
                "",
            ])

        # Growth trajectory
        if 'growth' in consistency_data:
            growth = consistency_data['growth']
            report_lines.extend([
                "### 成长轨迹",
                "",
                f"- **学习周期**: 当前第 {growth['current_month']} 月",
                f"  - {growth['status']}",
                f"- **内容演进**: ",
                f"{growth['content_evolution']}",
                "",
            ])

        # Gap analysis
        if 'goal_gaps' in data and data['goal_gaps']:
            report_lines.extend([
                "## ⚠️ 差距分析",
                "",
                "- 对照当前月份目标，分析实际完成情况：",
            ])

            for gap in data['goal_gaps']:
                checkbox = '[ ]' if gap['status'] != '✅ 进展良好' else '[x]'
                report_lines.append(f"  - {checkbox} {gap['goal']}：{gap['status']} ({gap['completion']})")

            report_lines.append("")

        # Detailed improvement suggestions
        report_lines.extend([
            "## 🚀 改进建议",
            "",
            "### 基于学习习惯的改进建议",
            "",
        ])

        # Consistency improvements
        if 'consistency' in consistency_data:
            consistency = consistency_data['consistency']
            if consistency['rate'] < 80:
                report_lines.extend([
                    f"- **提高学习频率**: 目前学习频率为 {consistency['rate']:.0f}%，建议：",
                    "  - 设置固定的学习时间段（如每日早晨或晚上）",
                    "  - 使用 /daily-start 命令创建每日学习记录",
                    "  - 即使学习时间有限，也要保持记录的连续性",
                    "",
                ])

        # Content-specific improvements
        if 'balance' in consistency_data:
            for balance_item in consistency_data['balance']:
                if balance_item['status'] != '✅':
                    suggestions_map = {
                        '视频学习': '- **增加视频学习**: 建议每周观看 2-3 个技术相关视频教程',
                        '文章阅读': '- **增加文章阅读**: 建议订阅 AI/技术相关 newsletter，保持行业敏感度',
                        '思考记录': '- **加强深度思考**: 每日学习后，在 braindump 部分记录：\n  - 学到了什么新知识\n  - 如何与之前的知识连接\n  - 可以应用到哪些实际场景'
                    }
                    if balance_item['type'] in suggestions_map:
                        report_lines.append(suggestions_map[balance_item['type']])

        report_lines.append("")

        # Review improvements
        if 'quality' in consistency_data:
            quality = consistency_data['quality']
            if 'review_rate' in quality and float(quality['review_rate'].replace('%', '')) < 80:
                report_lines.extend([
                    f"- **完善每日总结**: 当前总结完成率 {quality['review_rate']}，建议：",
                    "  - 每日结束时使用 /daily-review 命令",
                    "  - 回顾当天的学习收获和不足",
                    "  - 规划第二天的学习重点",
                    "",
                ])

        # Next steps
        report_lines.extend([
            "### 下一步行动",
            "",
            "- 定期使用 /milestone 命令（建议每周一次）监控学习习惯",
            "- 根据评估结果调整学习策略和时间分配",
            "- 寻找学习伙伴或加入相关社群，增加交流和反馈",
            "- 设定具体的月度/周度学习目标，并跟踪完成情况",
            "",
        ])

        return "\n".join(report_lines)

    def generate_milestone_report(self, target_month: Optional[int] = None,
                                output_format: str = "markdown") -> Dict[str, Any]:
        """Generate comprehensive milestone report."""
        current_month = self.calculate_current_month()
        analysis_month = target_month if target_month else current_month

        # Collect data
        monthly_goals = self.extract_monthly_goals(analysis_month)
        activities = self.collect_learning_activities(target_month)
        score_data = self.calculate_learning_habits_score(activities)
        recommendations = self.generate_recommendations(score_data, activities)

        # New detailed analysis
        consistency_analysis = self.analyze_consistency_and_balance(activities)
        goal_gaps = self.analyze_goal_gaps(monthly_goals, activities)

        # Determine analysis period
        start_date = self.get_learning_start_date()
        if target_month:
            period_start = start_date + timedelta(days=(target_month-1)*30)
            period_end = period_start + timedelta(days=29)
            analysis_period = f"第 {target_month} 月 ({period_start.strftime('%Y-%m-%d')} 至 {period_end.strftime('%Y-%m-%d')})"
        else:
            analysis_period = f"学习开始至今 ({start_date.strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')})"

        return {
            'current_month': current_month,
            'analysis_month': analysis_month,
            'analysis_period': analysis_period,
            'monthly_goals': monthly_goals,
            'learning_habits': score_data,
            'activities': activities,
            'recommendations': recommendations,
            'consistency_analysis': consistency_analysis,
            'goal_gaps': goal_gaps,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'learning_start_date': start_date.isoformat(),
                'total_learning_days': (datetime.now() - start_date).days + 1
            }
        }


def main():
    """Main entry point for the milestone script."""
    parser = argparse.ArgumentParser(
        description="生成学习里程碑报告",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--save', help='保存报告到指定文件')
    parser.add_argument('--month', type=int, help='分析特定月份 (1-12)')
    parser.add_argument('--format', choices=['markdown', 'json'],
                       default='markdown', help='输出格式')

    args = parser.parse_args()

    analyzer = MilestoneAnalyzer()

    try:
        # Generate report
        report_data = analyzer.generate_milestone_report(
            target_month=args.month,
            output_format=args.format
        )

        # Format output
        formatted_report = analyzer.format_output(report_data, args.format)

        # Save or print
        if args.save:
            output_path = Path(args.save)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            print(f"📄 里程碑报告已保存到: {output_path}")
        else:
            print(formatted_report)

        return 0

    except Exception as e:
        print(f"Error generating milestone report: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())