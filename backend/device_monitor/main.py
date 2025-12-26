import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import _setup_backend
import backend.device_monitor._setup_django
import backend.m_common.set_timezone

from backend.device_monitor.config import MQTT_HOST, MQTT_PORT, MQTT_TLS, MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, \
    device_monitor_logger
from backend.device_monitor.event_monitor import DeviceMonitor
from backend.device_monitor.state_checker import DeviceStateChecker
from backend.m_common.debugger import catch_exception, rerun


@rerun(default_rerun_message='Device Monitor MQTT 监听器重启中', logger=device_monitor_logger)
def task1():
    monitor = DeviceMonitor(
        MQTT_CLIENT_ID + f'{time.time() * 1000}',
        MQTT_HOST,
        MQTT_PORT,
        MQTT_USERNAME,
        MQTT_PASSWORD,
        MQTT_TLS,
        device_monitor_logger
    )
    monitor.loop_forever()


@rerun(default_rerun_message='Device Monitor 在线轮询检测器重启中', logger=device_monitor_logger)
def task2():
    checker = DeviceStateChecker()
    checker.run()


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.submit(task1)
        pool.submit(task2)
