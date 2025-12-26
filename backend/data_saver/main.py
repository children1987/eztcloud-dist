import _setup_backend

import json
import time
import traceback
import environ

from redis import Redis
from backend.m_common.redis_pool import device_data_pool
from backend.data_saver.config import MQTT_HOST, MQTT_PORT, TELEGRAF_MQTT_RO_USER, \
    TELEGRAF_MQTT_RO_PASSWORD, \
    MQTT_TLS, data_saver_logger
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.custom_logger import WATCH_LOG_LEVEL
from backend.m_common.tsdb.interface import DatabaseFactory


class SaveDataUtils(object):
    """
    关于数据存储的工具集
    """

    @staticmethod
    def get_sprint_str(o_str: str):
        """
        获取可打印的字符串
        :param o_str: 原字符串
        :return:
        """
        return json.dumps(o_str)

    @classmethod
    def format_for_saving(cls, attrs: dict) -> list:
        """
        格式化数据，将数据转换为InfluxDB的格式
        :param attrs: 需要格式化的数据，样例：
            {"t": 36.5, "s": "a", "run": true, "j": {"a": 1, "b": 2}}
        :return: 格式化后的数据，样例： 
            [
                {"key": "f_t", "value": 36.5, "value_key":"f_value"},
                {"key": "s_s", "value": "a", "value_key":"s_value"},
                {"key": "s_run", "value": "T", "value_key":"s_value"},
                {"key": "s_a", "value": '{"a": 1, "b": 2}', "value_key":"s_value"}
            ]
        """
        rtn = []
        for k, v in attrs.items():
            if isinstance(v, bool):
                rtn.append({
                    "key": f"s_{k}",
                    "value": "T" if v else "F",
                    "value_key": "s_value"
                })
            elif isinstance(v, (int, float)):
                rtn.append({
                    "key": f"f_{k}",
                    "value": float(v),
                    "value_key": "f_value"
                })
            elif isinstance(v, str):
                rtn.append({
                    "key": f"s_{k}",
                    "value": cls.get_sprint_str(v),
                    "value_key": "s_value"
                })
            elif isinstance(v, (dict, list)):
                rtn.append({
                    "key": f"s_{k}",
                    "value": json.dumps(v),
                    "value_key": "s_value"
                })
            else:
                # 正常不应进入这里，仅用于防错、调试
                rtn.append({
                    "key": f"x_{k}",
                    "value": cls.get_sprint_str(str(v)),
                    "value_key": "s_value"
                })
        return rtn


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
        self.redis_data_conn = Redis(connection_pool=device_data_pool)

    def on_connect(self, client, user_data, flags, rc):
        # 订阅topic
        client.subscribe([
            ("internal/data/+/+", 0),  # 属性上报
            ("internal/log_attr_down/+/+", 0),  # 属性下发
        ])

    def on_message(self, client, user_data, msg):
        """
            ('U', '设备上报'),
            ('D', '云端下发'),
            ('CS', '双向传输'),
            ('CP', '云端私有'),
        :param client:
        :param user_data:
        :param msg:
        :return:
        """
        attr_type_map = {
            'U': "设备上报",
            'D': "云端下发",
            'CP': "云端私有"
        }
        try:  
            data = json.loads(msg.payload)
            self.logger.debug(f"收到数据：{data}")
            # 根据需要解析主题  
            topic_parts = msg.topic.split('/')
            topic_type = topic_parts[1]
            bucket_name = topic_parts[2]
            device_username = topic_parts[3]
            if topic_type == 'data':
                attrs = data.get("attrs")
                timestamp = data.get("time")
                attr_type = 'U'
            elif topic_type == 'log_attr_down':
                attrs = data.get("content")
                timestamp = data.get("time") or int(time.time() * 1000)
                attr_type = data.get("attr_type", 'D')
            else:
                self.logger.error(f"未知的topic_type：{topic_type}")
                return
            if not attrs:
                self.logger.error(f"msg数据error：{data}")
                return
            if attr_type not in attr_type_map:
                self.logger.error(f"未知的attr_type：{attr_type} topic_type：{topic_type}")
                return
            formated_data = SaveDataUtils.format_for_saving(attrs)
            self.logger.debug(f"格式化数据：{formated_data}")
            # 处理数据
            points = []  
            for each in formated_data:
                point = {
                    'measurement': "data",
                    'tags': {
                        "key": each['key'],
                        "device_username": device_username,
                        "attr_type": attr_type
                    },
                    'fields': {
                        each['value_key']: each['value']
                    },
                    'timestamp': timestamp
                }
                points.append(point)

            TSDB_TYPE = environ.Env().str('TSDB_TYPE')
            wrapper = DatabaseFactory.get_client(TSDB_TYPE, logger=self.logger)
            wrapper.write_multiple_data(bucket_name, points)
            self.redis_data_conn.set('last_device_save_data_time', int(time.time() * 1000))
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(str(e))


def main():
    client = MQTTChannelClient(
        TELEGRAF_MQTT_RO_USER + str(int(time.time())),
        MQTT_HOST,
        MQTT_PORT,
        TELEGRAF_MQTT_RO_USER,
        TELEGRAF_MQTT_RO_PASSWORD,
        tls=MQTT_TLS,
        logger=data_saver_logger,
    )
    client.loop_forever()

if __name__ == "__main__":
    data_saver_logger.info("data_saver 开始运行")
    main()
