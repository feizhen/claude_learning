#!/usr/bin/env python3
"""
Insight Script

从学习记录中提取灵感，生成适用于社交媒体创作的内容建议。
分析学习内容的主题趋势、产品体验、技术洞察，为内容创作提供素材和灵感。
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import tempfile
import subprocess


class InsightAnalyzer:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.weeks_dir = self.base_dir / "weeks"

    def get_analysis_date_range(self, days: Optional[int] = None,
                              weeks: Optional[int] = None,
                              all_content: bool = False) -> Tuple[datetime, datetime]:
        """Calculate the date range for analysis."""
        end_date = datetime.now()

        if all_content:
            # Find earliest file
            daily_files = list(self.weeks_dir.glob("*/????_??_??.md"))
            if daily_files:
                daily_files.sort(key=lambda x: x.name)
                earliest_file = daily_files[0]
                try:
                    filename = earliest_file.stem
                    year, month, day = map(int, filename.split('_'))
                    start_date = datetime(year, month, day)
                except (ValueError, IndexError):
                    start_date = datetime(2025, 9, 15)
            else:
                start_date = datetime(2025, 9, 15)
        elif weeks:
            start_date = end_date - timedelta(weeks=weeks)
        else:
            # Default to days (7 if not specified)
            days = days or 7
            start_date = end_date - timedelta(days=days)

        return start_date, end_date

    def collect_content_in_range(self, start_date: datetime, end_date: datetime,
                                topic: Optional[str] = None) -> Dict[str, List[Any]]:
        """Collect all content within the specified date range."""
        content = {
            'videos': [],
            'readings': [],
            'thoughts': [],
            'outputs': [],
            'projects': [],
            'insights': [],
            'product_experiences': [],
            'technical_notes': []
        }

        daily_files = list(self.weeks_dir.glob("*/????_??_??.md"))

        for file_path in daily_files:
            try:
                # Parse file date
                filename = file_path.stem
                year, month, day = map(int, filename.split('_'))
                file_date = datetime(year, month, day)

                # Skip files outside date range
                if file_date < start_date or file_date > end_date:
                    continue

                # Read and parse file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                # Apply topic filter if specified
                if topic and not self._content_matches_topic(file_content, topic):
                    continue

                date_str = file_date.strftime('%Y-%m-%d')

                # Extract video content
                video_section = self._extract_section(file_content, 'video')
                if video_section.strip():
                    videos = self._parse_video_content(video_section, date_str)
                    content['videos'].extend(videos)

                # Extract reading materials
                newsletter_section = self._extract_section(file_content, 'newsletter')
                if newsletter_section.strip():
                    readings = self._parse_reading_content(newsletter_section, date_str)
                    content['readings'].extend(readings)

                # Extract thoughts and braindump
                braindump_section = self._extract_section(file_content, 'braindump')
                if braindump_section.strip():
                    thoughts, insights, products = self._parse_braindump_content(braindump_section, date_str)
                    content['thoughts'].extend(thoughts)
                    content['insights'].extend(insights)
                    content['product_experiences'].extend(products)

                # Extract outputs
                output_section = self._extract_section(file_content, 'output')
                if output_section.strip():
                    outputs = self._parse_output_content(output_section, date_str)
                    content['outputs'].extend(outputs)

                # Extract project progress
                waytoace_section = self._extract_section(file_content, 'WayToAce')
                if waytoace_section.strip():
                    content['projects'].append({
                        'date': date_str,
                        'content': waytoace_section.strip(),
                        'type': 'WayToAce'
                    })

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue

        return content

    def _extract_section(self, content: str, section: str) -> str:
        """Extract content from a specific markdown section."""
        pattern = rf"^## {re.escape(section)}$(.*?)(?=^## |\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _content_matches_topic(self, content: str, topic: str) -> bool:
        """Check if content matches the specified topic."""
        topic_lower = topic.lower()
        content_lower = content.lower()
        return topic_lower in content_lower

    def _parse_video_content(self, content: str, date: str) -> List[Dict[str, Any]]:
        """Parse video learning content."""
        videos = []
        lines = content.split('\n')

        current_video = None
        for line in lines:
            line = line.strip()
            if line.startswith('- [') and '](' in line:
                # Extract video title and URL
                match = re.match(r'- \[(.*?)\]\((.*?)\)', line)
                if match:
                    title, url = match.groups()
                    current_video = {
                        'date': date,
                        'title': title,
                        'url': url,
                        'notes': []
                    }
                    videos.append(current_video)
            elif line.startswith('  ') and current_video:
                # Add notes to current video
                current_video['notes'].append(line.strip())

        return videos

    def _parse_reading_content(self, content: str, date: str) -> List[Dict[str, Any]]:
        """Parse reading materials content."""
        readings = []
        for line in content.split('\n'):
            line = line.strip()
            if '[x]' in line.lower():
                # Extract completed reading item
                reading_text = re.sub(r'\[x\]', '', line, flags=re.IGNORECASE).strip()
                if reading_text:
                    readings.append({
                        'date': date,
                        'content': reading_text,
                        'completed': True
                    })

        return readings

    def _parse_braindump_content(self, content: str, date: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Parse braindump content into thoughts, insights, and product experiences."""
        thoughts = []
        insights = []
        products = []

        lines = content.split('\n')
        current_item = None
        current_type = 'thought'

        for line in lines:
            line = line.strip()

            # Detect insights sections
            if 'insights:' in line.lower() or 'insight:' in line.lower():
                current_type = 'insight'
                continue

            # Detect product experience sections
            if any(keyword in line.lower() for keyword in ['产品使用体验', '体验了', '试用了']):
                current_type = 'product'
                current_item = {
                    'date': date,
                    'content': line,
                    'details': []
                }
                products.append(current_item)
                continue

            if line.startswith('- '):
                # New main point
                item_content = line[2:].strip()
                current_item = {
                    'date': date,
                    'content': item_content,
                    'details': []
                }

                if current_type == 'insight':
                    insights.append(current_item)
                elif current_type == 'product':
                    products.append(current_item)
                else:
                    thoughts.append(current_item)

            elif line.startswith('  ') and current_item:
                # Add detail to current item
                current_item['details'].append(line.strip())

        return thoughts, insights, products

    def _parse_output_content(self, content: str, date: str) -> List[Dict[str, Any]]:
        """Parse learning output content."""
        outputs = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                output_text = line[2:].strip()

                # Try to extract URL if present
                url_match = re.search(r'\[(.*?)\]\((.*?)\)', output_text)
                if url_match:
                    title, url = url_match.groups()
                    outputs.append({
                        'date': date,
                        'title': title,
                        'url': url,
                        'type': 'link'
                    })
                else:
                    outputs.append({
                        'date': date,
                        'content': output_text,
                        'type': 'text'
                    })

        return outputs

    def analyze_themes_and_trends(self, content: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Analyze themes and trends from collected content."""
        analysis = {
            'top_keywords': [],
            'themes': {},
            'trends': [],
            'content_summary': {}
        }

        # Collect all text content for keyword analysis
        all_text = []

        # Add video content
        for video in content['videos']:
            all_text.append(video['title'])
            all_text.extend(video['notes'])

        # Add thoughts and insights
        for thought in content['thoughts']:
            all_text.append(thought['content'])
            all_text.extend(thought['details'])

        for insight in content['insights']:
            all_text.append(insight['content'])
            all_text.extend(insight['details'])

        # Add product experiences
        for product in content['product_experiences']:
            all_text.append(product['content'])
            all_text.extend(product['details'])

        # Extract keywords (simplified approach)
        text_content = ' '.join(all_text).lower()

        # Define important keywords to look for
        tech_keywords = ['ai', 'claude', 'gpt', 'python', 'javascript', 'react', 'vue', '机器学习', '深度学习', '人工智能']
        product_keywords = ['产品', '用户体验', 'ux', 'ui', '设计', '功能', '需求', '迭代']
        business_keywords = ['商业', '变现', '商业化', '创业', '投资', '市场', '用户', '获客']

        # Count keyword frequencies
        keyword_counts = Counter()
        for keyword in tech_keywords + product_keywords + business_keywords:
            count = text_content.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count

        analysis['top_keywords'] = keyword_counts.most_common(10)

        # Categorize themes
        analysis['themes'] = {
            'technology': [kw for kw, _ in keyword_counts.most_common() if kw in tech_keywords],
            'product': [kw for kw, _ in keyword_counts.most_common() if kw in product_keywords],
            'business': [kw for kw, _ in keyword_counts.most_common() if kw in business_keywords]
        }

        # Content summary
        analysis['content_summary'] = {
            'total_videos': len(content['videos']),
            'total_readings': len(content['readings']),
            'total_thoughts': len(content['thoughts']),
            'total_insights': len(content['insights']),
            'total_outputs': len(content['outputs']),
            'total_products': len(content['product_experiences']),
            'total_projects': len(content['projects'])
        }

        return analysis

    def generate_content_suggestions(self, content: Dict[str, List[Any]],
                                   analysis: Dict[str, Any],
                                   platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate content creation suggestions based on analysis."""
        suggestions = []

        # Platform-specific templates
        platform_templates = {
            'xiaohongshu': {
                'max_length': 1000,
                'style': 'casual',
                'hashtags': True,
                'emojis': True
            },
            'weibo': {
                'max_length': 140,
                'style': 'concise',
                'hashtags': True,
                'emojis': False
            },
            'linkedin': {
                'max_length': 3000,
                'style': 'professional',
                'hashtags': False,
                'emojis': False
            },
            'twitter': {
                'max_length': 280,
                'style': 'engaging',
                'hashtags': True,
                'emojis': True
            }
        }

        template_config = platform_templates.get(platform, platform_templates['xiaohongshu'])

        # Generate suggestions based on insights
        if content['insights']:
            for insight in content['insights'][-5:]:  # Last 5 insights
                suggestion = {
                    'type': 'insight_sharing',
                    'source': insight,
                    'title': f"关于{insight['content'][:20]}...的思考",
                    'content': self._format_insight_post(insight, template_config),
                    'platform': platform or 'xiaohongshu',
                    'tags': self._extract_relevant_tags(insight['content'], analysis['themes'])
                }
                suggestions.append(suggestion)

        # Generate suggestions based on product experiences
        if content['product_experiences']:
            for product in content['product_experiences'][-3:]:  # Last 3 product experiences
                suggestion = {
                    'type': 'product_review',
                    'source': product,
                    'title': f"产品体验分享: {product['content'][:30]}...",
                    'content': self._format_product_post(product, template_config),
                    'platform': platform or 'xiaohongshu',
                    'tags': ['产品体验', '工具推荐'] + self._extract_relevant_tags(product['content'], analysis['themes'])
                }
                suggestions.append(suggestion)

        # Generate suggestions based on learning progress
        if content['videos'] or content['readings']:
            learning_summary = self._create_learning_summary(content)
            suggestion = {
                'type': 'learning_summary',
                'source': {'videos': content['videos'], 'readings': content['readings']},
                'title': "近期学习总结分享",
                'content': self._format_learning_post(learning_summary, template_config),
                'platform': platform or 'xiaohongshu',
                'tags': ['学习笔记', '技术分享'] + analysis['themes']['technology'][:3]
            }
            suggestions.append(suggestion)

        # Generate trend analysis suggestions
        if analysis['top_keywords']:
            suggestion = {
                'type': 'trend_analysis',
                'source': analysis,
                'title': "技术趋势观察",
                'content': self._format_trend_post(analysis, template_config),
                'platform': platform or 'xiaohongshu',
                'tags': ['趋势分析', '技术观察'] + [kw for kw, _ in analysis['top_keywords'][:3]]
            }
            suggestions.append(suggestion)

        return suggestions

    def _format_insight_post(self, insight: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Format an insight into a social media post."""
        lines = []

        if config.get('emojis'):
            lines.append("💡 今日思考")
            lines.append("")

        lines.append(insight['content'])

        if insight['details']:
            lines.append("")
            for detail in insight['details']:
                lines.append(f"• {detail}")

        if config.get('hashtags'):
            lines.append("")
            lines.append("#学习思考 #技术洞察 #产品思维")

        content = '\n'.join(lines)

        # Truncate if too long
        if len(content) > config['max_length']:
            content = content[:config['max_length'] - 3] + "..."

        return content

    def _format_product_post(self, product: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Format a product experience into a social media post."""
        lines = []

        if config.get('emojis'):
            lines.append("🔧 产品体验分享")
            lines.append("")

        lines.append(product['content'])

        if product['details']:
            lines.append("")
            lines.append("主要特点:")
            for i, detail in enumerate(product['details'][:5], 1):
                lines.append(f"{i}. {detail}")

        if config.get('hashtags'):
            lines.append("")
            lines.append("#产品体验 #工具推荐 #效率工具")

        content = '\n'.join(lines)

        if len(content) > config['max_length']:
            content = content[:config['max_length'] - 3] + "..."

        return content

    def _format_learning_post(self, summary: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Format learning summary into a social media post."""
        lines = []

        if config.get('emojis'):
            lines.append("📚 本周学习总结")
            lines.append("")

        if summary['video_count'] > 0:
            lines.append(f"🎥 观看了 {summary['video_count']} 个学习视频")

        if summary['reading_count'] > 0:
            lines.append(f"📖 完成了 {summary['reading_count']} 项阅读")

        if summary['key_topics']:
            lines.append("")
            lines.append("重点学习领域:")
            for topic in summary['key_topics'][:3]:
                lines.append(f"• {topic}")

        if config.get('hashtags'):
            lines.append("")
            lines.append("#学习笔记 #技术学习 #持续学习")

        content = '\n'.join(lines)

        if len(content) > config['max_length']:
            content = content[:config['max_length'] - 3] + "..."

        return content

    def _format_trend_post(self, analysis: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Format trend analysis into a social media post."""
        lines = []

        if config.get('emojis'):
            lines.append("📊 技术趋势观察")
            lines.append("")

        lines.append("根据最近的学习和观察，以下技术值得关注:")
        lines.append("")

        for keyword, count in analysis['top_keywords'][:5]:
            lines.append(f"• {keyword} (出现 {count} 次)")

        if config.get('hashtags'):
            lines.append("")
            lines.append("#技术趋势 #行业观察 #技术分析")

        content = '\n'.join(lines)

        if len(content) > config['max_length']:
            content = content[:config['max_length'] - 3] + "..."

        return content

    def _create_learning_summary(self, content: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Create a summary of learning activities."""
        video_count = len(content['videos'])
        reading_count = len(content['readings'])

        # Extract key topics
        key_topics = []
        for video in content['videos']:
            if 'AI' in video['title'] or 'ai' in video['title'].lower():
                key_topics.append('人工智能')
            if 'Python' in video['title'] or 'python' in video['title'].lower():
                key_topics.append('Python编程')
            if '产品' in video['title']:
                key_topics.append('产品设计')

        # Remove duplicates
        key_topics = list(set(key_topics))

        return {
            'video_count': video_count,
            'reading_count': reading_count,
            'key_topics': key_topics
        }

    def _extract_relevant_tags(self, text: str, themes: Dict[str, List[str]]) -> List[str]:
        """Extract relevant tags based on content and themes."""
        tags = []
        text_lower = text.lower()

        # Add theme-based tags
        for theme_name, keywords in themes.items():
            for keyword in keywords:
                if keyword in text_lower:
                    tags.append(keyword)

        return list(set(tags))[:5]  # Max 5 tags

    def run_ai_analysis(self, content: Dict[str, List[Any]]) -> Optional[str]:
        """Run AI-enhanced analysis if available."""
        try:
            # This would typically call an AI API
            # For now, return a placeholder
            return "AI 分析功能需要联网环境才能使用"
        except Exception as e:
            return f"AI 分析失败: {e}"

    def format_output(self, content: Dict[str, List[Any]], analysis: Dict[str, Any],
                     suggestions: List[Dict[str, Any]], output_format: str,
                     verbose: bool = False) -> str:
        """Format the insight report in the specified format."""
        if output_format.lower() == 'json':
            data = {
                'content': content,
                'analysis': analysis,
                'suggestions': suggestions,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_suggestions': len(suggestions)
                }
            }
            return json.dumps(data, ensure_ascii=False, indent=2)

        # Default to markdown format
        report_lines = []

        # Header
        report_lines.extend([
            "# 📝 内容创作灵感报告",
            "",
            f"📅 **生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            f"📊 **分析内容**: {analysis['content_summary']['total_videos']} 个视频, {analysis['content_summary']['total_thoughts']} 条思考, {analysis['content_summary']['total_insights']} 个洞察",
            "",
        ])

        # Content summary
        summary = analysis['content_summary']
        report_lines.extend([
            "## 📊 内容概览",
            "",
            f"- 🎥 学习视频: {summary['total_videos']} 个",
            f"- 📚 阅读材料: {summary['total_readings']} 项",
            f"- 💭 深度思考: {summary['total_thoughts']} 条",
            f"- 💡 核心洞察: {summary['total_insights']} 个",
            f"- 📝 学习输出: {summary['total_outputs']} 项",
            f"- 🔧 产品体验: {summary['total_products']} 个",
            "",
        ])

        # Theme analysis
        if analysis['top_keywords']:
            report_lines.extend([
                "## 🎯 主题分析",
                "",
                "### 热门关键词",
                "",
            ])
            for keyword, count in analysis['top_keywords']:
                report_lines.append(f"- **{keyword}**: {count} 次")
            report_lines.append("")

        # Content suggestions
        if suggestions:
            report_lines.extend([
                "## 💡 内容创作建议",
                "",
            ])

            for i, suggestion in enumerate(suggestions, 1):
                report_lines.extend([
                    f"### {i}. {suggestion['title']}",
                    "",
                    f"**类型**: {suggestion['type']}",
                    f"**平台**: {suggestion['platform']}",
                    "",
                    "**建议内容**:",
                    "```",
                    suggestion['content'],
                    "```",
                    "",
                    f"**推荐标签**: {', '.join(suggestion['tags'][:5])}",
                    "",
                    "---",
                    "",
                ])

        # Detailed content if verbose
        if verbose:
            report_lines.extend([
                "## 📖 详细内容分析",
                "",
            ])

            if content['insights']:
                report_lines.extend([
                    "### 💡 核心洞察",
                    "",
                ])
                for insight in content['insights']:
                    report_lines.append(f"**{insight['date']}**: {insight['content']}")
                    for detail in insight['details']:
                        report_lines.append(f"  - {detail}")
                    report_lines.append("")

            if content['product_experiences']:
                report_lines.extend([
                    "### 🔧 产品体验",
                    "",
                ])
                for product in content['product_experiences']:
                    report_lines.append(f"**{product['date']}**: {product['content']}")
                    for detail in product['details']:
                        report_lines.append(f"  - {detail}")
                    report_lines.append("")

        # Footer
        report_lines.extend([
            "---",
            "",
            f"*报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}*",
            "*基于 claude_learning 系统内容分析*",
        ])

        return "\n".join(report_lines)


def main():
    """Main entry point for the insight script."""
    parser = argparse.ArgumentParser(
        description="从学习记录中提取灵感，生成社交媒体创作内容建议",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--days', type=int, help='分析最近N天的内容')
    parser.add_argument('--weeks', type=int, help='分析最近N周的内容')
    parser.add_argument('--all', action='store_true', help='分析所有历史内容')
    parser.add_argument('--topic', help='聚焦特定主题分析')
    parser.add_argument('--platform', choices=['xiaohongshu', 'weibo', 'linkedin', 'twitter'],
                       help='为特定平台优化')
    parser.add_argument('--format', choices=['markdown', 'json'],
                       default='markdown', help='输出格式')
    parser.add_argument('--save', help='保存结果到文件')
    parser.add_argument('--verbose', action='store_true', help='显示详细分析过程')
    parser.add_argument('--ai-analysis', action='store_true', help='启用AI深度分析')

    args = parser.parse_args()

    analyzer = InsightAnalyzer()

    try:
        # Determine analysis range
        start_date, end_date = analyzer.get_analysis_date_range(
            days=args.days,
            weeks=args.weeks,
            all_content=args.all
        )

        print(f"🔍 分析时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

        # Collect content
        content = analyzer.collect_content_in_range(start_date, end_date, args.topic)

        # Analyze themes and trends
        analysis = analyzer.analyze_themes_and_trends(content)

        # Generate content suggestions
        suggestions = analyzer.generate_content_suggestions(content, analysis, args.platform)

        # Run AI analysis if requested
        if args.ai_analysis:
            ai_result = analyzer.run_ai_analysis(content)
            if ai_result:
                print(f"🤖 AI 分析: {ai_result}")

        # Format output
        formatted_report = analyzer.format_output(
            content, analysis, suggestions, args.format, args.verbose
        )

        # Save or print
        if args.save:
            output_path = Path(args.save)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            print(f"📄 洞察报告已保存到: {output_path}")
        else:
            print(formatted_report)

        print(f"\n✨ 生成了 {len(suggestions)} 个内容创作建议")

        return 0

    except Exception as e:
        print(f"Error generating insight report: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())