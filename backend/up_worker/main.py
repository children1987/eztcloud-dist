"""
本组件功能：
    1. 从redis中获取设备上报的数据（数据格式详见up receiver.md文档）
    2. 根据不同的消息类型做出相应的处理（消息类型详见 up_receiver.md 订阅topic概览）
    其中需要访问关系型数据库，来获取处理方法需要的数据
    其中需要缓存机制来降低数据库压力
依赖关系：
    依赖device_shadow组件
    依赖up_MQ 组件
"""
import json
import time
import traceback

import _setup_backend
import backend._setup_django
import backend.m_common.set_timezone
from backend.m_common.mq_factory import MqFactory
from backend.m_common.mqtt_pub_client_factory import MQTTPublishClientFactory, \
    PublishClientNames, InternalPublishClientParams
from backend.m_common.custom_logger import WATCH_LOG_LEVEL
from backend.rule_engine.biz.tools import save_msg_log
from backend.up_worker.config import up_worker_logger
from backend.device_shadow.device_shadow import DeviceShadow
from backend.up_worker.msg_handler_mapping import MSG_HANDLER
from backend.up_worker.utils import DataTypeCheck


def init_django():
    """
    子进程内Django初始化函数，保证仅执行一次
    """

    try:
        from django.conf import settings
        if not settings.configured:
            import backend._setup_django
    except:
        up_worker_logger.error(traceback.format_exc())


def update_msg_info(msg, username, device_info):
    """
    更新up_mq上报的消息，增加username对应设备的基本信息
    sub_devices： 字段示例
        "01": {
            "id": 72,
            "code": "01",
            "username": "DU_qBinSxu9qx"
        },
        "02": {
            "id": 75,
            "code": "02",
            "username": "DU_rTAuCfSuRY"
        },
    :param msg: up_mq中的一条消息, 字段定义格式详见mqtt_receiver.md字段规范
    :param username: 设备的username，获取设备相关信息
    :param device_info: 设备影子数据
    :return:
    """
    project_id = device_info['project']
    project_info = device_info['category']['project']
    info = {
        'project_id': project_id,   # 弃用，之后需要project数据直接从project字段取
        'project_name': project_info.get('name', project_id),  # 弃用，之后需要project数据直接从project字段取
        'category_id': device_info['category']['id'],
        # 接入协议
        'access_protocol': device_info['category']['access_protocol'],
        # 设备是否需要响应
        'is_send_response': device_info['category'].get('is_send_response', False),
        # 节点类型
        'node_type': device_info['category']['node_type'],
        # 子设备地址
        'sub_code': device_info['code'],
        'device_username': username,
        'device_name': device_info['name'],
        'is_record': device_info['is_record'],
        'sub_devices': device_info.get('sub_devices'),
        'project': project_info
    }
    msg.update(info)
    return msg


def get_device_is_online(online_cfg, msg):
    """
    基于属性获取设备当前状态
    :param online_cfg:
    :param msg:
    :return:
    """
    # 配置上线下状态属性的 上报数据不含状态的不处理
    is_online = None
    try:
        if isinstance(online_cfg, str):
            online_cfg = json.loads(online_cfg)
        attr_key = online_cfg['attr_key']
        attr_value = online_cfg['attr_value']
        if attr_key not in msg['payload']:
            return is_online
        is_online = msg['payload'][attr_key] == attr_value
    except Exception as _:
        up_worker_logger.error(traceback.format_exc())
        up_worker_logger.error(f'【up_worker_handler】online_cfg:{online_cfg} msg:{msg}')
    return is_online


def run(msg):
    """
    :param msg: 从上行队列中拿出来的原始数据
    :return:
    """
    up_worker_logger.debug(f'【up_worker_handler】:{msg}')
    try:
        init_django()
        params_obj = InternalPublishClientParams(
            client_name=PublishClientNames.up_worker,
            logger=up_worker_logger,
            send_to_mq=False
        )
        up_worker_mqtt_client = MQTTPublishClientFactory.get_mqtt_client(params_obj)
        device_shadow = DeviceShadow(up_worker_logger)
        msg_type = msg['type']
        username = msg.get('username') or msg.get('device_username')
        # 修复：payload 可能是 bytes 类型，需要先检查类型再调用 .keys()
        payload = msg.get("payload", {})
        if isinstance(payload, dict):
            payload_keys = list(payload.keys())
        else:
            payload_keys = "N/A (bytes)"
        up_worker_logger.debug(
            f'[up_worker] 开始处理 attributes 消息: username={username}, '
            f'device_username={msg.get("device_username")}, payload_keys={payload_keys}'
        )
        # 如果设备被禁用，此设备所有上报为无效
        device_info = device_shadow.get_info(username)
        if not device_info:
            up_worker_logger.error(f'[up_worker] 设备信息未找到: username={username}, msg_type={msg_type}, msg={msg}')
            return
        if not device_info['is_active']:
            device_shadow.set_online(username, False)
            up_worker_logger.debug(f'设备已禁用：{username}')
            return
        if 'time' in msg:
            msg_timestamp = int(str(msg['time'])[:13])
        else:
            msg_timestamp = int(time.time() * 1000)
        # 更新设备活跃时间
        device_shadow.set_device_last_active_timestamp(username, timestamp=msg_timestamp)
        online_cfg = device_info['category'].get('online_cfg')
        if not online_cfg:
            # 更新设备在线状态与状态变化时间
            device_shadow.set_online(
                username,
                is_online=True,
                mqtt_client=up_worker_mqtt_client,
                state_time=msg_timestamp,
                device_info=device_info
            )
        updated_msg = update_msg_info(msg, username, device_info)
        # 非自定义上报 其数据类型为JSON
        if msg_type == 'data':
            updated_msg = MSG_HANDLER[msg_type](
                up_worker_mqtt_client
            ).update_payload(updated_msg)
        else:
            # 在自定义上报handler方法中 更新为自定义数据流的格式
            updated_msg['data_type'] = 'J'
            updated_msg['data_type_text'] = 'JSON'
            updated_msg = DataTypeCheck.check_msg(updated_msg)
        # 记录设备上报日志
        if not updated_msg.get('is_valid'):
            if 'err_msg' in updated_msg:
                err_msg = updated_msg.pop('err_msg')
            else:
                data_type_text = updated_msg.get('data_type_text', '')
                err_msg = f'{data_type_text} 数据格式错误！'
            extra = {
                'err_data': {
                    'errcode': 400,
                    'err_msg': err_msg
                }
            }
            save_msg_log(updated_msg, msg_type, extra)
            # 截断超长日志打印
            log_msg = str(msg)
            if len(log_msg) > 512:
                log_msg = log_msg[:512] + "... [truncated]"
            up_worker_logger.info(f'【up_worker】 设备：{username}上报数据格式校验失败 msg:{log_msg}')
            return
        save_msg_log(updated_msg, msg_type)
        # 2. 根据不同的消息类型做出相应操作
        up_worker_logger.debug(f'[up_worker] 准备执行 attributes handler: username={username}')
        MSG_HANDLER[msg_type](up_worker_mqtt_client).exec(updated_msg)
        up_worker_logger.debug(f'[up_worker] attributes handler 执行完成: username={username}')
        if msg_type == 'attributes' and online_cfg and msg:
            is_online = get_device_is_online(online_cfg, msg)
            if is_online is None:
                return
            old_state = device_shadow.get_device_state(username, device_info['project'])
            is_notify = old_state != is_online
            device_shadow.set_online(
                username,
                is_online=is_online,
                mqtt_client=up_worker_mqtt_client,
                is_notify=is_notify,
                state_time=msg_timestamp,
                device_info=device_info
            )
            up_worker_logger.debug(f'设备：{username} 上报属性，解析状态：{is_online}， online_cfg: {online_cfg}')
    except Exception as e:
        up_worker_logger.error(traceback.format_exc())
        up_worker_logger.error(f'【up_worker_handler】msg:{msg}')


def main():
    mq_interface = MqFactory().get_mq('up', callback=run)
    mq_interface.wait_msg_blocked(
        concurrency=4,
        multi_process=True,
        interval_time=0.01
    )


if __name__ == '__main__':
    main()
