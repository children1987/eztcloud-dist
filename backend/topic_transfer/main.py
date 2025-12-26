import os
import sys
import json
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

import backend.topic_transfer._setup_django
import backend.m_common.set_timezone
from backend.apps.equipments.biz.device_manage import set_stream_topic_transfer
from backend.topic_transfer.config import MQTT_CLIENT_ID, MQTT_HOST, MQTT_PORT, \
    MQTT_USERNAME, MQTT_PASSWORD, MQTT_TLS, topic_transfer_logger as logger
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.mq_factory import MqFactory
from backend.m_common.debugger import rerun, catch_exception
from backend.m_common.custom_logger import WATCH_LOG_LEVEL
from backend.topic_transfer.topic_transfer_manage import TopicTransferManager
from backend.apps.equipments.models import DeviceCategoryDataStream


class MQTTChannelClient(MQTTClient):
    """
    MQTTClient
    """

    def __init__(
            self,
            client_id,
            tls=False,
            logger=None
    ):
        super().__init__(client_id=client_id,
                         broker_url=MQTT_HOST,
                         port=int(MQTT_PORT),
                         username=MQTT_USERNAME,
                         password=MQTT_PASSWORD,
                         tls=tls,
                         logger=logger)
        self.mq_interface = MqFactory().get_mq('up')

    def on_connect(self, client, user_data, flags, rc):
        """
        连接成功后，订阅topic
        :param client:
        :param user_data:
        :param flags:
        :param rc:
        :return:
        """

        topic_data = [
            ('topic_transfer/#', 0),  # 通过EMQX规则转发的topic
        ]
        client.subscribe(topic_data)

    def on_message(self, client, user_data, msg):
        """
        当消息类型不为data时， 放入上行队列中的payload字段数据格式为JSON字符串；
        反之，有可能是JSON字符串
        """
        try:
            logger.debug(
                f'got new message: topic={msg.topic}, payload={msg.payload}'
            )
            msg_data = json.loads(msg.payload.decode())
            topic = str(msg.topic).replace('topic_transfer/', '', 1)
            obj_manager = TopicTransferManager(topic, msg_data)
            p = threading.Thread(target=obj_manager.parse_msg)
            p.start()
        except Exception:
            logger.error(traceback.format_exc())


class MQTTChannel(object):
    """
    MQTT 通道
    """

    def __init__(self):
        # 实例化一个MQTTClient
        client_id = MQTT_CLIENT_ID + str(int(time.time()))
        client = MQTTChannelClient(
            client_id,
            tls=MQTT_TLS,
            logger=logger,
        )
        client.loop_forever()


class TransferApp(object):
    """
    应用程序
    """

    @staticmethod
    def init_redis_data():
        """
        初始化redis 缓存数据
        :return:
        """
        data_stream_qs = DeviceCategoryDataStream.objects.filter(
            topic_mode=True,
            topic_type='mapping'
        )
        for data_stream_obj in data_stream_qs:
            set_stream_topic_transfer(data_stream_obj)
    @classmethod
    def run(cls):
        """
        初始化服务
        :return:
        """
        p = threading.Thread(target=cls.init_redis_data)
        p.start()
        MQTTChannel()


@rerun(logger=logger, timeout=1, default_rerun_message='topic_transfer 正在重启')
@catch_exception(logger=logger, default_error_message='topic_transfer 服务异常退出')
def main():
    """
    :return:
    """
    TransferApp.run()


if __name__ == '__main__':
    main()
