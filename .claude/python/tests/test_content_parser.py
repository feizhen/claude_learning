#!/usr/bin/env python3
"""
Tests for content_parser module.
"""

import unittest
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.content_parser import ContentParser


class TestContentParser(unittest.TestCase):
    """测试ContentParser类。"""

    def setUp(self):
        """测试设置。"""
        self.sample_content = """# 0926 Journal

## video

- [AI Tutorial] Introduction to Machine Learning
- [Python Course] Advanced Data Structures

## newsletter

[] AI Valley
[x] The Keyword

## braindump

- 今天学习了机器学习的基础概念
- 对于产品设计有了新的思考
- 发现了一个很有意思的工具

## output

- 完成了一个小型demo项目
- 写了一篇技术总结

## review

今日学习总结：学习效果很好，掌握了核心概念。
建议明日继续深入学习算法部分。
"""

    def test_extract_section(self):
        """测试提取章节内容。"""
        # 测试提取video章节
        video_content = ContentParser.extract_section(self.sample_content, 'video')
        self.assertIn('AI Tutorial', video_content)
        self.assertIn('Python Course', video_content)

        # 测试提取不存在的章节
        nonexistent = ContentParser.extract_section(self.sample_content, 'nonexistent')
        self.assertIsNone(nonexistent)

    def test_extract_all_sections(self):
        """测试提取所有章节。"""
        sections = ContentParser.extract_all_sections(self.sample_content)

        self.assertIn('video', sections)
        self.assertIn('newsletter', sections)
        self.assertIn('braindump', sections)
        self.assertIn('output', sections)
        self.assertIn('review', sections)

        # 检查内容是否正确
        self.assertIn('AI Tutorial', sections['video'])
        self.assertIn('AI Valley', sections['newsletter'])

    def test_has_section(self):
        """测试检查是否包含章节。"""
        self.assertTrue(ContentParser.has_section(self.sample_content, 'video'))
        self.assertTrue(ContentParser.has_section(self.sample_content, 'review'))
        self.assertFalse(ContentParser.has_section(self.sample_content, 'nonexistent'))

    def test_count_section_items(self):
        """测试统计章节条目数量。"""
        video_count = ContentParser.count_section_items(self.sample_content, 'video')
        self.assertEqual(video_count, 2)

        braindump_count = ContentParser.count_section_items(self.sample_content, 'braindump')
        self.assertEqual(braindump_count, 3)

        nonexistent_count = ContentParser.count_section_items(self.sample_content, 'nonexistent')
        self.assertEqual(nonexistent_count, 0)

    def test_extract_checkbox_items(self):
        """测试提取复选框项目统计。"""
        total, completed = ContentParser.extract_checkbox_items(self.sample_content, 'newsletter')
        self.assertEqual(total, 2)
        self.assertEqual(completed, 1)

    def test_extract_links(self):
        """测试提取链接。"""
        content_with_links = "Check out [OpenAI](https://openai.com) and [Google](https://google.com)"
        links = ContentParser.extract_links(content_with_links)

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0], ('OpenAI', 'https://openai.com'))
        self.assertEqual(links[1], ('Google', 'https://google.com'))

    def test_extract_keywords(self):
        """测试提取关键词。"""
        keywords = ['学习', 'AI', '项目']
        keyword_counts = ContentParser.extract_keywords(self.sample_content, keywords)

        self.assertIn('学习', keyword_counts)
        self.assertIn('AI', keyword_counts)
        self.assertIn('项目', keyword_counts)

        # 检查计数
        self.assertGreater(keyword_counts['学习'], 0)

    def test_remove_section(self):
        """测试移除章节。"""
        content_without_video = ContentParser.remove_section(self.sample_content, 'video')

        # 确保video章节被移除
        self.assertNotIn('## video', content_without_video)
        self.assertNotIn('AI Tutorial', content_without_video)

        # 确保其他章节仍然存在
        self.assertIn('## newsletter', content_without_video)
        self.assertIn('## braindump', content_without_video)

    def test_replace_section(self):
        """测试替换章节。"""
        new_video_content = "- [New Video] Test Content"
        updated_content = ContentParser.replace_section(self.sample_content, 'video', new_video_content)

        # 检查新内容是否存在
        self.assertIn('New Video', updated_content)

        # 检查旧内容是否被移除
        self.assertNotIn('AI Tutorial', updated_content)

    def test_get_section_summary(self):
        """测试获取章节摘要。"""
        summary = ContentParser.get_section_summary(self.sample_content)

        # 检查所有标准章节都有摘要
        for section_name in ContentParser.STANDARD_SECTIONS:
            self.assertIn(section_name, summary)

        # 检查存在的章节
        self.assertTrue(summary['video']['exists'])
        self.assertGreater(summary['video']['word_count'], 0)
        self.assertGreater(summary['video']['line_count'], 0)

        # 检查不存在的章节
        if 'TODO' in summary:
            self.assertFalse(summary['TODO']['exists'])
            self.assertEqual(summary['TODO']['word_count'], 0)


if __name__ == '__main__':
    unittest.main()