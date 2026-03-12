import base64
import json
import threading
import time
import traceback

# 先设置 sys.path，确保可以导入 backend.*
# 使用 Path(__file__).resolve() 确保始终得到绝对路径，兼容所有导入方式
import _setup_backend
import backend._setup_django

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
                'got new message: topic=%s, payload_len=%s',
                msg.topic,
                len(msg.payload) if msg.payload is not None else None
            )
            msg_data = _parse_incoming_mqtt_payload_to_dict(msg.payload)
            topic = str(msg.topic).replace('topic_transfer/', '', 1)
            obj_manager = TopicTransferManager(topic, msg_data)
            p = threading.Thread(target=obj_manager.parse_msg)
            p.start()
        except Exception:
            logger.error(traceback.format_exc())


def _parse_incoming_mqtt_payload_to_dict(raw_payload):
    """
    将 mqtt 的 msg.payload 转成标准 dict。

    兼容两类输入：
    - 标准 JSON（utf-8 编码，payload 字段也是标准 JSON 值：str/dict/list/...）
    - 非标准“JSON 头 + 二进制 payload”（你日志里那种：... "payload": \\xee\\xee... }）
      这种情况下会把 payload 的二进制段原样提取成 bytes，并额外附上 payload_b64 方便日志/排查。
    """
    if raw_payload is None:
        raise ValueError('mqtt payload is None')

    # paho mqtt 通常给 bytes；这里也兼容 str
    if isinstance(raw_payload, str):
        raw_payload = raw_payload.encode('utf-8', errors='surrogatepass')
    if not isinstance(raw_payload, (bytes, bytearray)):
        raise TypeError(f'unsupported payload type: {type(raw_payload)}')

    raw_payload = bytes(raw_payload)

    # 1) 标准 JSON：直接解析即可
    try:
        return json.loads(raw_payload)
    except UnicodeDecodeError:
        # 2) 兼容 payload 内混入二进制导致 utf-8 decode 失败
        pass

    key = b'"payload"'
    idx = raw_payload.find(key)
    if idx < 0:
        raise ValueError('payload is not valid utf-8 json, and no "payload" key found')

    colon = raw_payload.find(b':', idx + len(key))
    if colon < 0:
        raise ValueError('invalid message: no ":" after "payload" key')

    start = colon + 1
    while start < len(raw_payload) and raw_payload[start] in b' \t\r\n':
        start += 1

    end = raw_payload.rfind(b'}')
    if end < 0 or end <= start:
        raise ValueError('invalid message: cannot find ending "}" for message')

    # 假设 payload 是最后一个字段：把二进制段替换成 null，让 JSON 头部可被解析
    sanitized = raw_payload[:start] + b'null' + raw_payload[end:]
    head_obj = json.loads(sanitized.decode('utf-8'))

    bin_payload = raw_payload[start:end].rstrip(b' \t\r\n')
    head_obj['payload'] = bin_payload
    head_obj['payload_b64'] = base64.b64encode(bin_payload).decode('ascii')
    return head_obj


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
