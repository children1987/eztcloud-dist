#!/bin/bash
# ISW Backend 依赖安装脚本 (Linux/macOS)
# 此脚本用于在 Linux/macOS 中安装项目依赖
# 使用方法: chmod +x install_deps.sh && ./install_deps.sh

set -e

echo "开始安装 ISW Backend 项目依赖..."
echo "使用豆瓣 PyPI 镜像源加速下载..."

# Set Douban mirror for uv
export UV_INDEX_URL="https://pypi.doubanio.com/simple/"

# 检查是否已创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境（使用 Python 3.11）..."
    # Try to use Python 3.11 specifically
    if ! uv venv --python 3.11; then
        echo "使用 Python 3.11 创建虚拟环境失败，尝试使用默认 Python..."
        uv venv
        if [ $? -ne 0 ]; then
            echo "创建虚拟环境失败！请确保已安装 Python 3.11 并在 PATH 中可用。"
            exit 1
        fi
    fi
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 创建临时 requirements 文件（排除 django-celery-beat）
echo "创建临时依赖文件（排除 django-celery-beat）..."
grep -v "^django-celery-beat" requirements.txt | grep -v "^#.*django-celery-beat" > requirements-temp.txt

# 安装其他依赖
echo "安装其他依赖包..."
uv pip install -r requirements-temp.txt --index-url https://pypi.doubanio.com/simple/

# 安装 django-celery-beat（使用 --no-binary）
echo "安装 django-celery-beat（从源码安装）..."
if ! uv pip install --no-binary django-celery-beat django-celery-beat==2.5.0 --index-url https://pypi.doubanio.com/simple/; then
    echo "uv 安装失败，尝试使用 pip..."
    pip install django-celery-beat==2.5.0 -i https://pypi.doubanio.com/simple/
fi

# 清理临时文件
rm -f requirements-temp.txt

echo ""
echo "依赖安装完成！"
echo "虚拟环境已激活，您可以使用项目了。"
echo "运行示例: python manage.py migrate"


