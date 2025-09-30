"""
Template management for learning journal.
模板管理模块，提供各种内容模板。
"""

from typing import Dict, Any
import datetime


class Templates:
    """模板管理类，提供各种内容生成模板。"""

    @staticmethod
    def daily_journal_template(date: datetime.date) -> str:
        """
        生成日记模板。

        Args:
            date: 日期

        Returns:
            日记模板内容
        """
        header_date = date.strftime("%m%d")

        return f"""# {header_date} Journal

## video


## newsletter

[] AI Vally

[] The Keyword

## braindump


## output

"""

    @staticmethod
    def week_review_template(monday: datetime.date, sunday: datetime.date, folder_name: str) -> str:
        """
        生成周总结模板。

        Args:
            monday: 周一日期
            sunday: 周日日期
            folder_name: 文件夹名称

        Returns:
            周总结模板内容
        """
        monday_str = monday.strftime("%B %d")
        sunday_str = sunday.strftime("%B %d, %Y")

        return f"""# Weekly Review: {folder_name}

Week of {monday_str} - {sunday_str}

## Summary

## Daily Summaries

"""

    @staticmethod
    def milestone_report_template(current_date: str, current_month: int, start_date: str) -> str:
        """
        生成里程碑报告模板。

        Args:
            current_date: 当前日期
            current_month: 当前月份
            start_date: 开始日期

        Returns:
            里程碑报告模板
        """
        return f"""# Milestone Report - {current_date}

## 🎯 当前阶段

- **计划月份**: 月 {current_month}
- **学习开始日期**: {start_date}

## 📊 学习统计

## ✅ 主要成就

## 📈 学习习惯评估

## ⚠️ 差距分析

## 🚀 改进建议

"""

    @staticmethod
    def insight_report_template(current_date: str, analysis_range: str, analyzed_count: int) -> str:
        """
        生成洞察报告模板。

        Args:
            current_date: 当前日期
            analysis_range: 分析范围
            analyzed_count: 分析文件数量

        Returns:
            洞察报告模板
        """
        return f"""# 🎯 Insight Report - {current_date}

## 📈 分析摘要

- **分析范围**: {analysis_range}
- **分析文件数**: {analyzed_count} 个学习记录

## 🌟 高价值内容片段

## 🚀 社交媒体内容建议

## 📄 内容创作模板

## 📊 关键词分析

## 🎯 下一步行动建议

---
*本报告由 /insight 命令自动生成，基于您的学习记录分析*
"""

    @staticmethod
    def daily_review_template(activity_summary: str, habits_analysis: str, insights: str, recommendations: str) -> str:
        """
        生成每日总结模板。

        Args:
            activity_summary: 活动总结
            habits_analysis: 习惯分析
            insights: 主要收获
            recommendations: 建议

        Returns:
            每日总结内容
        """
        return f"""
## review

**今日学习活动总结:**

{activity_summary}

{habits_analysis}

**主要收获:**
{insights}

{recommendations}
"""

    @staticmethod
    def learning_habit_analysis_template(video_count: int, newsletter_count: int,
                                       braindump_count: int, output_count: int,
                                       content_diversity: int, total_days: int,
                                       days_since_start: int) -> str:
        """
        生成学习习惯分析模板。

        Args:
            video_count: 视频学习数量
            newsletter_count: 文章阅读数量
            braindump_count: 思考记录数量
            output_count: 输出数量
            content_diversity: 内容多样性评分
            total_days: 学习总天数
            days_since_start: 开始以来的天数

        Returns:
            学习习惯分析内容
        """
        learning_frequency_pct = (total_days * 100 // days_since_start) if days_since_start > 0 else 0

        frequency_status = "✅ 学习频率很高，保持良好习惯" if learning_frequency_pct >= 80 else \
                          "⚠️ 学习频率中等，可以进一步提升" if learning_frequency_pct >= 60 else \
                          "❌ 学习频率偏低，需要建立更规律的学习习惯"

        diversity_status = "✅ 内容类型分布均衡" if content_diversity >= 3 else \
                          "⚠️ 建议增加学习内容的多样性"

        return f"""学习习惯评估 ({content_diversity * 25}/100分):

- ✅ 视频学习：包含实用的学习视频内容
- ✅ 阅读输入：关注行业动态和知识更新
- ✅ 深度思考：记录了丰富的思考和洞察 ({braindump_count} 条)
- ✅ 学习输出：有实际的学习成果产出

🎯 **学习状态**: 今日学习内容均衡，输入输出兼备，学习习惯良好

### 一致性评估

- **学习频率**: {learning_frequency_pct}% ({total_days}/{days_since_start} 天)
  - {frequency_status}
- **内容平衡度**:
  - 视频学习: {video_count}
  - 文章阅读: {newsletter_count}
  - 思考记录: {braindump_count}
  - {diversity_status}
"""

    @staticmethod
    def social_media_content_template(platform: str, content_type: str) -> str:
        """
        生成社交媒体内容模板。

        Args:
            platform: 平台名称
            content_type: 内容类型

        Returns:
            社交媒体内容模板
        """
        templates = {
            "xiaohongshu": {
                "tool_review": """🚀 又发现一个宝藏AI工具！

姐妹们，今天必须要分享这个发现！

✨ [工具体验和感受]

🔥 最让我惊喜的几个点：
1️⃣ [亮点1]
2️⃣ [亮点2]
3️⃣ [亮点3]

💡 适合人群：
• [目标用户1]
• [目标用户2]

评分：⭐⭐⭐⭐⭐

你们还有什么好用的AI工具推荐吗？评论区见👇

#AI工具 #效率神器 #产品体验 #科技分享 #学习笔记""",

                "learning_summary": """📚 这周的学习收获 #学习记录 #AI学习

本周重点学习了：
🔸 [技术/工具名称] - [简短描述]
🔸 [重要概念] - [个人理解]
🔸 [实践项目] - [具体成果]

💡 最大的收获：
[写出最有价值的洞察或体验]

🎯 下周计划：
[简述下周学习重点]

#持续学习 #技术成长 #个人发展"""
            },

            "weibo": {
                "insight_sharing": """💡 产品观察：[核心观点]

作为一个产品爱好者，今天深度体验了这个AI工具，几个值得思考的点：

1. [思考点1]
2. [思考点2]
3. [思考点3]

这让我想到，[延伸思考]。

你觉得一个AI产品最重要的是什么？技术还是体验？

#产品思考 #AI工具 #用户体验 #产品设计 #科技观察"""
            },

            "linkedin": {
                "professional_insight": """🎯 Product Insights: [标题]

After spending time with [具体内容], I was struck by [关键观察].

Key observations:

🔸 [观察1]
🔸 [观察2]
🔸 [观察3]

This reinforces something I've been thinking about: [深度思考].

For product teams building in this space:
• [建议1]
• [建议2]
• [建议3]

What's your experience with [相关话题]? What barriers have you encountered?

#ProductManagement #AITools #UserExperience #TechInnovation #ProductDesign"""
            }
        }

        return templates.get(platform, {}).get(content_type, "模板未找到")

    @staticmethod
    def content_analysis_keywords() -> Dict[str, str]:
        """
        获取内容分析关键词。

        Returns:
            关键词分类字典
        """
        return {
            "technology": "AI|人工智能|大模型|LLM|GPT|Claude|ChatGPT|机器学习|深度学习|神经网络|编程|代码|开发|程序|软件|产品|设计|用户体验|UX|UI|Python|JavaScript|React|Vue|Node|后端|前端|全栈|数据库|API|云计算|AWS|阿里云|腾讯云|Docker|Kubernetes|微服务|架构",

            "tools": "Replit|HeyGen|Figma|Notion|Slack|GitHub|GitLab|VSCode|Jupyter|小红书|微博|LinkedIn|Twitter|抖音|B站|YouTube|TikTok|数字人|视频生成|图像处理|自动化|效率工具|生产力",

            "business": "创业|投资|融资|IPO|独角兽|估值|商业模式|变现|增长|用户|流量|SaaS|B2B|B2C|C端|B端|ToB|ToC|平台|生态|社区|开源",

            "learning": "目标管理|时间管理|效率|习惯|成长|学习|技能|能力|经验|总结|反思|面试|求职|跳槽|职业发展|转岗|晋升|领导力|沟通|协作|团队"
        }