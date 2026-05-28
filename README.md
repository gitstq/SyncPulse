<div align="center">

# 🚀 SyncPulse

**Lightweight Terminal File Sync & Backup Engine**

**轻量级终端文件智能同步与备份引擎**

**輕量級終端檔案智能同步與備份引擎**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Project Introduction

**SyncPulse** is a lightweight, zero-dependency terminal file synchronization and backup tool designed for developers and system administrators who value efficiency and simplicity.

**Core Value Proposition:**
- ⚡ **Zero Dependencies**: Pure Python standard library implementation, no installation hassles
- 🔄 **Intelligent Sync**: Incremental, mirror, and bidirectional sync modes
- 📦 **Version Control**: Automatic backup with configurable retention
- 🎯 **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- 🚀 **Lightning Fast**: Optimized file hashing and transfer algorithms

**Inspiration:** Born from the need for a simple yet powerful file sync tool that doesn't require complex setup or heavy dependencies.

### ✨ Core Features

| Feature | Description | Emoji |
|---------|-------------|-------|
| **🔄 Incremental Sync** | Only transfer changed files, saving time and bandwidth | ⚡ |
| **🪞 Mirror Mode** | Keep destination identical to source, delete extra files | 🎯 |
| **↔️ Bidirectional Sync** | Two-way synchronization with conflict detection | 🔄 |
| **📦 Version Control** | Automatic backup of overwritten files | 💾 |
| **🚫 Smart Exclusion** | Configurable file/directory exclusion patterns | 🛡️ |
| **📊 Progress Tracking** | Real-time sync statistics and logging | 📈 |
| **🔒 Checksum Verification** | BLAKE2b/MD5/SHA256 hash verification | 🔐 |
| **🎨 Colored Output** | Beautiful terminal output with color coding | 🌈 |

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- No additional dependencies required!

#### Installation

**Method 1: Direct Download**
```bash
# Clone the repository
git clone https://github.com/gitstq/SyncPulse.git
cd SyncPulse

# Make executable
chmod +x syncpulse.py

# Optional: Install to system
python3 setup.py install --user
```

**Method 2: pip Install**
```bash
pip install git+https://github.com/gitstq/SyncPulse.git
```

#### Basic Usage

```bash
# Initialize configuration
syncpulse init

# Simple incremental sync
syncpulse sync /path/to/source /path/to/destination

# Mirror mode (exact copy, deletes extra files)
syncpulse sync /path/to/source /path/to/destination --mode mirror

# Dry run (simulate without making changes)
syncpulse sync /path/to/source /path/to/destination --dry-run

# Verbose output
syncpulse -v sync /path/to/source /path/to/destination
```

### 📖 Detailed Usage Guide

#### Command Reference

```bash
syncpulse [options] <command> [args]

Commands:
  sync <source> <destination>    Synchronize files
  init                           Initialize configuration
  list                           List configuration profiles

Options:
  -v, --verbose                  Enable verbose output
  -q, --quiet                    Suppress output
  --version                      Show version
  -h, --help                     Show help

Sync Options:
  -c, --config <path>            Use custom config file
  -p, --profile <name>           Use configuration profile
  -m, --mode <mode>              Sync mode: mirror|incremental|bidirectional
  -e, --exclude <pattern>        Exclude pattern (can use multiple)
  -n, --dry-run                  Simulate without making changes
  --delete                       Delete files in destination
```

#### Configuration File

Create `~/.syncpulse/config.json`:

```json
{
  "profiles": {
    "documents": {
      "source": "~/Documents",
      "destination": "~/Backup/Documents",
      "mode": "incremental",
      "exclude_patterns": ["*.tmp", "*.log", ".DS_Store"],
      "version_count": 5
    },
    "projects": {
      "source": "~/Projects",
      "destination": "/mnt/backup/projects",
      "mode": "mirror",
      "exclude_patterns": ["node_modules", "__pycache__", ".git"],
      "version_count": 3
    }
  },
  "global": {
    "log_level": "info",
    "default_profile": "documents"
  }
}
```

Use profiles:
```bash
syncpulse sync -p documents
syncpulse sync -p projects
```

#### Advanced Examples

```bash
# Exclude multiple patterns
syncpulse sync ~/Projects /backup/projects \
  -e "*.log" \
  -e "node_modules" \
  -e ".git"

# Bidirectional sync with dry run
syncpulse sync ~/Workspace /mnt/shared \
  --mode bidirectional \
  --dry-run \
  -v

# Mirror mode (be careful - deletes extra files!)
syncpulse sync ~/Important /backup/important \
  --mode mirror \
  --delete
```

### 💡 Design Philosophy & Roadmap

**Design Principles:**
1. **Simplicity First**: Easy to install, easy to use
2. **Zero Dependencies**: Pure Python, no external packages
3. **Reliability**: Checksum verification and error handling
4. **Flexibility**: Multiple sync modes and configuration options

**Future Roadmap:**
- [ ] SSH/SCP remote sync support
- [ ] S3-compatible cloud storage integration
- [ ] Real-time file watching and auto-sync
- [ ] TUI (Terminal User Interface) dashboard
- [ ] Compression support (gzip, zstd)
- [ ] Encryption support (AES-256)
- [ ] Bandwidth limiting
- [ ] Parallel transfer for large files

### 📦 Build & Package

```bash
# Build source distribution
python3 setup.py sdist

# Build wheel
python3 setup.py bdist_wheel

# Build executable (requires PyInstaller)
make build-exe

# Run tests
make test

# Clean build artifacts
make clean
```

### 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Commit Message Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test additions/changes

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**SyncPulse** 是一款轻量级、零依赖的终端文件同步与备份工具，专为追求效率和简洁的开发者与系统管理员设计。

**核心价值主张：**
- ⚡ **零依赖**：纯 Python 标准库实现，无需安装繁琐依赖
- 🔄 **智能同步**：支持增量、镜像、双向三种同步模式
- 📦 **版本控制**：自动备份，可配置保留版本数量
- 🎯 **跨平台**：完美支持 Windows、macOS 和 Linux
- 🚀 **极速体验**：优化的文件哈希和传输算法

**灵感来源：** 源于对简单却强大的文件同步工具的需求，无需复杂配置或沉重依赖。

### ✨ 核心特性

| 特性 | 描述 | 图标 |
|------|------|------|
| **🔄 增量同步** | 仅传输变更文件，节省时间和带宽 | ⚡ |
| **🪞 镜像模式** | 保持目标与源完全一致，删除多余文件 | 🎯 |
| **↔️ 双向同步** | 双向同步，智能冲突检测 | 🔄 |
| **📦 版本控制** | 自动备份被覆盖的文件 | 💾 |
| **🚫 智能排除** | 可配置文件/目录排除规则 | 🛡️ |
| **📊 进度追踪** | 实时同步统计和日志 | 📈 |
| **🔒 校验和验证** | BLAKE2b/MD5/SHA256 哈希验证 | 🔐 |
| **🎨 彩色输出** | 美观的终端彩色输出 | 🌈 |

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- 无需额外依赖！

#### 安装

**方式 1：直接下载**
```bash
# 克隆仓库
git clone https://github.com/gitstq/SyncPulse.git
cd SyncPulse

# 添加执行权限
chmod +x syncpulse.py

# 可选：安装到系统
python3 setup.py install --user
```

**方式 2：pip 安装**
```bash
pip install git+https://github.com/gitstq/SyncPulse.git
```

#### 基础用法

```bash
# 初始化配置
syncpulse init

# 简单增量同步
syncpulse sync /path/to/source /path/to/destination

# 镜像模式（精确复制，删除多余文件）
syncpulse sync /path/to/source /path/to/destination --mode mirror

# 模拟运行（不实际执行）
syncpulse sync /path/to/source /path/to/destination --dry-run

# 详细输出
syncpulse -v sync /path/to/source /path/to/destination
```

### 📖 详细使用指南

#### 命令参考

```bash
syncpulse [选项] <命令> [参数]

命令：
  sync <源目录> <目标目录>    同步文件
  init                        初始化配置
  list                        列出配置方案

选项：
  -v, --verbose               启用详细输出
  -q, --quiet                 静默模式
  --version                   显示版本
  -h, --help                  显示帮助

同步选项：
  -c, --config <路径>         使用自定义配置文件
  -p, --profile <名称>        使用配置方案
  -m, --mode <模式>           同步模式：mirror|incremental|bidirectional
  -e, --exclude <模式>        排除模式（可多次使用）
  -n, --dry-run               模拟运行，不实际执行
  --delete                    删除目标目录中的多余文件
```

#### 配置文件

创建 `~/.syncpulse/config.json`：

```json
{
  "profiles": {
    "documents": {
      "source": "~/Documents",
      "destination": "~/Backup/Documents",
      "mode": "incremental",
      "exclude_patterns": ["*.tmp", "*.log", ".DS_Store"],
      "version_count": 5
    },
    "projects": {
      "source": "~/Projects",
      "destination": "/mnt/backup/projects",
      "mode": "mirror",
      "exclude_patterns": ["node_modules", "__pycache__", ".git"],
      "version_count": 3
    }
  },
  "global": {
    "log_level": "info",
    "default_profile": "documents"
  }
}
```

使用配置方案：
```bash
syncpulse sync -p documents
syncpulse sync -p projects
```

#### 高级示例

```bash
# 排除多个模式
syncpulse sync ~/Projects /backup/projects \
  -e "*.log" \
  -e "node_modules" \
  -e ".git"

# 双向同步并模拟运行
syncpulse sync ~/Workspace /mnt/shared \
  --mode bidirectional \
  --dry-run \
  -v

# 镜像模式（注意：会删除多余文件！）
syncpulse sync ~/Important /backup/important \
  --mode mirror \
  --delete
```

### 💡 设计理念与路线图

**设计原则：**
1. **简洁优先**：易于安装，易于使用
2. **零依赖**：纯 Python，无外部包
3. **可靠性**：校验和验证和错误处理
4. **灵活性**：多种同步模式和配置选项

**未来路线图：**
- [ ] SSH/SCP 远程同步支持
- [ ] S3 兼容云存储集成
- [ ] 实时文件监控和自动同步
- [ ] TUI（终端用户界面）仪表板
- [ ] 压缩支持（gzip、zstd）
- [ ] 加密支持（AES-256）
- [ ] 带宽限制
- [ ] 大文件并行传输

### 📦 构建与打包

```bash
# 构建源码分发包
python3 setup.py sdist

# 构建 wheel
python3 setup.py bdist_wheel

# 构建可执行文件（需要 PyInstaller）
make build-exe

# 运行测试
make test

# 清理构建产物
make clean
```

### 🤝 贡献指南

欢迎贡献！请遵循以下准则：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

**提交信息规范：**
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试添加/修改

### 📄 开源协议

本项目采用 MIT 协议 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹