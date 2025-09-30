"""
File utilities for learning journal commands.
文件工具模块，提供文件操作和路径管理功能。
"""

import os
import glob
from pathlib import Path
from typing import List, Optional, Tuple


class FileUtils:
    """文件工具类，提供学习日记系统所需的各种文件操作功能。"""

    @staticmethod
    def ensure_directory(path: str) -> None:
        """
        确保目录存在，如果不存在则创建。

        Args:
            path: 目录路径
        """
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_weeks_directory() -> str:
        """
        获取weeks目录路径。

        Returns:
            weeks目录的绝对路径
        """
        return os.path.abspath("weeks")

    @staticmethod
    def get_week_folder_path(folder_name: str) -> str:
        """
        获取周文件夹的完整路径。

        Args:
            folder_name: 周文件夹名称 (如: 2025_0901-0907)

        Returns:
            周文件夹的完整路径
        """
        weeks_dir = FileUtils.get_weeks_directory()
        return os.path.join(weeks_dir, folder_name)

    @staticmethod
    def get_daily_file_path(week_folder: str, daily_filename: str) -> str:
        """
        获取日记文件的完整路径。

        Args:
            week_folder: 周文件夹路径
            daily_filename: 日记文件名

        Returns:
            日记文件的完整路径
        """
        return os.path.join(week_folder, daily_filename)

    @staticmethod
    def file_exists(path: str) -> bool:
        """
        检查文件是否存在。

        Args:
            path: 文件路径

        Returns:
            文件是否存在
        """
        return os.path.isfile(path)

    @staticmethod
    def directory_exists(path: str) -> bool:
        """
        检查目录是否存在。

        Args:
            path: 目录路径

        Returns:
            目录是否存在
        """
        return os.path.isdir(path)

    @staticmethod
    def write_file(path: str, content: str) -> None:
        """
        写入文件内容。

        Args:
            path: 文件路径
            content: 文件内容
        """
        # 确保父目录存在
        parent_dir = os.path.dirname(path)
        if parent_dir:
            FileUtils.ensure_directory(parent_dir)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def read_file(path: str) -> Optional[str]:
        """
        读取文件内容。

        Args:
            path: 文件路径

        Returns:
            文件内容，如果文件不存在返回None
        """
        if not FileUtils.file_exists(path):
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(path, 'r', encoding='gbk') as f:
                    return f.read()
            except UnicodeDecodeError:
                return None

    @staticmethod
    def append_to_file(path: str, content: str) -> None:
        """
        向文件追加内容。

        Args:
            path: 文件路径
            content: 要追加的内容
        """
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def find_daily_files(weeks_dir: Optional[str] = None) -> List[str]:
        """
        查找所有日记文件。

        Args:
            weeks_dir: weeks目录路径，默认为当前目录下的weeks

        Returns:
            日记文件路径列表，按文件名排序
        """
        if weeks_dir is None:
            weeks_dir = FileUtils.get_weeks_directory()

        if not FileUtils.directory_exists(weeks_dir):
            return []

        # 查找所有符合YYYY_MM_DD.md格式的文件
        pattern = os.path.join(weeks_dir, "**", "????_??_??.md")
        files = glob.glob(pattern, recursive=True)

        # 按文件名排序
        return sorted(files)

    @staticmethod
    def find_week_directories() -> List[str]:
        """
        查找所有周目录。

        Returns:
            周目录路径列表，按名称排序
        """
        weeks_dir = FileUtils.get_weeks_directory()

        if not FileUtils.directory_exists(weeks_dir):
            return []

        directories = []
        for item in os.listdir(weeks_dir):
            item_path = os.path.join(weeks_dir, item)
            if os.path.isdir(item_path) and item.count('_') == 1 and '-' in item:
                directories.append(item_path)

        return sorted(directories)

    @staticmethod
    def get_files_in_directory(directory: str, pattern: str = "*") -> List[str]:
        """
        获取目录中符合模式的文件。

        Args:
            directory: 目录路径
            pattern: 文件名模式

        Returns:
            文件路径列表
        """
        if not FileUtils.directory_exists(directory):
            return []

        search_pattern = os.path.join(directory, pattern)
        return sorted(glob.glob(search_pattern))

    @staticmethod
    def get_earliest_daily_file() -> Optional[Tuple[str, str]]:
        """
        获取最早的日记文件。

        Returns:
            (文件路径, 日期字符串) 或 None
        """
        daily_files = FileUtils.find_daily_files()

        if not daily_files:
            return None

        earliest_file = daily_files[0]
        filename = os.path.basename(earliest_file)

        # 提取日期 (YYYY_MM_DD.md -> YYYY-MM-DD)
        if filename.endswith('.md'):
            date_part = filename[:-3]
            date_str = date_part.replace('_', '-')
            return earliest_file, date_str

        return None

    @staticmethod
    def backup_file(path: str) -> Optional[str]:
        """
        备份文件。

        Args:
            path: 要备份的文件路径

        Returns:
            备份文件路径，如果备份失败返回None
        """
        if not FileUtils.file_exists(path):
            return None

        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup_{timestamp}"

        try:
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception:
            return None

    @staticmethod
    def get_file_size(path: str) -> int:
        """
        获取文件大小。

        Args:
            path: 文件路径

        Returns:
            文件大小（字节），如果文件不存在返回0
        """
        if not FileUtils.file_exists(path):
            return 0

        return os.path.getsize(path)

    @staticmethod
    def get_relative_path(path: str, base_path: Optional[str] = None) -> str:
        """
        获取相对路径。

        Args:
            path: 绝对路径
            base_path: 基准路径，默认为当前工作目录

        Returns:
            相对路径
        """
        if base_path is None:
            base_path = os.getcwd()

        return os.path.relpath(path, base_path)