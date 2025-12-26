import os
import sys
import threading
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

import backend.scene_engine._setup_django
# 切记：main中关于django models的引包需要放到该注释的下面
import backend.m_common.set_timezone

from django.conf import settings
from django_celery_beat.models import PeriodicTask
from multiprocessing import Process
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.redi_db_const import SCENE_DB
from backend.scene_engine.scene_config import BROKER_URL, USERNAME, \
    PASSWORD, MQTT_PORT, INTERNAL_DATA, MQTT_TLS, ON_LINE, OFF_LINE
from backend.scene_engine.scene_manage import SceneManager
from backend.apps.scenes.models import SceneConfig
from backend.apps.scenes.serializers import SceneDataSerializer, SceneTimingSerializer
# from celery_tasks.scene_ctrl.tasks import parse_scene_task
logger = settings.SCENE_ENGINE_LOGGER


class SceneReceiverServer(MQTTClient):
    """
    接收 mqtt 相关数据 处理对应Scene 业务
    """
    def on_connect(self, client, user_data, flags, rc):
        client.subscribe([
            (f'{INTERNAL_DATA}/+/+', 0),  # 属性上报触发
            (f'{ON_LINE}/+', 0),  # 设备上线
            (f'{OFF_LINE}/+', 0),  # 设别离线
        ])

    def on_message(self, client, user_data, msg):
        # 每次有消息进来时，先判断下有没有失效的数据库连接，如果有，则关闭
        try:
            payload = msg.payload
            if isinstance(payload, bytes):
                payload = bytes.decode(payload)
            # 调试 不起用celery 可打开下方注释
            # SceneManager(msg.topic, payload).parse_msg()
            # logger.info(msg.topic)
            # logger.info(payload)
            logger.debug(
                'topic <<{}>> msg <<{}>> '.format(msg.topic, payload)
            )
            scene_manager = SceneManager(msg.topic, payload)
            p = threading.Thread(target=scene_manager.parse_msg)
            p.start()
            # parse_scene_task.delay(msg.topic, payload)  # 调起celery任务
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())


class SceneEngineServe(object):
    """
    场景 server
    """
    @staticmethod
    def close_all_tinging_task():
        """
        关闭所有scene 定时任务
        :return:
        """
        PeriodicTask.objects.filter(
            task='scene_timing_task',
        ).delete()

    @staticmethod
    def clear_scene_redis():
        """
        清空redis 缓存
        :return:
        """
        redis_conn = SceneManager.get_redis_conn(SCENE_DB)
        redis_conn.flushdb()
        # 通配符查找
        # keys = redis_conn.keys(pattern='scene_*')
        # redis_conn.delete(*keys)

    def del_scene_data(self):
        """
        重新启动时删除缓存的场景数据
        todo 关闭原有定时任务 是否需要
        :return:
        """
        self.clear_scene_redis()
        self.close_all_tinging_task()

    @staticmethod
    def start_receiver_server():
        """
        启动 mqtt server
        :return:
        """
        try:
            client = SceneReceiverServer(
                client_id=f'su_scene_{int(time.time()*1000)}',
                broker_url=BROKER_URL,
                port=MQTT_PORT,
                username=USERNAME,
                password=PASSWORD,
                tls=MQTT_TLS,
                logger=logger
            )
            logger.info('client.loop_forever()')
            client.loop_forever()
        except Exception as _:
            error_msg = 'SceneReceiverServer服务启动失败：{}'.format(traceback.format_exc())
            logger.error(error_msg)

    @staticmethod
    def get_redis_conn(redis_db):
        """
        实现一个连接池
        :param db:
        :return:
        """
        return SceneManager.get_redis_conn(redis_db)

    @staticmethod
    def set_redis_data():
        """
        设置 redis 缓存数据
        :return:
        """
        scene_qs = SceneConfig.objects.filter(
            is_active=True,
            is_deleted=False
        ).all()
        ret = SceneDataSerializer(scene_qs, many=True).data
        for scene_data in ret:
            SceneManager.set_scene_redis(scene_data)

    @staticmethod
    def start_timing_task():
        """
        开启 定时任务
        :return:
        """
        scene_qs = SceneConfig.objects.filter(
            trigger_type__contains='timing',
            is_active=True,
            is_deleted=False
        ).all()
        ret = SceneTimingSerializer(scene_qs, many=True).data
        for scene_data in ret:
            SceneManager.on_timing_scene(scene_data)

    def read_scene_data(self):
        """
         读取 mysql 中开启的场景数据 并且初始化
        :return:
        """
        self.set_redis_data()
        # self.start_timing_task()

    def run(self):
        # 启动 mqtt server
        self.start_receiver_server()


def main():
    error_numb = 0
    while True:
        try:
            SceneEngineServe().run()
        except Exception as e:
            error_msg = 'SceneEngine服务启动失败：{}'.format(traceback.format_exc())
            logger.error(error_msg)
            if error_numb <= 3:
                error_numb += 1
            time.sleep(error_numb * 20)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error('SceneEngine服务启动失败！')
        logger.error(traceback.format_exc())
