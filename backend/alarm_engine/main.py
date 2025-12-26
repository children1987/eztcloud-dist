import json
import threading
import traceback
import uuid
import _add_sys_path
import backend.m_common.set_timezone

from paho.mqtt.client import MQTTMessage

import backend.alarm_engine._setup_django

from backend.alarm_engine.assist_tool import AssistTool
from backend.alarm_engine.config import MQTT_PASSWORD, MQTT_USERNAME, MQTT_PORT, \
    MQTT_HOST, MQTT_CLIENT_ID, MQTT_TLS, alarm_logger
from backend.alarm_engine.state_getter import AlarmState
from backend.alarm_engine.state_changer import Transform
from backend.m_common.mqtt_client import MQTTClient
from backend.m_common.debugger import rerun, catch_exception
from backend.m_common.custom_logger import WATCH_LOG_LEVEL


class MQTTReceiver(MQTTClient):
    """
    本组件实时监听`输入数据`，并根据`输入告警规则`，判定告警是否产生。
    若告警产生则`输出告警记录`，`输入告警规则`配置了通知时，还需要`触发通知`。
    """

    @staticmethod
    def _process(message: MQTTMessage):
        """
        {
            "id": 7,
            "project": {
                "id": 1,
                "name": "测试项目（测试专用）"
            },
            "notice_group": {
                "id": 4,
                "project": {
                    "id": 1,
                    "name": "测试项目（测试专用）"
                },
                "creator": {
                    "id": 1,
                    "username": "admin",
                    "nickname": "梁凯ddd",
                    "last_login": "2023-06-20 17:11:38",
                    "mobile": "18821636919",
                    "email": "1@qq.com",
                    "is_bind_wx": false,
                    "wx_notice_account": "oCl_56n3NNGvSxl56nmI2K9flkyE"
                },
                "name": "頂頂機器人",
                "desc": "dds",
                "notice_types": [
                    "member",
                    "ding_robot"
                ],
                "is_active": true,
                "notice_conf": {
                    "member": [
                        {
                            "id": 1,
                            "is_sms": true,
                            "is_email": true,
                            "is_wechat": false,
                            "is_ding_work": true
                        },
                    ]
                    "ding_robot": {
                            "url": "https://www.xyz.com",
                            "secret": "wdj4ae0iowri4eoa5bvzz"
                    }
                },
                "created_time": "2023-04-14 11:11:16",
                "updated_time": "2023-04-14 14:30:50",
                "is_deleted": false
            },
            "device_origin_text": "设备类型",
            "device_origin": "C",
            "device_category": {
                "id": 22,
                "created_time": "2023-03-31 15:09:21",
                "updated_time": "2023-04-12 11:54:48",
                "project": {
                    "id": 1,
                    "name": "测试项目（测试专用）"
                },
                "quote_product_text": "产品类型",
                "quote_product": "P",
                "node_type_text": "网关",
                "node_type": "CG",
                "access_protocol_text": "EasyCloud标准网关协议",
                "access_protocol": "SGP",
                "net_type_text": "以太网",
                "net_type": "ethernet",
                "cfg_info": null,
                "other_info": null,
                "creator": {
                    "id": 1,
                    "username": "admin",
                    "nickname": "梁凯ddd",
                    "last_login": "2023-06-20 17:11:38",
                    "mobile": "18821636919",
                    "email": "1@qq.com",
                    "is_bind_wx": false,
                    "wx_notice_account": "oCl_56n3NNGvSxl56nmI2K9flkyE"
                },
                "name": "子设备类型1",
                "desc": "是多少",
                "scene_action": true,
                "scene_condition": true,
                "online_delay_time": 300,
                "alive_delay_time": 300,
                "logo": null,
                "fixed_product": null
            },
            "degree_text": "普通",
            "degree": "30",
            "creator": {
                "id": 4,
                "username": "lch_root",
                "nickname": "罗成",
                "last_login": "2023-06-06 09:47:39",
                "mobile": "11111111111",
                "email": "3@qq.com",
                "is_bind_wx": false,
                "wx_notice_account": null
            },
            "devices": [
                59,
                60,
                64,
                65,
                67
            ],
            "name": "ddd",
            "condition": {
                "conditions": [
                    {
                        "attr_id": 26,
                        "condition": "equal",
                        "judge_params": true,
                        "prop_data_type": "B"
                    }
                ],
                "logical_condition": "and"
            },
            "is_active": true,
            "remark": "ff",
            "daily_notice_times_max": 2,
            "daily_notice_times_max_device": 3,
            "repeat_times": 2,
            "endure_seconds": 180,
            "extra_conf": null,
            "created_time": "2023-06-06 09:48:33",
            "updated_time": "2023-06-06 09:48:33",
            "is_deleted": false
        }
        """
        last_slash_index = message.topic.rfind("/")
        device_username = message.topic[last_slash_index + 1:]
        # 此处获取rule_ids 和 每个rule_id 对应的规则
        alarm_rule_ids = AssistTool.get_alarm_rule_ids(device_username)
        alarm_logger.debug(f"alarm_rule_ids: {alarm_rule_ids}")
        for alarm_id in alarm_rule_ids:
            try:
                rule = AssistTool.get_alarm_rule(device_username, alarm_id)
                base_key = f'{device_username}_on_{alarm_id}'
                state_key = f'warning_state:{base_key}'
                last_state = AssistTool.redis_alarm.get(state_key) or 'normal'
                state, attributes_data = AlarmState.get_state_by_new_message(
                    message,
                    device_username,
                    alarm_id,
                    last_state=last_state,
                    rule=rule
                )
                if state is None:
                    continue
                # 如果和上个状态一致，则不做处理
                if last_state == state:
                    if state == 'alerting':
                        AssistTool.redis_alarm.set(
                            f'alerting_data:{base_key}',
                            json.dumps(attributes_data)
                        )
                    continue
                AssistTool.redis_alarm.set(state_key, state)
                getattr(Transform, f'to_{state}')(
                    device_username,
                    alarm_id,
                    attributes_data,
                    last_state,
                    rule=rule
                )
                alarm_logger.debug(
                    f'state change success '
                    f'device: {device_username} '
                    f'alarm_id: {alarm_id} {last_state} --> {state}! '
                )
            except Exception as err:
                alarm_logger.error(err)
                alarm_logger.error(traceback.format_exc())
                alarm_logger.info(f'device_username: {device_username} alarm_id: {alarm_id} failed ')

    @staticmethod
    def _parse_device_disconnect(message: MQTTMessage):
        """
        设备离线 告警检测
        :param message:
        :return:
        """
        device_username = message.topic.split('/')[-1]
        # 此处获取rule_ids 和 每个rule_id 对应的规则
        alarm_rule_ids = AssistTool.get_alarm_rule_ids(device_username)
        for alarm_id in alarm_rule_ids:
            try:
                rule = AssistTool.get_alarm_rule(device_username, alarm_id)
                # alarm_logger.debug(f'rule: {rule}')
                if not rule['is_active']:
                    continue
                if rule.get('trigger_source') != 'device_offline':
                    continue
                endure_seconds = rule.get('endure_seconds')
                state, attributes_data = AlarmState.get_state_by_device_disconnect(
                    endure_seconds)
                key = f'warning_state:{device_username}_on_{alarm_id}'
                last_state = AssistTool.redis_alarm.get(key) or 'normal'
                # 如果和上个状态一致，则不做处理
                if last_state == state:
                    continue
                AssistTool.redis_alarm.set(key, state)
                getattr(Transform, f'to_{state}')(device_username, alarm_id, attributes_data, last_state)
            except Exception as err:
                alarm_logger.error(err)
                alarm_logger.error(traceback.format_exc())

    @staticmethod
    def _parse_device_connect(message: MQTTMessage):
        """
        设备上线 告警恢复检测
        :param message:
        :return:
        """

        device_username = message.topic.split('/')[-1]
        # 此处获取rule_ids 和 每个rule_id 对应的规则
        alarm_ids = AssistTool.get_alarm_rule_ids(device_username)
        for alarm_id in alarm_ids:
            try:
                alarm_id = int(alarm_id)
                rule = AssistTool.get_alarm_rule(device_username, alarm_id)
                if not rule['is_active']:
                    continue
                if rule.get('trigger_source') != 'device_offline':
                    continue
                key = f'warning_state:{device_username}_on_{alarm_id}'
                state = 'normal'
                last_state = AssistTool.redis_alarm.get(key) or 'normal'
                # 如果和上个状态一致，则不做处理
                if last_state == state:
                    continue
                attributes_data = [{
                    'name': '在线状态',
                    'value': '在线',
                    'unit': '',
                }]
                AssistTool.redis_alarm.set(key, state)
                Transform.to_normal(device_username, alarm_id, attributes_data, last_state)
            except Exception as err:
                alarm_logger.error(err)
                alarm_logger.error(traceback.format_exc())

    @classmethod
    def parse_msg(cls, message):
        """
        解析消息
        :param message:
        :return:
        """
        topic = message.topic
        if topic.startswith('internal/data'):
            cls._process(message)
        elif topic.startswith('internal/disconnect'):
            cls._parse_device_disconnect(message)
        elif topic.startswith('internal/connect'):
            cls._parse_device_connect(message)

    def on_message(self, client, user_data, message):
        alarm_logger.debug(f"topic: {message.topic} \n payload_type:{type(message.payload)}\n message.payload: {message.payload}")
        # msg = json.loads(message.payload)
        t = threading.Thread(target=self.parse_msg, args=(message,))
        t.start()
        # self._process(message)

    def on_connect(self, client, user_data, flags, rc):
        super().on_connect(client, user_data, flags, rc)
        self.subscribe([
            ('internal/data/+/+', 0),  # 属性上报触发
            ('internal/disconnect/+', 0),  # 设备离线
            ('internal/connect/+', 0),  # 设备上线
        ])


@catch_exception(default_error_message='告警引擎出错', logger=alarm_logger)
def main():
    receiver = MQTTReceiver(MQTT_CLIENT_ID+str(uuid.uuid4()), MQTT_HOST, MQTT_PORT,
                            MQTT_USERNAME, MQTT_PASSWORD, tls=MQTT_TLS, logger=alarm_logger)
    receiver.loop_forever()


if __name__ == "__main__":
    main()

