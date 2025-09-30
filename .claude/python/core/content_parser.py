"""
Content parser for markdown files.
内容解析器模块，用于解析和处理markdown文件内容。
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MarkdownSection:
    """Markdown章节数据结构。"""
    title: str
    content: str
    line_start: int
    line_end: int


class ContentParser:
    """内容解析器类，用于解析和处理学习日记markdown文件。"""

    # 标准的日记章节
    STANDARD_SECTIONS = ["video", "newsletter", "braindump", "output", "review", "TODO", "WayToAce"]

    @staticmethod
    def extract_section(content: str, section_name: str) -> Optional[str]:
        """
        从markdown内容中提取指定章节的内容。

        Args:
            content: markdown文件内容
            section_name: 章节名称 (如 "video", "newsletter")

        Returns:
            章节内容，如果章节不存在返回None
        """
        if not content:
            return None

        # 构建正则表达式模式，匹配章节标题和内容
        pattern = rf'^## {re.escape(section_name)}$\s*(.*?)(?=^## \w+|$)'

        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            section_content = match.group(1).strip()
            # 过滤掉空行
            lines = [line for line in section_content.split('\n') if line.strip()]
            return '\n'.join(lines) if lines else None

        return None

    @staticmethod
    def extract_all_sections(content: str) -> Dict[str, str]:
        """
        提取所有章节内容。

        Args:
            content: markdown文件内容

        Returns:
            章节名称到内容的映射
        """
        sections = {}

        for section_name in ContentParser.STANDARD_SECTIONS:
            section_content = ContentParser.extract_section(content, section_name)
            if section_content:
                sections[section_name] = section_content

        return sections

    @staticmethod
    def parse_sections_with_positions(content: str) -> List[MarkdownSection]:
        """
        解析所有章节，包含位置信息。

        Args:
            content: markdown文件内容

        Returns:
            章节列表，包含位置信息
        """
        sections = []
        lines = content.split('\n')

        current_section = None
        current_content_lines = []
        current_start = 0

        for i, line in enumerate(lines):
            # 检查是否是章节标题
            match = re.match(r'^## (\w+)$', line.strip())

            if match:
                # 保存上一个章节
                if current_section:
                    content_str = '\n'.join(current_content_lines).strip()
                    sections.append(MarkdownSection(
                        title=current_section,
                        content=content_str,
                        line_start=current_start,
                        line_end=i - 1
                    ))

                # 开始新章节
                current_section = match.group(1)
                current_content_lines = []
                current_start = i + 1
            elif current_section:
                # 添加到当前章节内容
                current_content_lines.append(line)

        # 处理最后一个章节
        if current_section:
            content_str = '\n'.join(current_content_lines).strip()
            sections.append(MarkdownSection(
                title=current_section,
                content=content_str,
                line_start=current_start,
                line_end=len(lines) - 1
            ))

        return sections

    @staticmethod
    def has_section(content: str, section_name: str) -> bool:
        """
        检查是否包含指定章节。

        Args:
            content: markdown文件内容
            section_name: 章节名称

        Returns:
            是否包含该章节
        """
        return ContentParser.extract_section(content, section_name) is not None

    @staticmethod
    def count_section_items(content: str, section_name: str) -> int:
        """
        统计章节中的条目数量（以"-"开头的行）。

        Args:
            content: markdown文件内容
            section_name: 章节名称

        Returns:
            条目数量
        """
        section_content = ContentParser.extract_section(content, section_name)
        if not section_content:
            return 0

        # 统计以"-"开头的行
        lines = section_content.split('\n')
        return len([line for line in lines if line.strip().startswith('-')])

    @staticmethod
    def extract_checkbox_items(content: str, section_name: str) -> Tuple[int, int]:
        """
        提取章节中的复选框项目统计。

        Args:
            content: markdown文件内容
            section_name: 章节名称

        Returns:
            (总数量, 已完成数量)
        """
        section_content = ContentParser.extract_section(content, section_name)
        if not section_content:
            return 0, 0

        lines = section_content.split('\n')
        total = 0
        completed = 0

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- ['):
                total += 1
                if stripped.startswith('- [x]') or stripped.startswith('- [X]'):
                    completed += 1

        return total, completed

    @staticmethod
    def extract_links(content: str) -> List[Tuple[str, str]]:
        """
        提取内容中的所有链接。

        Args:
            content: markdown内容

        Returns:
            [(链接文本, 链接URL), ...] 列表
        """
        # 匹配markdown链接格式 [文本](URL)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(link_pattern, content)

        return matches

    @staticmethod
    def extract_keywords(content: str, keywords: List[str]) -> Dict[str, int]:
        """
        提取指定关键词在内容中的出现次数。

        Args:
            content: 内容文本
            keywords: 关键词列表

        Returns:
            关键词到出现次数的映射
        """
        keyword_counts = {}

        for keyword in keywords:
            # 使用不区分大小写的匹配
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                keyword_counts[keyword] = len(matches)

        return keyword_counts

    @staticmethod
    def remove_section(content: str, section_name: str) -> str:
        """
        从内容中移除指定章节。

        Args:
            content: markdown内容
            section_name: 要移除的章节名称

        Returns:
            移除章节后的内容
        """
        # 匹配整个章节（包括标题）
        pattern = rf'^## {re.escape(section_name)}$.*?(?=^## \w+|$)'

        result = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)

        # 清理多余的空行
        lines = result.split('\n')
        cleaned_lines = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()

            if not (is_empty and prev_empty):
                cleaned_lines.append(line)

            prev_empty = is_empty

        return '\n'.join(cleaned_lines)

    @staticmethod
    def replace_section(content: str, section_name: str, new_content: str) -> str:
        """
        替换指定章节的内容。

        Args:
            content: 原始markdown内容
            section_name: 章节名称
            new_content: 新的章节内容

        Returns:
            替换后的内容
        """
        # 先移除原章节
        content_without_section = ContentParser.remove_section(content, section_name)

        # 添加新章节
        section_block = f"\n## {section_name}\n\n{new_content}\n"

        return content_without_section + section_block

    @staticmethod
    def get_section_summary(content: str) -> Dict[str, dict]:
        """
        获取所有章节的摘要信息。

        Args:
            content: markdown内容

        Returns:
            章节摘要信息
        """
        summary = {}

        for section_name in ContentParser.STANDARD_SECTIONS:
            section_content = ContentParser.extract_section(content, section_name)

            if section_content:
                lines = section_content.split('\n')
                word_count = len(section_content.split())
                line_count = len([line for line in lines if line.strip()])
                item_count = ContentParser.count_section_items(content, section_name)

                summary[section_name] = {
                    'exists': True,
                    'word_count': word_count,
                    'line_count': line_count,
                    'item_count': item_count,
                    'first_line': lines[0][:100] + '...' if lines and len(lines[0]) > 100 else (lines[0] if lines else '')
                }
            else:
                summary[section_name] = {
                    'exists': False,
                    'word_count': 0,
                    'line_count': 0,
                    'item_count': 0,
                    'first_line': ''
                }

        return summary