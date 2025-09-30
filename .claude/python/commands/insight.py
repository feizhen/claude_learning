#!/usr/bin/env python3
"""
Insight Command
从学习记录中提取社交媒体创作灵感的Python实现。

从学习记录中提取灵感，生成适用于社交媒体创作的内容建议。
分析学习内容的主题趋势、产品体验、技术洞察，为内容创作提供素材和灵感。
"""

import sys
import os
import argparse
import re
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta

# 添加父目录到Python路径，以便导入core模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.date_utils import DateUtils
from core.file_utils import FileUtils
from core.content_parser import ContentParser
from core.templates import Templates


class InsightAnalyzer:
    """洞察分析器类。"""

    def __init__(self):
        self.analyzed_files = 0
        self.content_sections = {
            'video': {},
            'newsletter': {},
            'braindump': {},
            'output': {},
            'review': {}
        }

    def extract_learning_content(self, days: Optional[int] = None, weeks: Optional[int] = None,
                               all_content: bool = False) -> None:
        """提取学习内容。"""
        daily_files = FileUtils.find_daily_files()
        current_date = DateUtils.get_current_date()

        # 确定分析期间
        if all_content:
            cutoff_date = None
        elif days:
            cutoff_date = DateUtils.get_date_n_days_ago(days, current_date)
        elif weeks:
            cutoff_date = DateUtils.get_date_n_weeks_ago(weeks, current_date)
        else:
            cutoff_date = DateUtils.get_date_n_days_ago(7, current_date)  # 默认7天

        print("📊 正在扫描学习记录...", file=sys.stderr)

        for file_path in daily_files:
            # 提取文件日期
            filename = os.path.basename(file_path)
            file_date = DateUtils.parse_filename_date(filename)

            if file_date is None:
                continue

            # 检查是否在分析期间内
            if cutoff_date and file_date < cutoff_date:
                continue

            self.analyzed_files += 1

            # 读取文件内容
            content = FileUtils.read_file(file_path)
            if not content:
                continue

            # 提取各个章节内容
            sections = ContentParser.extract_all_sections(content)
            date_str = file_date.strftime("%Y-%m-%d")

            for section_name, section_content in sections.items():
                if section_content and section_name in self.content_sections:
                    self.content_sections[section_name][date_str] = section_content

        print(f"📈 扫描完成: 分析了 {self.analyzed_files} 个文件", file=sys.stderr)

    def analyze_content_themes(self) -> Dict[str, Dict[str, int]]:
        """分析内容主题和关键词。"""
        print("🔍 正在分析内容主题...", file=sys.stderr)

        # 获取关键词分类
        keyword_categories = Templates.content_analysis_keywords()
        keyword_counts = {}

        # 分析每个内容类型
        for content_type, content_dict in self.content_sections.items():
            if not content_dict:
                continue

            print(f"分析 {content_type} 内容...", file=sys.stderr)

            for category_name, keywords_str in keyword_categories.items():
                keywords = keywords_str.split('|')

                for keyword in keywords:
                    count = 0
                    for date_str, content in content_dict.items():
                        count += len(re.findall(keyword, content, re.IGNORECASE))

                    if count > 0:
                        key = f"{keyword}:{count}:{content_type}"
                        keyword_counts[key] = count

        return keyword_counts

    def identify_valuable_content(self) -> Dict[str, List[str]]:
        """识别高价值内容片段。"""
        print("💎 正在识别高价值内容...", file=sys.stderr)

        valuable_content = {
            'insights': [],
            'achievements': [],
            'trends': []
        }

        # 分析braindump中的洞察
        for date_str, content in self.content_sections['braindump'].items():
            insight_keywords = ['思考', '洞察', '发现', '体验', '感受', '总结', '建议', '推荐', '不错', '很棒', '有趣', '惊喜']
            lines = content.split('\n')

            for line in lines:
                if any(keyword in line for keyword in insight_keywords):
                    if line.strip() and not line.strip().startswith('==='):
                        valuable_content['insights'].append(f"{date_str}: {line.strip()}")

        # 分析output中的成就
        for date_str, content in self.content_sections['output'].items():
            achievement_keywords = ['完成', '发布', '创建', '实现', '搭建', '上线', 'demo', '项目', '产品']
            lines = content.split('\n')

            for line in lines:
                if any(keyword in line for keyword in achievement_keywords):
                    if line.strip() and not line.strip().startswith('==='):
                        valuable_content['achievements'].append(f"{date_str}: {line.strip()}")

        # 分析newsletter中的趋势
        for date_str, content in self.content_sections['newsletter'].items():
            lines = content.split('\n')
            for line in lines:
                if len(line.strip()) > 10 and not line.strip().startswith('==='):
                    valuable_content['trends'].append(f"{date_str}: {line.strip()}")

        return valuable_content

    def generate_social_media_suggestions(self, keywords: Dict[str, int],
                                        valuable_content: Dict[str, List[str]],
                                        platform: Optional[str] = None) -> str:
        """生成社交媒体内容建议。"""
        print("📱 正在生成社交媒体内容建议...", file=sys.stderr)

        suggestions = ["## 🚀 社交媒体内容建议\n\n"]

        # 推荐话题标签
        if keywords:
            suggestions.append("### 🏷️ 推荐话题标签\n\n")
            # 获取热门关键词
            sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]

            for keyword_info, _ in sorted_keywords:
                keyword = keyword_info.split(':')[0]
                suggestions.append(f"- #{keyword}\n")

            suggestions.append("\n")

        # 平台专属建议
        if platform:
            suggestions.append(f"### 📲 {platform} 专属建议\n\n")

            platform_tips = {
                "xiaohongshu": [
                    "**小红书内容特点:**",
                    "- 标题要吸引眼球，使用数字和情绪词汇",
                    "- 多用表情符号增加视觉吸引力",
                    "- 分享个人体验和真实感受",
                    "- 包含实用的教程或建议"
                ],
                "weibo": [
                    "**微博内容特点:**",
                    "- 简洁明了，突出重点",
                    "- 结合时事热点",
                    "- 使用相关的超话标签",
                    "- 鼓励转发和互动"
                ],
                "linkedin": [
                    "**LinkedIn 内容特点:**",
                    "- 专业性强，展示专业见解",
                    "- 分享职业经验和学习心得",
                    "- 英文内容为主",
                    "- 适合技术深度分享"
                ],
                "twitter": [
                    "**Twitter 内容特点:**",
                    "- 简短精炼，一针见血",
                    "- 使用 thread 展开复杂话题",
                    "- 及时性强，追求viral传播",
                    "- 多使用相关 hashtag"
                ]
            }

            if platform in platform_tips:
                for tip in platform_tips[platform]:
                    suggestions.append(f"{tip}\n")
                suggestions.append("\n")

        # 内容格式建议
        suggestions.extend([
            "### 📝 内容格式建议\n\n",
            "**推荐内容类型:**\n",
            "- 📊 学习总结 - 将本周/本月学习内容制作成图表\n",
            "- 🔧 工具分享 - 介绍使用过的优秀工具和体验\n",
            "- 💡 思考感悟 - 分享学习过程中的洞察和思考\n",
            "- 🎯 成果展示 - 展示学习成果和项目进展\n",
            "- 📚 资源推荐 - 推荐优质的学习资源和文章\n\n"
        ])

        # 发布时机建议
        suggestions.extend([
            "### ⏰ 发布时机建议\n\n",
            "**最佳发布时间:**\n",
            "- 工作日早上 8-9 点（上班路上）\n",
            "- 午休时间 12-13 点\n",
            "- 晚上 20-22 点（休息时间）\n",
            "- 周末下午 14-17 点\n\n"
        ])

        return ''.join(suggestions)

    def generate_platform_content_examples(self, valuable_content: Dict[str, List[str]]) -> str:
        """生成平台专属内容示例。"""
        print("📱 正在生成平台专属内容示例...", file=sys.stderr)

        examples = ["## 📲 平台专属内容示例\n\n"]

        # 获取一个示例洞察
        sample_insight = "今天体验了一个AI工具，发现它的用户体验设计非常出色"
        if valuable_content['insights']:
            sample_line = valuable_content['insights'][0]
            if ':' in sample_line:
                sample_insight = sample_line.split(':', 1)[1].strip()

        # 小红书版本
        examples.extend([
            "### 🍃 小红书版本\n\n",
            "```\n",
            "🚀 又发现一个宝藏AI工具！\n\n",
            "姐妹们，今天必须要分享这个发现！\n\n",
            f"✨ {sample_insight}\n\n",
            "🔥 最让我惊喜的几个点：\n",
            "1️⃣ 界面设计超级简洁好看\n",
            "2️⃣ 新手引导做得特别贴心\n",
            "3️⃣ 功能强大但不会让人觉得复杂\n\n",
            "你们还有什么好用的AI工具推荐吗？评论区见👇\n\n",
            "#AI工具 #效率神器 #产品体验 #科技分享 #学习笔记\n",
            "```\n\n"
        ])

        # 微博版本
        examples.extend([
            "### 🐦 微博版本\n\n",
            "```\n",
            f"💡 产品观察：{sample_insight}\n\n",
            "作为一个产品爱好者，今天深度体验了这个AI工具，几个值得思考的点：\n\n",
            "1. 用户引导的力量：好的引导能让复杂功能变得易懂\n",
            "2. 设计的温度感：技术产品也需要人文关怀\n",
            "3. 功能与简洁的平衡：克制比堆砌更需要智慧\n\n",
            "你觉得一个AI产品最重要的是什么？技术还是体验？\n\n",
            "#产品思考 #AI工具 #用户体验 #产品设计 #科技观察\n",
            "```\n\n"
        ])

        # LinkedIn版本
        examples.extend([
            "### 💼 LinkedIn版本\n\n",
            "```\n",
            "🎯 Product Insights: What Makes AI Tools Truly User-Friendly?\n\n",
            "After spending time with a new AI tool today, I was struck by how thoughtful user onboarding can transform the entire experience.\n\n",
            "Key observations:\n\n",
            "🔸 Progressive Disclosure: Complex features introduced gradually\n",
            "🔸 Contextual Guidance: Help appears exactly when and where needed\n",
            "🔸 Emotional Design: The interface feels approachable, not intimidating\n\n",
            "For product teams building in this space:\n",
            "• Invest heavily in onboarding design\n",
            "• Test with real users, not just tech-savvy early adopters\n",
            "• Remember that complexity should be hidden, not eliminated\n\n",
            "What's your experience with AI tool adoption in your organization?\n\n",
            "#ProductManagement #AITools #UserExperience #TechInnovation #ProductDesign\n",
            "```\n\n"
        ])

        return ''.join(examples)

    def create_content_templates(self) -> str:
        """创建内容创作模板。"""
        print("📋 正在创建内容模板...", file=sys.stderr)

        templates = ["## 📄 内容创作模板\n\n"]

        # 学习总结模板
        templates.extend([
            "### 📊 学习总结模板\n\n",
            "```\n",
            "📚 这周的学习收获 #学习记录 #AI学习\n\n",
            "本周重点学习了：\n",
            "🔸 [技术/工具名称] - [简短描述]\n",
            "🔸 [重要概念] - [个人理解]\n",
            "🔸 [实践项目] - [具体成果]\n\n",
            "💡 最大的收获：\n",
            "[写出最有价值的洞察或体验]\n\n",
            "🎯 下周计划：\n",
            "[简述下周学习重点]\n\n",
            "#持续学习 #技术成长 #个人发展\n",
            "```\n\n"
        ])

        # 工具体验模板
        templates.extend([
            "### 🔧 工具体验模板\n\n",
            "```\n",
            "🛠️ [工具名称]体验分享 #工具推荐\n\n",
            "✨ 亮点功能：\n",
            "• [功能1] - [具体体验]\n",
            "• [功能2] - [使用感受]\n",
            "• [功能3] - [实际价值]\n\n",
            "👍 推荐指数：⭐⭐⭐⭐⭐\n",
            "💰 付费情况：[免费/付费]\n",
            "🎯 适用场景：[具体应用场景]\n\n",
            "总结：[一句话总结工具价值]\n\n",
            "#效率工具 #产品体验 #生产力\n",
            "```\n\n"
        ])

        # 思考分享模板
        templates.extend([
            "### 💡 思考分享模板\n\n",
            "```\n",
            "🤔 关于[话题]的一些思考\n\n",
            "最近在学习/使用[具体内容]的过程中，有一个有趣的发现：\n\n",
            "[核心观点或洞察]\n\n",
            "这让我想到：\n",
            "• [延伸思考1]\n",
            "• [延伸思考2]\n",
            "• [实际应用]\n\n",
            "你们怎么看？欢迎在评论区分享你的想法👇\n\n",
            "#深度思考 #行业洞察 #互动讨论\n",
            "```\n\n"
        ])

        return ''.join(templates)

    def generate_keyword_analysis(self, keywords: Dict[str, int]) -> str:
        """生成关键词分析。"""
        if not keywords:
            return ""

        analysis = ["## 📊 关键词分析\n\n"]

        # 热门关键词排行
        analysis.append("### 🔥 热门关键词排行\n\n")

        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:15]
        for keyword_info, _ in sorted_keywords:
            parts = keyword_info.split(':')
            if len(parts) >= 3:
                keyword, count, source = parts[0], parts[1], parts[2]
                analysis.append(f"- **{keyword}** (出现 {count} 次，来源: {source})\n")

        analysis.append("\n")

        # 分类关键词统计
        analysis.append("### 📂 分类关键词统计\n\n")

        for category in ['video', 'newsletter', 'braindump', 'output', 'review']:
            category_keywords = [k for k in sorted_keywords if k[0].endswith(f':{category}')]

            if category_keywords:
                analysis.append(f"**{category} 相关关键词 ({len(category_keywords)} 个):**\n")
                for keyword_info, _ in category_keywords[:5]:
                    parts = keyword_info.split(':')
                    if len(parts) >= 2:
                        keyword, count = parts[0], parts[1]
                        analysis.append(f"- {keyword} ({count})\n")
                analysis.append("\n")

        return ''.join(analysis)


def parse_arguments():
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description='Generate insight report from learning records')
    parser.add_argument('--days', type=int, help='Analyze content from last N days')
    parser.add_argument('--weeks', type=int, help='Analyze content from last N weeks')
    parser.add_argument('--all', action='store_true', help='Analyze all historical content')
    parser.add_argument('--topic', help='Focus on specific topic analysis')
    parser.add_argument('--platform', choices=['xiaohongshu', 'weibo', 'linkedin', 'twitter'],
                       help='Optimize for specific platform')
    parser.add_argument('--format', choices=['markdown', 'json', 'html'], default='markdown',
                       help='Output format')
    parser.add_argument('--save', help='Save result to file')
    parser.add_argument('--verbose', action='store_true', help='Show detailed analysis process')
    parser.add_argument('--ai-analysis', action='store_true', help='Enable AI deep analysis')

    return parser.parse_args()


def main():
    """主函数，执行insight命令逻辑。"""
    try:
        args = parse_arguments()

        print("🎯 启动内容洞察分析...", file=sys.stderr)

        # 创建分析器
        analyzer = InsightAnalyzer()

        # 提取学习内容
        analyzer.extract_learning_content(
            days=args.days,
            weeks=args.weeks,
            all_content=args.all
        )

        if analyzer.analyzed_files == 0:
            print("未找到符合条件的学习记录文件。")
            return

        # 分析主题和关键词
        keywords = analyzer.analyze_content_themes()

        # 识别高价值内容
        valuable_content = analyzer.identify_valuable_content()

        # 生成社交媒体建议
        social_suggestions = analyzer.generate_social_media_suggestions(
            keywords, valuable_content, args.platform
        )

        # 生成内容模板
        content_templates = analyzer.create_content_templates()

        # 生成平台专属示例
        platform_examples = analyzer.generate_platform_content_examples(valuable_content)

        # 生成关键词分析
        keyword_analysis = analyzer.generate_keyword_analysis(keywords)

        # 生成报告
        current_date = DateUtils.format_chinese_date(DateUtils.get_current_date())

        # 确定分析范围描述
        if args.all:
            analysis_range = "所有历史内容"
        elif args.days:
            analysis_range = f"最近 {args.days} 天"
        elif args.weeks:
            analysis_range = f"最近 {args.weeks} 周"
        else:
            analysis_range = "最近 7 天"

        # 生成最终报告
        report_content = [
            f"# 🎯 Insight Report - {current_date}\n\n",
            "## 📈 分析摘要\n\n",
            f"- **分析范围**: {analysis_range}\n",
            f"- **分析文件数**: {analyzer.analyzed_files} 个学习记录\n",
            f"- **主题焦点**: {args.topic if args.topic else '全部主题'}\n",
            f"- **目标平台**: {args.platform if args.platform else '通用平台'}\n\n"
        ]

        # AI分析占位符
        if args.ai_analysis:
            report_content.extend([
                "## 🧠 AI 深度分析报告\n\n",
                "### ⚠️ AI分析说明\n\n",
                "AI深度分析功能需要在Claude Code环境中使用。请在Claude Code中运行此命令以获得：\n\n",
                "- 🎯 内容价值评估和传播潜力分析\n",
                "- 👥 目标受众画像和平台推荐\n",
                "- ✍️ 多风格文案建议和标题优化\n",
                "- 🖼️ 配图方向和视觉呈现建议\n",
                "- ⏰ 最佳发布时机和策略建议\n\n"
            ])

        # 添加高价值内容片段
        if valuable_content['insights'] or valuable_content['achievements']:
            report_content.append("## 🌟 高价值内容片段\n\n")

            if valuable_content['insights']:
                report_content.append("### 💡 深度思考与洞察\n\n")
                for insight in valuable_content['insights'][:10]:
                    if ':' in insight:
                        date_str, content = insight.split(':', 1)
                        report_content.append(f"- **{date_str}**: {content.strip()}\n")
                report_content.append("\n")

            if valuable_content['achievements']:
                report_content.append("### 🎯 学习成果与产出\n\n")
                for achievement in valuable_content['achievements'][:8]:
                    if ':' in achievement:
                        date_str, content = achievement.split(':', 1)
                        report_content.append(f"- **{date_str}**: {content.strip()}\n")
                report_content.append("\n")

        # 添加其他部分
        report_content.append(social_suggestions)
        report_content.append(content_templates)
        report_content.append(platform_examples)
        report_content.append(keyword_analysis)

        # 添加下一步行动建议
        report_content.extend([
            "## 🎯 下一步行动建议\n\n",
            "### 📅 内容创作计划\n\n",
            "- **本周重点**: 选择1-2个高价值内容片段，制作成社交媒体帖子\n",
            "- **内容日程**: \n",
            "  - 周一：发布学习总结类内容\n",
            "  - 周三：分享工具体验或产品评测\n",
            "  - 周五：发布思考洞察类内容\n",
            "- **互动策略**: 在帖子中加入问题，鼓励读者评论和分享\n",
            "- **内容优化**: 根据不同平台特点调整内容格式和长度\n\n",
            "### 🔄 持续改进\n\n",
            "- 定期使用 `/insight` 命令分析学习内容（建议每周一次）\n",
            "- 跟踪发布内容的反馈和互动数据\n",
            "- 根据受众反应调整内容主题和风格\n",
            "- 建立内容素材库，积累可复用的观点和金句\n\n",
            "---\n",
            "*本报告由 /insight 命令自动生成，基于您的学习记录分析*\n"
        ])

        final_report = ''.join(report_content)

        # 输出报告
        if args.save:
            FileUtils.write_file(args.save, final_report)
            print(f"✅ 洞察报告已保存到: {args.save}", file=sys.stderr)
        else:
            print(final_report)

        print("🎉 分析完成！", file=sys.stderr)

    except Exception as e:
        print(f"Error generating insight report: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()