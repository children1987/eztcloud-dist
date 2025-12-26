import json
import os
import sys
import asyncio
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from environ import Env

# 设置 Python 路径，将项目根目录加入 sys.path
# /workspace/isw_v2/backend/log_savers/main.py
_file_path = Path(__file__).resolve()
_proj_root = _file_path.parents[2]  # /workspace/isw_v2
_proj_root_str = str(_proj_root)

# 确保项目根目录在最前面（支持 from backend.xxx 导入）
if _proj_root_str in sys.path:
    sys.path.remove(_proj_root_str)
sys.path.insert(0, _proj_root_str)

from backend.m_common.tsdb.interface import DatabaseFactory

env = Env()
# 使用 Path(__file__).resolve() 确保始终得到绝对路径，兼容所有导入方式
env.read_env(str(Path(__file__).resolve().parent.parent / '.env'))
TSDB_TYPE = env('TSDB_TYPE')

# 设置超时时间（秒），可以根据实际情况调整
TIMEOUT_SECONDS = 10

# 最大数据大小（字节），超过此大小的数据将被跳过或截断
MAX_DATA_SIZE = 10 * 1024 * 1024  # 10MB

# 限制队列大小，防止内存溢出
QUEUE_MAX_SIZE = 1000

# 任务并发数量
WORKER_SIZE = 2

# 创建线程池执行器用于运行同步的 write_data 操作
executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="tsdb_writer")

# 使用信号量限制并发处理数量，防止资源耗尽
# 允许最多4个并发写入操作
concurrent_semaphore = asyncio.Semaphore(4)


def insert_data_to_tsdb_sync(wrapper, data):
    """同步方式插入数据到 TSDB"""
    store_name = data.get('tags', {}).get('bucket')
    measurement = data.get('name')
    fields = data.get('fields', {})
    tags = data.get('tags', {})
    timestamp = data.get('timestamp')

    try:
        wrapper.write_data(
            store_name,
            measurement,
            fields,
            tags,
            timestamp
        )
        print(f"Data successfully inserted into {store_name}")
    except Exception as e:
        print(f"Error inserting data into {store_name}: {e}", file=sys.stderr)
        # 打印堆栈信息
        traceback.print_exc()
        raise


def validate_data_size(data_str):
    """验证数据大小，如果过大则返回 False"""
    data_size = len(data_str.encode('utf-8'))
    if data_size > MAX_DATA_SIZE:
        print(f"Data size {data_size} bytes exceeds maximum {MAX_DATA_SIZE} bytes, skipping", file=sys.stderr)
        return False
    return True


async def process_data(wrapper, data):
    """异步处理数据，在线程池中运行同步操作"""
    # 使用信号量限制并发数量
    async with concurrent_semaphore:
        # 在线程池中运行同步的 write_data 操作
        # 使用 asyncio.to_thread (Python 3.9+) 或 asyncio.get_event_loop().run_in_executor
        try:
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(executor, insert_data_to_tsdb_sync, wrapper, data),
                timeout=TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            # 超时后记录错误，但不阻塞后续处理
            # 线程池中的任务会继续运行，但我们不再等待它
            print(f"Timeout after {TIMEOUT_SECONDS}s while processing data, skipping and continuing", file=sys.stderr)
            # 不抛出异常，让调用者继续处理下一条数据
            return False
        except Exception as e:
            print(f"Error processing data: {e}", file=sys.stderr)
            traceback.print_exc()
            return False
    return True


async def process_queue(wrapper, queue):
    """从队列中处理数据"""
    while True:
        try:
            # 从队列获取数据，如果队列为空则等待
            line = await queue.get()

            # 如果收到 None，表示结束信号
            if line is None:
                break

            # 验证数据大小
            if not validate_data_size(line):
                queue.task_done()
                continue

            try:
                data = json.loads(line)
                # print(f"Received data: {data}")
                # 异步处理数据，不阻塞
                await process_data(wrapper, data)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Unexpected error processing line: {e}", file=sys.stderr)
                traceback.print_exc()

            queue.task_done()
        except Exception as e:
            print(f"Error in process_queue: {e}", file=sys.stderr)
            traceback.print_exc()


def stdin_reader(queue, loop):
    """在单独线程中读取 stdin 并放入队列"""
    try:
        for line in sys.stdin:
            # 移除换行符
            line = line.rstrip('\n\r')
            if not line:
                continue

            # 将数据放入队列（同步调用，因为我们在另一个线程中）
            asyncio.run_coroutine_threadsafe(queue.put(line), loop)
    except Exception as e:
        print(f"Error reading from stdin: {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        # 发送结束信号
        asyncio.run_coroutine_threadsafe(queue.put(None), loop)


async def main():
    """主异步函数"""
    wrapper = DatabaseFactory.get_client(TSDB_TYPE)

    # 创建队列用于缓冲输入数据
    queue = asyncio.Queue(maxsize=QUEUE_MAX_SIZE)  # 限制队列大小，防止内存溢出

    # 创建事件循环引用
    loop = asyncio.get_event_loop()

    # 在单独线程中启动 stdin 读取器
    reader_thread = Thread(target=stdin_reader, args=(queue, loop), daemon=True)
    reader_thread.start()

    # 启动多个处理任务以提高并发性
    workers = [
        asyncio.create_task(process_queue(wrapper, queue))
        for _ in range(WORKER_SIZE)
    ]

    try:
        # 等待所有工作线程完成
        await asyncio.gather(*workers)
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
    finally:
        # 清理资源
        executor.shutdown(wait=False)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
