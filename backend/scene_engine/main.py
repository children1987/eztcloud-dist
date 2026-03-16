import sys
import time
import json
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

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
from multiprocessing import Process
from django.conf import settings
from django_celery_beat.models import PeriodicTask
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.redi_db_const import SCENE_DB
from backend.m_common.debugger import rerun
from backend.scene_engine.scene_config import BROKER_URL, USERNAME, \
    PASSWORD, MQTT_PORT, INTERNAL_DATA, MQTT_TLS, ON_LINE, OFF_LINE, \
    MQTT_RECONNECT_MIN_DELAY, MQTT_RECONNECT_MAX_DELAY
from backend.scene_engine.scene_manage import SceneManager
from backend.apps.scenes.models import SceneConfig
from backend.apps.scenes.serializers import SceneDataSerializer, SceneTimingSerializer
# from celery_tasks.scene_ctrl.tasks import parse_scene_task
logger = settings.SCENE_ENGINE_LOGGER

# 线程池用于处理场景消息，避免为每条消息创建一个新线程导致内存溢出
SCENE_ENGINE_MAX_WORKERS = 10
SCENE_PARSE_EXECUTOR = ThreadPoolExecutor(max_workers=SCENE_ENGINE_MAX_WORKERS)


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
            # 使用线程池执行解析逻辑，避免无限制创建线程
            SCENE_PARSE_EXECUTOR.submit(scene_manager.parse_msg)
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
        client = SceneReceiverServer(
            client_id=f'su_scene_{int(time.time()*1000)}',
            broker_url=BROKER_URL,
            port=MQTT_PORT,
            username=USERNAME,
            password=PASSWORD,
            tls=MQTT_TLS,
            logger=logger,
            # 当 broker 首次不可用或运行中断线时，按配置的间隔自动重连
            reconnect_min_delay=MQTT_RECONNECT_MIN_DELAY,
            reconnect_max_delay=MQTT_RECONNECT_MAX_DELAY,
            retry_first_connection=True,
        )
        logger.info(
            'client.loop_forever() with auto reconnect: '
            'min_delay=%s, max_delay=%s',
            MQTT_RECONNECT_MIN_DELAY,
            MQTT_RECONNECT_MAX_DELAY,
        )
        client.loop_forever()

    @staticmethod
    def get_redis_conn(redis_db):
        """
        实现一个连接池
        :param redis_db:
        :return:
        """
        return SceneManager.get_redis_conn(redis_db)


    @staticmethod
    def init_scene_data():
        """
        读取mysql初始化场景数据
        :return:
        """
        scene_qs = SceneConfig.objects.filter(
            is_active=True,
            is_deleted=False,
            project__isnull=False,
        )
        redis_conn = SceneManager.get_redis_conn(SCENE_DB)
        for scene_obj in scene_qs:
            scene_id = scene_obj.pk
            key = f'scene_{scene_id}'
            if redis_conn.exists(key):
                continue
            scene_data = SceneTimingSerializer(scene_obj).data
            SceneManager.set_scene_redis(scene_data)


    @rerun(default_rerun_message='SceneEngine服务重启中', timeout=5, logger=logger)
    def run(self, *args, **kwargs):
        # 启动 mqtt server
        self.start_receiver_server()


def main():
    # 1 读取 mysql 中 所有场景数据 缓存到数据库中
    scene_manage = SceneEngineServe()
    receiver_server = Process(target=scene_manage.init_scene_data)
    receiver_server.start()
    scene_manage.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error('SceneEngine服务启动失败！')
        logger.error(traceback.format_exc())
