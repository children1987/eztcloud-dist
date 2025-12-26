"""
本组件功能：
    1. 从down MQ中获取向设备下发的数据（数据格式详见down sender.md文档）
    2. 根据不同的消息类型、下发方式做出相应的处理（消息类型详见 down_sender.md 和 发布topic概览）
备注：
    当前仅实现 设备下发属性、设备下发命令、自定义数据下发、网关下发子设备属性、网关下发子设备命令
    本模块不做数据解析处理 其余模块向down MQ中写入数据时应提前处理成设备可识别的数据格式

"""
import json
import time
import traceback

import redis

import _setup_backend
import backend.m_common.set_timezone

from backend.down_sender.config import down_sender_logger
from backend.down_sender.down_manager import DownSenderDataServer
from backend.m_common.mq_factory import MqFactory
from backend.m_common.mqtt_pub_client_factory import MQTTPublishClientFactory, PublishClientNames, InternalPublishClientParams
from backend.m_common.redis_pool import down_mq_pool, unexpired_device_pool
from backend.m_common.time_util import get_utc_timestamp
from backend.m_common.tools import is_generator_empty


def purge_existing_down_tasks():
    # 每次重启down_sender时清空所有任务队列
    redis_down_db = redis.Redis(connection_pool=down_mq_pool)
    redis_unexpired_db = redis.Redis(connection_pool=unexpired_device_pool)
    if not (res := is_generator_empty(redis_down_db.scan_iter('down*')))[0]:
        redis_down_db.unlink(*res[1])
    if not (res := is_generator_empty(redis_unexpired_db.scan_iter('processing*')))[0]:
        redis_unexpired_db.unlink(*res[1])


def parse_msg(msg: dict):
    """
    作为回调函数 解析 mqtt的消息
    """
    # todo 异步操作
    down_sender_logger.debug(f'收到数据，开始解析。{msg}')
    msg['time'] = get_utc_timestamp()
    try:
        DownSenderDataServer(msg, down_mq_, tcp_down_mq, down_sender_mqtt_client).run()
    except Exception as err:
        down_sender_logger.error(traceback.format_exc())
        down_sender_logger.error(err)


def main():
    # 因为下发数据具有很强的时效性，每次启动down_sender之前down_mq可能已经累积了长时间的下发数据,故每次重启之前先清空队列
    purge_existing_down_tasks()
    down_mq = MqFactory().get_mq(
        'down',
        callback=parse_msg,
    )
    down_mq.wait_msg_blocked(concurrency=20, multi_thread=True)


if __name__ == '__main__':
    error_times = 0
    while True:
        try:
            down_mq_ = MqFactory().get_mq('down')
            tcp_down_mq = MqFactory().get_mq('tcp_down_mq')
            _params_obj = InternalPublishClientParams(client_name=PublishClientNames.down_sender,
                                                      logger=down_sender_logger)
            down_sender_mqtt_client = MQTTPublishClientFactory.get_mqtt_client(_params_obj)
            main()
        except Exception as err:
            down_sender_logger.error(traceback.format_exc())
        error_times += 1
        if error_times <= 6:
            time.sleep(error_times * 10)
        else:
            time.sleep(60)
