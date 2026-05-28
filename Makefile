# SyncPulse Makefile
# 轻量级终端文件智能同步与备份引擎 - 构建脚本

.PHONY: help install uninstall test clean build lint format

PYTHON := python3
PIP := pip3
SCRIPT := syncpulse.py

help:
	@echo "SyncPulse - Lightweight Terminal File Sync & Backup Engine"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install SyncPulse to system"
	@echo "  uninstall    Uninstall SyncPulse from system"
	@echo "  test         Run test suite"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black"
	@echo "  run          Run syncpulse with example args"
	@echo ""

install:
	$(PYTHON) setup.py install --user
	@echo "SyncPulse installed successfully!"
	@echo "Run 'syncpulse --help' to get started"

uninstall:
	$(PIP) uninstall syncpulse -y

test:
	$(PYTHON) -m pytest tests/ -v --cov=syncpulse --cov-report=html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: clean
	$(PYTHON) setup.py sdist bdist_wheel

lint:
	flake8 syncpulse.py --max-line-length=120
	pylint syncpulse.py --disable=C0103,C0111,R0903

format:
	black syncpulse.py --line-length=120

run:
	$(PYTHON) $(SCRIPT) --help

# Development helpers
dev-install:
	$(PIP) install -e .

dev-setup:
	$(PIP) install pytest pytest-cov black flake8 pylint

# Build executables
build-exe:
	pyinstaller --onefile --name syncpulse syncpulse.py

# Cross-platform builds
build-all: build-exe
	@echo "Building for all platforms..."
	@echo "Note: Use GitHub Actions for true cross-platform builds"
