import os
import sys
import time
import traceback
from pathlib import Path

# 先设置 sys.path，确保可以导入 backend.*
# 使用 Path(__file__).resolve() 确保始终得到绝对路径，兼容所有导入方式
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJ_ROOT = BASE_DIR.parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

import backend.task_engine._setup_django
# 切记：main中关于django models的引包需要放到该注释的下面
import backend.m_common.set_timezone

from django.conf import settings
from django_celery_beat.models import PeriodicTask
from multiprocessing import Process
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.redi_db_const import TASK_DB
from backend.task_engine.config import task_engine_logger as logger
from backend.task_engine.data_manage import TaskDataManage
from backend.task_engine.exec_manage import TaskExecManage
from backend.task_engine.task_engine_config import BROKER_URL, USERNAME, \
    PASSWORD, MQTT_PORT, TASK_CREATE, TASK_UPDATE, TASK_DEL, MQTT_TLS
from backend.apps.tasks.models import Tasks
from backend.apps.tasks.serializers import TaskSerializer, TaskManagerSerializer
from backend.apps.celery_tasks.custom_tasks.tasks import parse_task_data


class TasksReceiverServer(MQTTClient):
    """
    接收 mqtt 相关数据 处理对应Task 业务
    """
    def on_connect(self, client, user_data, flags, rc):
        client.subscribe([
            (TASK_CREATE.format(task_id='+'), 0),  # 任务创建
            (TASK_UPDATE.format(task_id='+'), 0),  # 任务修改
            (TASK_DEL.format(task_id='+'), 0),  # 任务删除
        ])

    def on_message(self, client, user_data, msg):

        # 每次有消息进来时，先判断下有没有失效的数据库连接，如果有，则关闭
        try:
            payload = msg.payload
            if isinstance(payload, bytes):
                payload = bytes.decode(payload)
            # 调试
            logger.info(msg.topic)
            logger.info(payload)
            # TaskManager(msg.topic, payload).parse_msg()
            parse_task_data.delay(msg.topic, payload)  # 调起celery任务
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())


class TaskEngineServe(object):
    """
    任务 server
    """
    @staticmethod
    def close_all_tinging_task():
        """
        关闭所有 任务
        :return:
        """
        PeriodicTask.objects.filter(
            task='task_timing_task',
        ).update(
            enabled=False
        )

    @staticmethod
    def clear_task_redis():
        """
        清空redis 缓存
        :return:
        """
        redis_conn = TaskDataManage.get_redis_conn(TASK_DB)
        redis_conn.flushdb()
        # 通配符查找
        # keys = redis_conn.keys(pattern='task_*')
        # redis_conn.delete(*keys)

    def del_task_data(self):
        """
        重新启动时删除缓存的场景数据
        :return:
        """
        self.clear_task_redis()
        self.close_all_tinging_task()

    @staticmethod
    def start_receiver_server():
        """
        启动 mqtt server
        :return:
        """
        client = TasksReceiverServer(
            client_id=f'su_task_{int(time.time()*1000)}',
            broker_url=BROKER_URL,
            port=MQTT_PORT,
            username=USERNAME,
            password=PASSWORD,
            tls=MQTT_TLS,
            logger=logger
        )
        logger.info('client.loop_forever()')
        client.loop_forever()

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
        ret = TaskManagerSerializer(scene_qs, many=True).data
        for scene_data in ret:
            TaskDataManage.redis_save_task(scene_data)
            TaskDataManage.start_task(scene_data)
        logger.info("TaskEngine服务 初始完成！")

    def run(self):
        # 1，删除 原redis 缓存 关闭所有celery_beat定时任务
        self.del_task_data()
        # 3 读取 mysql 中 所有任务数据 缓存到数据库中
        receiver_server = Process(target=self.init_task_data, args=(20, ))
        receiver_server.start()
        # 2启动 mqtt server
        self.start_receiver_server()


def main():
    try:
        TaskEngineServe().run()
    except Exception as e:
        error_msg = 'TaskEngine服务启动失败：{}'.format(traceback.format_exc())
        logger.error(error_msg)
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()