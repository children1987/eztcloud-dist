import os
import sys
from pathlib import Path

# 先设置 sys.path，确保可以导入 backend.*
# 使用 Path(__file__).resolve() 确保始终得到绝对路径，兼容所有导入方式
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJ_ROOT = BASE_DIR.parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

import backend.emqx_task_engine._setup_django
import backend.m_common.set_timezone

from concurrent.futures import ThreadPoolExecutor
from backend.emqx_task_engine.config import emqx_task_logger as logger
from backend.emqx_task_engine.emqx_auth import EmqxAuthManage
from backend.m_common.debugger import rerun
from backend.m_common.mq_factory import MqFactory


@rerun(default_rerun_message='Device Monitor MQTT 监听器重启中', logger=logger)
def authorization_all_rules_task():
    """
    emqx: 客户端授权 - 内置数据库 - 权限管理 - 所有用户（topic权限配置）
    因该操作接口提交时整体为一个json, 并发时无法保证操作的原子性
    该任务使授权操作按队列依次执行 保证操作的原子性
    api接口： authorization/sources/built_in_database/rules/all
    :return:
    """
    auth_manage = EmqxAuthManage()
    task_mq = MqFactory().get_mq(
        mq_name='emqx_task',
        sub_mq_name='auth_all_rule',
        callback=auth_manage.parse_msg,
        logger=logger
    )
    task_mq.wait_run_task()




if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=1) as pool:
        pool.submit(authorization_all_rules_task)