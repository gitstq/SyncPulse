#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyncPulse Setup Script
轻量级终端文件智能同步与备份引擎 - 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='syncpulse',
    version='1.0.0',
    description='SyncPulse - Lightweight Terminal File Sync & Backup Engine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='gitstq',
    author_email='',
    url='https://github.com/gitstq/syncpulse',
    py_modules=['syncpulse'],
    entry_points={
        'console_scripts': [
            'syncpulse=syncpulse:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: Utilities',
        'Environment :: Console',
    ],
    python_requires='>=3.8',
    keywords='sync backup file-sync incremental-backup mirror-sync cli terminal',
    project_urls={
        'Bug Reports': 'https://github.com/gitstq/syncpulse/issues',
        'Source': 'https://github.com/gitstq/syncpulse',
    },
)
