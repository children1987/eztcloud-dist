"""
@summary: setup django 环境，便于独立脚本调用django模型等相关对象
"""
import os
import sys
from pathlib import Path

import django


# 使用 Path(__file__).resolve() 确保始终得到绝对路径，兼容所有导入方式
SCRIPT_DIR = Path(__file__).resolve().parent  # backend/tcp_server
BASE_DIR = SCRIPT_DIR.parent  # backend
PROJ_ROOT = BASE_DIR.parent  # 项目根目录
sys.path.insert(0, str(PROJ_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.base")

django.setup()
