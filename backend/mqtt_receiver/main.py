import json
import pickle
import time
import traceback

import _setup_backend
import backend.m_common.set_timezone
from backend.device_shadow.device_shadow import DeviceShadow
from backend.mqtt_receiver.config import MQTT_CLIENT_ID, MQTT_HOST, MQTT_PORT, \
    MQTT_USERNAME, MQTT_PASSWORD, MQTT_TLS, mqtt_receiver_logger
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.mq_factory import MqFactory
from backend.m_common.time_util import get_utc_timestamp
from backend.m_common.debugger import rerun, catch_exception
from backend.m_common.custom_logger import WATCH_LOG_LEVEL
from backend.mqtt_receiver.open_msg_manage import OpenTransferManager

logger = mqtt_receiver_logger
client_id = MQTT_CLIENT_ID + str(int(time.time()))
broker_url = MQTT_HOST
port = int(MQTT_PORT)
username = MQTT_USERNAME
password = MQTT_PASSWORD

# 设备topic配置
DEVICE_ATTR = 'attributes/{username}'  # 设备上报属性值
DEVICE_ATTR_GET = 'attributes_get/{username}'  # 设备获取当前属性值
DEVICE_EVENT = 'event_report/{username}'  # 设备上报事件
DEVICE_COMMAND_ACK = 'command_reply/{username}'  # 设备回复命令
DEVICE_DATA = 'data/{username}/{identifier}/#'  # 设备自定义数据上报

# 网关topic
GATEWAY_CONNECT = 'gateway_connect/{username}'  # 子设备已连接
GATEWAY_DISCONNECT = 'gateway_disconnect/{username}'  # 子设备已断开
GATEWAY_ATTR = 'gateway_attributes/{username}'  # 上报子设备属性
GATEWAY_ATTR_GET = 'gateway_attributes_get/{username}'  # 获取子设备属性
GATEWAY_EVENT = 'gateway_event_report/{username}'  # 上报子设备事件
GATEWAY_COMMAND_ACK = 'gateway_command_reply/{username}'  # 上报子设备命令回复


# 子设备通过联网设备与云端通讯
SUB_CONNECT = 'sub_connect/{username}'  # 上报子设备上线通知
SUB_DISCONNECT = 'sub_disconnect/{username}'  # 上报子设备下线通知
SUB_ATTR = 'sub_attributes/{username}'  # 上报子设备属性
SUB_ATTR_GET = 'sub_attributes_get/{username}'  # 获取子设备云端属性
SUB_EVENT = 'sub_event_report/{username}'  # 上报子设备事件
SUB_COMMAND_ACK = 'sub_command_reply/{username}'  # 云端下发命令至子设备

# 的open mqtt下发
OPEN_ATTR_PUSH = 'open/{projectKey}/{deviceUsername}/attributes_push'  # 属性下发
OPEN_COMMAND_SEND = 'open/{projectKey}/{deviceUsername}/command_send'  # 命令下发


TOPIC_PARSER_FUNC = {
    'data': lambda x: {
       'identifier': x[2]  # 自定义数据流标识符默认第三位
    }
}


class MQTTChannelClient(MQTTClient):
    """
    MQTTClient
    """

    def __init__(
            self,
            client_id,
            broker_url,
            port,
            username,
            password,
            tls=False,
            logger=None
    ):
        super().__init__(client_id=client_id,
                         broker_url=broker_url,
                         port=port,
                         username=username,
                         password=password,
                         tls=tls,
                         logger=logger)
        self.mq_interface = MqFactory().get_mq('up')

    def on_connect(self, client, user_data, flags, rc):
        # 订阅topic
        client.subscribe(
            [
                # 设备
                (DEVICE_ATTR.format(username='+'), 0),
                (DEVICE_ATTR_GET.format(id='+', username='+'), 0),
                (DEVICE_EVENT.format(id='+', username='+'), 0),
                (DEVICE_COMMAND_ACK.format(id='+', username='+'), 0),
                (DEVICE_DATA.format(identifier='+', username='+'), 0),
                # 联网设备上报一级子设备数据
                (GATEWAY_CONNECT.format(username='+'), 0),
                (GATEWAY_DISCONNECT.format(username='+'), 0),
                (GATEWAY_ATTR.format(username='+'), 0),
                (GATEWAY_ATTR_GET.format(username='+'), 0),
                (GATEWAY_EVENT.format(username='+'), 0),
                (GATEWAY_COMMAND_ACK.format(username='+'), 0),
                # 联网设备上报多级子设备数据
                (SUB_CONNECT.format(username='+'), 0),
                (SUB_DISCONNECT.format(username='+'), 0),
                (SUB_ATTR.format(username='+'), 0),
                (SUB_ATTR_GET.format(username='+'), 0),
                (SUB_EVENT.format(username='+'), 0),
                (SUB_COMMAND_ACK.format(username='+'), 0),
                # open mqtt接口，支持属性下发、命令下发
                (OPEN_ATTR_PUSH.format(projectKey='+', deviceUsername='+'), 0),
                (OPEN_COMMAND_SEND.format(projectKey='+', deviceUsername='+'), 0),

            ]
        )

    def on_message(self, client, user_data, msg):
        """
        当消息类型不为data时， 放入上行队列中的payload字段数据格式为JSON字符串；
        反之，有可能是JSON字符串
        """
        try:
            logger.debug(
                f'got new message: topic={msg.topic}, payload={msg.payload}'
            )
            timestamp = get_utc_timestamp()
            payload = msg.payload
            assert isinstance(payload, bytes)
            topic = msg.topic
            topic_datas = topic.split('/')
            type_ = topic_datas[0]
            if type_ == 'open':
                return OpenTransferManager(msg.topic, msg.payload).parse_msg()
            # 标准topic的数据格式都为json
            # # # 自定义数据流的数据格式不确定，依赖自定义数据流配置
            # if not type_ == 'data':
            #     # todo 格式错误问题
            #     payload = json.loads(payload.decode())
            # topic 默认 device_username 位置
            device_username = topic_datas[1]
            topic_params = TOPIC_PARSER_FUNC[type_](
                topic_datas
            ) if type_ in TOPIC_PARSER_FUNC else {}
            if 'username' in topic_params:
                device_username = topic_params.pop('username')
            data = {
                'payload': payload,
                'type': type_,
                'time': timestamp,
                'username': device_username,  # 计划废弃
                'device_username': device_username,
                'communication_type': 'MQTT'
            }
            if topic_params:
                data.update(topic_params)
            # device_shadow = DeviceShadow(logger)
            # device_info = device_shadow.get_info(device_username)
            # if not device_info:
            #     return
            # project_id = device_info['category']['project']['id']
            # if project_id == 'PR_TIiidZRrk4':
            #     return
            self.mq_interface.put_msg(pickle.dumps(data))
        except Exception:
            logger.error(traceback.format_exc())


class MQTTChannel(object):
    """
    MQTT 通道
    """

    def __init__(self):
        # 实例化一个MQTTClient
        client = MQTTChannelClient(
            client_id,
            broker_url,
            port,
            username,
            password,
            tls=MQTT_TLS,
            logger=logger,
        )
        client.loop_forever()


class App(object):
    """
    """
    @classmethod
    def run(cls):
        MQTTChannel()


@rerun(logger=logger, timeout=1, default_rerun_message='MQtt receiver 正在重启')
@catch_exception(logger=logger, default_error_message='MQTTChannel 服务异常退出')
def main():
    App.run()


if __name__ == '__main__':
    main()
