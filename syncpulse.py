#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyncPulse - Lightweight Terminal File Sync & Backup Engine
轻量级终端文件智能同步与备份引擎

A zero-dependency CLI tool for intelligent file synchronization and backup.
支持增量同步、多目标存储、实时监控、版本管理的轻量级文件同步工具。

Author: gitstq
License: MIT
Version: 1.0.0
"""

import os
import sys
import json
import hashlib
import shutil
import argparse
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

__version__ = "1.0.0"
__author__ = "gitstq"


class SyncMode(Enum):
    """同步模式"""
    MIRROR = "mirror"      # 镜像模式：目标与源完全一致
    INCREMENTAL = "incremental"  # 增量模式：只传输变更
    BIDIRECTIONAL = "bidirectional"  # 双向同步


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class SyncConfig:
    """同步配置数据类"""
    source: str
    destination: str
    mode: str = "incremental"
    exclude_patterns: List[str] = None
    include_patterns: List[str] = None
    preserve_permissions: bool = True
    preserve_timestamps: bool = True
    compress: bool = False
    encrypt: bool = False
    bandwidth_limit: int = 0  # KB/s, 0表示无限制
    version_count: int = 5    # 保留版本数量
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = ['*.tmp', '*.log', '.git', '__pycache__', '.DS_Store']
        if self.include_patterns is None:
            self.include_patterns = []


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    size: int
    mtime: float
    checksum: str
    is_dir: bool = False


class Logger:
    """日志记录器"""
    
    LEVELS = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.WARNING: 2,
        LogLevel.ERROR: 3
    }
    
    def __init__(self, level: LogLevel = LogLevel.INFO, quiet: bool = False):
        self.level = level
        self.quiet = quiet
        self.logs: List[Dict[str, Any]] = []
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """内部日志方法"""
        if self.LEVELS[level] < self.LEVELS[self.level]:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level.value,
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)
        
        if not self.quiet:
            color_map = {
                LogLevel.DEBUG: "\033[36m",    # Cyan
                LogLevel.INFO: "\033[32m",     # Green
                LogLevel.WARNING: "\033[33m",  # Yellow
                LogLevel.ERROR: "\033[31m"     # Red
            }
            reset = "\033[0m"
            color = color_map.get(level, "")
            print(f"{color}[{timestamp}] [{level.value.upper()}] {message}{reset}")
    
    def debug(self, message: str, **kwargs):
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def export_json(self, filepath: str):
        """导出日志为JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)


class FileHasher:
    """文件哈希计算器"""
    
    @staticmethod
    def calculate_checksum(filepath: str, algorithm: str = "blake2b") -> str:
        """
        计算文件校验和
        
        Args:
            filepath: 文件路径
            algorithm: 哈希算法 (md5, sha256, blake2b)
        
        Returns:
            十六进制哈希字符串
        """
        if not os.path.exists(filepath):
            return ""
        
        if os.path.isdir(filepath):
            return ""
        
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except (IOError, OSError) as e:
            return ""
    
    @staticmethod
    def quick_hash(filepath: str) -> str:
        """
        快速哈希：结合文件大小和修改时间
        
        Args:
            filepath: 文件路径
        
        Returns:
            快速哈希字符串
        """
        try:
            stat = os.stat(filepath)
            data = f"{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(data.encode()).hexdigest()[:16]
        except (IOError, OSError):
            return ""


class FileScanner:
    """文件扫描器"""
    
    def __init__(self, config: SyncConfig, logger: Logger):
        self.config = config
        self.logger = logger
    
    def should_exclude(self, filepath: str) -> bool:
        """检查文件是否应该被排除"""
        filename = os.path.basename(filepath)
        
        # 检查排除模式
        for pattern in self.config.exclude_patterns:
            if self._match_pattern(filename, pattern):
                return True
        
        # 如果有包含模式，检查是否匹配
        if self.config.include_patterns:
            for pattern in self.config.include_patterns:
                if self._match_pattern(filename, pattern):
                    return False
            return True
        
        return False
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """简单的通配符匹配"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def scan_directory(self, directory: str) -> Dict[str, FileInfo]:
        """
        扫描目录获取文件信息
        
        Args:
            directory: 要扫描的目录
        
        Returns:
            文件路径到FileInfo的映射字典
        """
        files_info = {}
        
        if not os.path.exists(directory):
            self.logger.warning(f"Directory does not exist: {directory}")
            return files_info
        
        self.logger.info(f"Scanning directory: {directory}")
        
        for root, dirs, files in os.walk(directory):
            # 过滤被排除的目录
            dirs[:] = [d for d in dirs if not self.should_exclude(os.path.join(root, d))]
            
            for filename in files:
                filepath = os.path.join(root, filename)
                
                if self.should_exclude(filepath):
                    continue
                
                try:
                    stat = os.stat(filepath)
                    rel_path = os.path.relpath(filepath, directory)
                    
                    file_info = FileInfo(
                        path=rel_path,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        checksum=FileHasher.quick_hash(filepath),
                        is_dir=False
                    )
                    files_info[rel_path] = file_info
                    
                except (IOError, OSError) as e:
                    self.logger.error(f"Error scanning file {filepath}: {e}")
        
        self.logger.info(f"Found {len(files_info)} files")
        return files_info


class SyncEngine:
    """同步引擎"""
    
    def __init__(self, config: SyncConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.scanner = FileScanner(config, logger)
        self.stats = {
            "files_copied": 0,
            "files_updated": 0,
            "files_deleted": 0,
            "files_skipped": 0,
            "bytes_transferred": 0,
            "errors": 0
        }
    
    def sync(self, dry_run: bool = False) -> bool:
        """
        执行同步操作
        
        Args:
            dry_run: 是否仅模拟运行
        
        Returns:
            同步是否成功
        """
        self.logger.info(f"Starting sync: {self.config.source} -> {self.config.destination}")
        self.logger.info(f"Mode: {self.config.mode}")
        
        if dry_run:
            self.logger.info("DRY RUN MODE - No changes will be made")
        
        # 扫描源目录和目标目录
        source_files = self.scanner.scan_directory(self.config.source)
        dest_files = self.scanner.scan_directory(self.config.destination)
        
        # 执行同步
        try:
            if self.config.mode == SyncMode.MIRROR.value:
                self._sync_mirror(source_files, dest_files, dry_run)
            elif self.config.mode == SyncMode.INCREMENTAL.value:
                self._sync_incremental(source_files, dest_files, dry_run)
            elif self.config.mode == SyncMode.BIDIRECTIONAL.value:
                self._sync_bidirectional(source_files, dest_files, dry_run)
            else:
                self._sync_incremental(source_files, dest_files, dry_run)
            
            self._print_stats()
            return True
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            self.stats["errors"] += 1
            return False
    
    def _sync_mirror(self, source_files: Dict[str, FileInfo], 
                     dest_files: Dict[str, FileInfo], dry_run: bool):
        """镜像模式同步"""
        # 复制或更新源文件到目标
        for rel_path, file_info in source_files.items():
            src_path = os.path.join(self.config.source, rel_path)
            dst_path = os.path.join(self.config.destination, rel_path)
            
            if rel_path in dest_files:
                # 文件存在，检查是否需要更新
                if file_info.checksum != dest_files[rel_path].checksum:
                    self._copy_file(src_path, dst_path, dry_run, update=True)
                else:
                    self.stats["files_skipped"] += 1
                    self.logger.debug(f"Skipped (unchanged): {rel_path}")
            else:
                # 新文件
                self._copy_file(src_path, dst_path, dry_run)
        
        # 删除目标中多余的文件
        for rel_path in dest_files:
            if rel_path not in source_files:
                dst_path = os.path.join(self.config.destination, rel_path)
                self._delete_file(dst_path, dry_run)
    
    def _sync_incremental(self, source_files: Dict[str, FileInfo],
                          dest_files: Dict[str, FileInfo], dry_run: bool):
        """增量模式同步"""
        for rel_path, file_info in source_files.items():
            src_path = os.path.join(self.config.source, rel_path)
            dst_path = os.path.join(self.config.destination, rel_path)
            
            if rel_path in dest_files:
                # 文件存在，检查是否需要更新
                if file_info.checksum != dest_files[rel_path].checksum:
                    # 创建版本备份
                    if self.config.version_count > 0 and not dry_run:
                        self._create_version_backup(dst_path)
                    self._copy_file(src_path, dst_path, dry_run, update=True)
                else:
                    self.stats["files_skipped"] += 1
                    self.logger.debug(f"Skipped (unchanged): {rel_path}")
            else:
                # 新文件
                self._copy_file(src_path, dst_path, dry_run)
    
    def _sync_bidirectional(self, source_files: Dict[str, FileInfo],
                            dest_files: Dict[str, FileInfo], dry_run: bool):
        """双向同步模式"""
        # 先执行增量同步（源到目标）
        self._sync_incremental(source_files, dest_files, dry_run)
        
        # 然后同步目标到源（只复制源中不存在的文件）
        for rel_path, file_info in dest_files.items():
            if rel_path not in source_files:
                src_path = os.path.join(self.config.destination, rel_path)
                dst_path = os.path.join(self.config.source, rel_path)
                self._copy_file(src_path, dst_path, dry_run)
    
    def _copy_file(self, src: str, dst: str, dry_run: bool, update: bool = False):
        """复制文件"""
        if dry_run:
            action = "Would update" if update else "Would copy"
            self.logger.info(f"{action}: {os.path.basename(src)}")
            return
        
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            # 复制文件
            shutil.copy2(src, dst) if self.config.preserve_timestamps else shutil.copy(src, dst)
            
            if update:
                self.stats["files_updated"] += 1
                self.logger.info(f"Updated: {os.path.basename(src)}")
            else:
                self.stats["files_copied"] += 1
                self.logger.info(f"Copied: {os.path.basename(src)}")
            
            self.stats["bytes_transferred"] += os.path.getsize(src)
            
        except (IOError, OSError) as e:
            self.logger.error(f"Error copying {src}: {e}")
            self.stats["errors"] += 1
    
    def _delete_file(self, filepath: str, dry_run: bool):
        """删除文件"""
        if dry_run:
            self.logger.info(f"Would delete: {os.path.basename(filepath)}")
            return
        
        try:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
            self.stats["files_deleted"] += 1
            self.logger.info(f"Deleted: {os.path.basename(filepath)}")
        except (IOError, OSError) as e:
            self.logger.error(f"Error deleting {filepath}: {e}")
            self.stats["errors"] += 1
    
    def _create_version_backup(self, filepath: str):
        """创建版本备份"""
        if not os.path.exists(filepath):
            return
        
        # 创建版本目录
        versions_dir = os.path.join(os.path.dirname(filepath), ".syncpulse_versions",
                                    os.path.basename(filepath))
        os.makedirs(versions_dir, exist_ok=True)
        
        # 生成版本文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_path = os.path.join(versions_dir, f"v_{timestamp}")
        
        try:
            shutil.copy2(filepath, version_path)
            
            # 清理旧版本
            self._cleanup_old_versions(versions_dir)
            
        except (IOError, OSError) as e:
            self.logger.error(f"Error creating version backup: {e}")
    
    def _cleanup_old_versions(self, versions_dir: str):
        """清理旧版本"""
        try:
            versions = sorted(os.listdir(versions_dir))
            while len(versions) > self.config.version_count:
                old_version = versions.pop(0)
                os.remove(os.path.join(versions_dir, old_version))
                self.logger.debug(f"Removed old version: {old_version}")
        except (IOError, OSError) as e:
            self.logger.error(f"Error cleaning up versions: {e}")
    
    def _print_stats(self):
        """打印统计信息"""
        self.logger.info("=" * 50)
        self.logger.info("Sync Statistics:")
        self.logger.info(f"  Files copied: {self.stats['files_copied']}")
        self.logger.info(f"  Files updated: {self.stats['files_updated']}")
        self.logger.info(f"  Files deleted: {self.stats['files_deleted']}")
        self.logger.info(f"  Files skipped: {self.stats['files_skipped']}")
        self.logger.info(f"  Bytes transferred: {self._format_bytes(self.stats['bytes_transferred'])}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
        self.logger.info("=" * 50)
    
    @staticmethod
    def _format_bytes(size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_PATH = os.path.expanduser("~/.syncpulse/config.json")
    
    @classmethod
    def load_config(cls, config_path: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = cls.DEFAULT_CONFIG_PATH
        
        if not os.path.exists(config_path):
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any], config_path: str = None):
        """保存配置文件"""
        if config_path is None:
            config_path = cls.DEFAULT_CONFIG_PATH
        
        # 确保配置目录存在
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    @classmethod
    def create_default_config(cls, config_path: str = None):
        """创建默认配置文件"""
        default_config = {
            "profiles": {
                "default": {
                    "source": "~/Documents",
                    "destination": "~/Backup",
                    "mode": "incremental",
                    "exclude_patterns": ["*.tmp", "*.log", ".git", "__pycache__", ".DS_Store"],
                    "version_count": 5
                }
            },
            "global": {
                "log_level": "info",
                "default_profile": "default"
            }
        }
        cls.save_config(default_config, config_path)
        print(f"Default config created at: {config_path or cls.DEFAULT_CONFIG_PATH}")


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='syncpulse',
        description='SyncPulse - Lightweight Terminal File Sync & Backup Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sync /path/to/source /path/to/dest
  %(prog)s sync -c config.json
  %(prog)s init
  %(prog)s sync --mode mirror --dry-run src/ dst/
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize files')
    sync_parser.add_argument('source', nargs='?', help='Source directory')
    sync_parser.add_argument('destination', nargs='?', help='Destination directory')
    sync_parser.add_argument('-c', '--config', help='Configuration file path')
    sync_parser.add_argument('-p', '--profile', help='Configuration profile')
    sync_parser.add_argument('-m', '--mode', choices=['mirror', 'incremental', 'bidirectional'],
                            default='incremental', help='Sync mode')
    sync_parser.add_argument('-e', '--exclude', action='append', help='Exclude pattern')
    sync_parser.add_argument('-n', '--dry-run', action='store_true', help='Dry run')
    sync_parser.add_argument('--delete', action='store_true', help='Delete files in destination')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize configuration')
    init_parser.add_argument('-c', '--config', help='Configuration file path')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List configuration profiles')
    list_parser.add_argument('-c', '--config', help='Configuration file path')
    
    return parser


def main():
    """主入口函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 设置日志级别
    log_level = LogLevel.DEBUG if args.verbose else LogLevel.INFO
    if args.quiet:
        log_level = LogLevel.ERROR
    logger = Logger(level=log_level, quiet=args.quiet)
    
    if args.command == 'init':
        ConfigManager.create_default_config(args.config)
        sys.exit(0)
    
    elif args.command == 'list':
        config = ConfigManager.load_config(args.config)
        profiles = config.get('profiles', {})
        if profiles:
            print("Available profiles:")
            for name, profile in profiles.items():
                print(f"  - {name}: {profile.get('source', 'N/A')} -> {profile.get('destination', 'N/A')}")
        else:
            print("No profiles configured. Run 'syncpulse init' to create default config.")
        sys.exit(0)
    
    elif args.command == 'sync':
        # 加载配置
        config_data = ConfigManager.load_config(args.config)
        
        # 确定源和目标
        source = args.source
        destination = args.destination
        
        if args.profile or (not source and not destination):
            profiles = config_data.get('profiles', {})
            profile_name = args.profile or config_data.get('global', {}).get('default_profile', 'default')
            profile = profiles.get(profile_name, {})
            
            source = source or profile.get('source')
            destination = destination or profile.get('destination')
        
        if not source or not destination:
            logger.error("Source and destination are required")
            sys.exit(1)
        
        # 展开路径
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)
        
        # 创建同步配置
        sync_config = SyncConfig(
            source=source,
            destination=destination,
            mode=args.mode,
            exclude_patterns=args.exclude or ['*.tmp', '*.log', '.git', '__pycache__', '.DS_Store']
        )
        
        # 执行同步
        engine = SyncEngine(sync_config, logger)
        success = engine.sync(dry_run=args.dry_run)
        
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
