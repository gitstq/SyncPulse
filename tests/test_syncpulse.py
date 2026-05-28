#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyncPulse Test Suite
轻量级终端文件智能同步与备份引擎 - 测试套件
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from syncpulse import (
    FileHasher, FileScanner, SyncEngine, SyncConfig, 
    FileInfo, Logger, LogLevel, ConfigManager, SyncMode
)


class TestFileHasher(unittest.TestCase):
    """测试文件哈希计算器"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Hello, SyncPulse!")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_calculate_checksum(self):
        """测试校验和计算"""
        checksum = FileHasher.calculate_checksum(self.test_file, "md5")
        self.assertIsInstance(checksum, str)
        self.assertEqual(len(checksum), 32)  # MD5长度
    
    def test_calculate_checksum_blake2b(self):
        """测试Blake2b算法"""
        checksum = FileHasher.calculate_checksum(self.test_file, "blake2b")
        self.assertIsInstance(checksum, str)
        self.assertTrue(len(checksum) > 0)
    
    def test_calculate_checksum_nonexistent(self):
        """测试不存在的文件"""
        checksum = FileHasher.calculate_checksum("/nonexistent/file.txt")
        self.assertEqual(checksum, "")
    
    def test_quick_hash(self):
        """测试快速哈希"""
        quick_hash = FileHasher.quick_hash(self.test_file)
        self.assertIsInstance(quick_hash, str)
        self.assertEqual(len(quick_hash), 16)


class TestSyncConfig(unittest.TestCase):
    """测试同步配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = SyncConfig(source="/src", destination="/dst")
        self.assertEqual(config.source, "/src")
        self.assertEqual(config.destination, "/dst")
        self.assertEqual(config.mode, "incremental")
        self.assertTrue(config.preserve_permissions)
        self.assertTrue(config.preserve_timestamps)
        self.assertEqual(config.version_count, 5)
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = SyncConfig(
            source="/src",
            destination="/dst",
            mode="mirror",
            exclude_patterns=["*.tmp"],
            version_count=3
        )
        self.assertEqual(config.mode, "mirror")
        self.assertEqual(config.exclude_patterns, ["*.tmp"])
        self.assertEqual(config.version_count, 3)


class TestFileScanner(unittest.TestCase):
    """测试文件扫描器"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Logger(level=LogLevel.ERROR, quiet=True)
        self.config = SyncConfig(source=self.temp_dir, destination="/dst")
        self.scanner = FileScanner(self.config, self.logger)
        
        # 创建测试文件结构
        os.makedirs(os.path.join(self.temp_dir, "subdir"))
        with open(os.path.join(self.temp_dir, "file1.txt"), 'w') as f:
            f.write("content1")
        with open(os.path.join(self.temp_dir, "subdir", "file2.txt"), 'w') as f:
            f.write("content2")
        with open(os.path.join(self.temp_dir, "temp.tmp"), 'w') as f:
            f.write("temp")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_should_exclude(self):
        """测试排除规则"""
        self.assertTrue(self.scanner.should_exclude("test.tmp"))
        self.assertTrue(self.scanner.should_exclude(".git"))
        self.assertFalse(self.scanner.should_exclude("file.txt"))
    
    def test_scan_directory(self):
        """测试目录扫描"""
        files_info = self.scanner.scan_directory(self.temp_dir)
        
        # 应该找到2个文件（temp.tmp被排除）
        self.assertEqual(len(files_info), 2)
        
        # 检查文件信息
        self.assertIn("file1.txt", files_info)
        self.assertIn(os.path.join("subdir", "file2.txt"), files_info)
    
    def test_scan_nonexistent_directory(self):
        """测试扫描不存在的目录"""
        files_info = self.scanner.scan_directory("/nonexistent/path")
        self.assertEqual(len(files_info), 0)


class TestSyncEngine(unittest.TestCase):
    """测试同步引擎"""
    
    def setUp(self):
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()
        self.logger = Logger(level=LogLevel.ERROR, quiet=True)
        
        # 创建源文件
        with open(os.path.join(self.src_dir, "file1.txt"), 'w') as f:
            f.write("content1")
        os.makedirs(os.path.join(self.src_dir, "subdir"))
        with open(os.path.join(self.src_dir, "subdir", "file2.txt"), 'w') as f:
            f.write("content2")
    
    def tearDown(self):
        shutil.rmtree(self.src_dir)
        shutil.rmtree(self.dst_dir)
    
    def test_incremental_sync(self):
        """测试增量同步"""
        config = SyncConfig(
            source=self.src_dir,
            destination=self.dst_dir,
            mode="incremental"
        )
        engine = SyncEngine(config, self.logger)
        
        success = engine.sync(dry_run=False)
        self.assertTrue(success)
        
        # 验证文件已复制
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "file1.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.dst_dir, "subdir", "file2.txt")))
        
        # 验证统计
        self.assertEqual(engine.stats["files_copied"], 2)
    
    def test_dry_run(self):
        """测试模拟运行"""
        config = SyncConfig(
            source=self.src_dir,
            destination=self.dst_dir,
            mode="incremental"
        )
        engine = SyncEngine(config, self.logger)
        
        success = engine.sync(dry_run=True)
        self.assertTrue(success)
        
        # 验证文件未实际复制
        self.assertFalse(os.path.exists(os.path.join(self.dst_dir, "file1.txt")))
    
    def test_mirror_sync(self):
        """测试镜像同步"""
        # 先在目标目录创建一个额外文件
        with open(os.path.join(self.dst_dir, "extra.txt"), 'w') as f:
            f.write("extra")
        
        config = SyncConfig(
            source=self.src_dir,
            destination=self.dst_dir,
            mode="mirror"
        )
        engine = SyncEngine(config, self.logger)
        
        success = engine.sync(dry_run=False)
        self.assertTrue(success)
        
        # 验证额外文件被删除
        self.assertFalse(os.path.exists(os.path.join(self.dst_dir, "extra.txt")))


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        test_config = {
            "profiles": {
                "test": {
                    "source": "/test/src",
                    "destination": "/test/dst"
                }
            }
        }
        
        ConfigManager.save_config(test_config, self.config_path)
        loaded_config = ConfigManager.load_config(self.config_path)
        
        self.assertEqual(loaded_config["profiles"]["test"]["source"], "/test/src")
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置"""
        config = ConfigManager.load_config("/nonexistent/config.json")
        self.assertEqual(config, {})
    
    def test_create_default_config(self):
        """测试创建默认配置"""
        ConfigManager.create_default_config(self.config_path)
        self.assertTrue(os.path.exists(self.config_path))
        
        config = ConfigManager.load_config(self.config_path)
        self.assertIn("profiles", config)
        self.assertIn("default", config["profiles"])


class TestLogger(unittest.TestCase):
    """测试日志记录器"""
    
    def test_log_levels(self):
        """测试日志级别"""
        logger = Logger(level=LogLevel.INFO, quiet=True)
        
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        
        # 验证日志被记录
        self.assertEqual(len(logger.logs), 3)  # debug被过滤
        self.assertEqual(logger.logs[0]["level"], "info")
    
    def test_export_json(self):
        """测试导出JSON"""
        logger = Logger(quiet=True)
        logger.info("test message")
        
        temp_file = tempfile.mktemp(suffix=".json")
        logger.export_json(temp_file)
        
        self.assertTrue(os.path.exists(temp_file))
        
        import json
        with open(temp_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        
        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main(verbosity=2)
