#!/usr/bin/env python
"""
确保 PostgreSQL hstore 扩展存在的脚本
用于解决偶发的 hstore 扩展创建冲突问题
"""
import os
import sys
from pathlib import Path

# 设置 Python 路径
_file_path = Path(__file__).resolve()
_proj_root = _file_path.parents[2]  # /workspace/isw_v2
_proj_root_str = str(_proj_root)
if _proj_root_str not in sys.path:
    sys.path.insert(0, _proj_root_str)

from environ import Env

# 读取环境变量
env = Env()
env.read_env(str(_file_path.parent / '.env'))

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("错误: 需要安装 psycopg2 库")
    sys.exit(1)


def ensure_hstore_extension():
    """确保 hstore 扩展存在"""
    db_config = {
        'host': env.str('DATABASE_HOST'),
        'port': env.str('DATABASE_PORT'),
        'database': env.str('DATABASE_NAME'),
        'user': env.str('DATABASE_USER'),
        'password': env.str('DATABASE_PASSWORD'),
    }
    
    try:
        # 连接到数据库
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查扩展是否已存在
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM pg_extension WHERE extname = 'hstore'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            # 扩展不存在，尝试创建
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore;")
                print("成功创建 hstore 扩展")
            except Exception as e:
                # 如果创建失败（可能是并发创建导致的唯一约束冲突，或其他错误）
                # 忽略错误，因为扩展可能已经被其他进程创建了
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg.lower():
                    print("hstore 扩展已被其他进程创建（并发情况）")
                else:
                    print(f"警告: 创建 hstore 扩展时出错: {e}")
                    print("将继续执行，migrate 命令可能会处理此问题")
        # 扩展已存在，无需操作
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"错误: 无法连接到数据库或检查 hstore 扩展: {e}")
        print("将继续执行，migrate 命令可能会处理此问题")
        return False


if __name__ == '__main__':
    ensure_hstore_extension()

