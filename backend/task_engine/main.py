import sys
import time
import json
import traceback
from pathlib import Path

# 先设置 sys.path，确保可以导入 backend.*
# 使用 Path(__file__).resolve() 确保始终得到绝对路径，兼容所有导入方式
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJ_ROOT = BASE_DIR.parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

import backend._setup_django
# 切记：main中关于django models的引包需要放到该注释的下面
import backend.m_common.set_timezone

from django.conf import settings
from django_celery_beat.models import PeriodicTask
from multiprocessing import Process
from backend.m_common.redi_db_const import TASK_DB
from backend.task_engine.config import task_engine_logger as logger
from backend.task_engine.data_manage import TaskDataManage
from backend.apps.tasks.models import Tasks
from backend.apps.tasks.serializers import TaskManagerSerializer
from backend.m_common.mq_factory import MqFactory


class TaskEngineServe(object):
    """
    任务 server
    """
    @staticmethod
    def init_task_data(sleep_time=None):
        """
         读取 mysql 任务数据
        :return:
        """
        if sleep_time:
            time.sleep(sleep_time)
        scene_qs = Tasks.objects.filter(
            is_active=True,
            is_deleted=False
        ).all()
        redis_conn = TaskDataManage.get_redis_conn(TASK_DB)
        for task_obj in scene_qs:
            task_id = task_obj.pk
            key = f'task_{task_id}'
            if task_obj.timing_type == 'repeat':
                filter_info = {'name__contains': f'task_{task_id}_'}
            else:
                filter_info = {'name': key}
            if PeriodicTask.objects.filter(
                **filter_info
            ).exists():
                continue
            task_data = TaskManagerSerializer(task_obj).data
            redis_conn.set(f'task_{task_id}', value=json.dumps(task_data))
            TaskDataManage.start_task(task_data)
        logger.info("TaskEngine服务 初始完成！")

    @classmethod
    def run(cls):
        # 1 读取 mysql 中 所有任务数据 缓存到数据库中
        receiver_server = Process(target=cls.init_task_data, args=(5,))
        receiver_server.start()
        # 2启动 TaskDataManage()
        task_manage = TaskDataManage()
        task_mq = MqFactory().get_mq(
            'm_task_engine',
            callback=task_manage.parse_msg,
            logger=logger)
        task_mq.wait_msg_blocked(concurrency=4)

def main():
    TaskEngineServe().run()


if __name__ == '__main__':
    main()
