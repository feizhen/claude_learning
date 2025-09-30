#!/usr/bin/env python3
"""
Test runner for learning journal Python modules.
"""

import unittest
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """运行所有测试。"""
    # 发现并加载所有测试
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(__file__)

    # 加载当前目录下的所有测试
    suite = loader.discover(test_dir, pattern='test_*.py')

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


def run_specific_test(test_module):
    """运行特定测试模块。"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        test_module = sys.argv[1]
        success = run_specific_test(test_module)
    else:
        # 运行所有测试
        success = run_all_tests()

    sys.exit(0 if success else 1)