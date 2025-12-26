import binascii
import json
import pickle
import threading
import time
import traceback

import _setup_backend
import backend.m_common.set_timezone

import redis
from twisted.internet import reactor, protocol, endpoints
from twisted.internet.threads import deferToThread

from backend.device_shadow.device_shadow import DeviceShadow
from backend.m_common.communication import MRP, process_payload_by_msg_data_type
from backend.m_common.data_get_tool import GetDataTool
from backend.m_common.mq_factory import MqFactory
from backend.m_common.mqtt_pub_client_factory import MQTTPublishClientFactory, PublishClientNames, InternalPublishClientParams
from backend.m_common.redis_pool import rule_pool, unexpired_device_pool, down_mq_pool
from backend.m_common.time_util import get_utc_timestamp
from backend.m_common.tools import is_generator_empty
from backend.rule_engine.rule_engine_interface import RuleEngineInterface
from backend.tcp_server.config import TCP_SERVER_HOST, TCP_SERVER_PORT, tcp_server_logger, API_HOST_TCP_SERVER, \
    API_USER_TCP_SERVER, API_TOKEN_TCP_SERVER
from backend.tcp_server.log import log_msg_in, log_msg_out
from backend.tcp_server.regist_adapter import get_reg_frame


class StateMachine(object):
    """
    设备在线、离线状态机
    """

    def __init__(self):
        self.handlers = {}  # 状态转移函数字典
        self.state = None  # 初始状态

    def add_transition(self, name, handler):
        """
        添加状态转移函数
        :param name: 状态名
        :param handler: 状态转移函数
        """
        self.handlers[name] = handler

    def set_state(self, name):
        self.state = name

    def run(self, msg):
        handler = self.handlers[self.state]
        handler(msg)


class DeviceServer(protocol.Protocol):
    """
    设备-服务
    """

    def __init__(self):
        self._get_data_tool = GetDataTool(
            API_TOKEN_TCP_SERVER,
            API_USER_TCP_SERVER,
            API_HOST_TCP_SERVER,
            redis.Redis(connection_pool=rule_pool),
            tcp_server_logger)
        self._up_mq = MqFactory().get_mq('up')

    def _to_connect(self, src_msg):
        """状态转为在线"""
        socket = self.transport
        reg_frame = src_msg

        # 注册包适配
        fixed_reg_frame = get_reg_frame(src_msg, socket)
        if fixed_reg_frame:
            reg_frame = fixed_reg_frame

        reg_frame = reg_frame.decode('utf-8')

        # 注册报文不含&，则直接返回
        if '&' not in reg_frame:
            tcp_server_logger.warning(f'注册包 reg_frame={reg_frame}')
            self._state_machine.set_state('disconnect')
            return

        tcp_server_logger.info(f'reg_frame: {reg_frame}')

        device, password = reg_frame.split('&')
        device_info = shadow.get_info(device)
        if device_info and device_info['is_active']:
            check_password = device_info['password']
            if check_password == password:
                tcp_server_logger.debug(f'device: {device} 连接成功！')
                self.factory.add_device(device, socket)
                shadow.set_online(device, True, tcp_server_mqtt_client, is_notify=True)
                self._state_machine.set_state('connect')

                # 如果是自定义注册帧，则解析该帧
                if fixed_reg_frame:
                    self.parse_data(src_msg)
            else:
                self._state_machine.set_state('disconnect')
        else:
            self._state_machine.set_state('disconnect')

    def _to_disconnect(self, msg):
        """状态转为离线"""
        socket = self.transport
        device = self.factory.get_device_by_socket(socket)
        if not device:
            tcp_server_logger.debug(f'msg：{msg}')
            return
        self.factory.remove_device(socket)
        shadow.set_online(device, False, tcp_server_mqtt_client, is_notify=True)

    def connectionMade(self):
        """
        连接创建时
        """
        # 实例化状态机
        self._state_machine = StateMachine()
        self._state_machine.add_transition("connect", self._to_connect)
        self._state_machine.add_transition("disconnect", self._to_disconnect)
        self._state_machine.set_state('disconnect')

    def connectionLost(self, reason):
        """
        连接断开时
        :param reason: 断开的原因
        """
        self._state_machine.set_state('disconnect')
        self._state_machine.run(reason)

    def _get_data_stream_bind_tcp(self, username, category):
        """
        获取设备的自定义数据流
        :param username:
        :param category:
        :return:
        """
        ret = []
        api = f'api/category_data_streams/get_all/?device_category={category}'
        key = f'data_stream:{category}'
        data_stream = self._get_data_tool.get_data(username, api, key)
        # tcp_server_logger.info(f'data_stream：{data_stream}')
        if not data_stream:
            return ret
        return [i['key'] for i in data_stream if i['bind_tcp']]

    def parse_data(self, data):
        """
        解析处理收到消息
        :return:
        """
        log_msg_in(data)

        socket = self.transport
        # tcp_server_logger.info(f'tcp服务收到数据：{data.hex()}')
        # 获取注册包，维护设备与socket的关系
        # 状态机获取设备是否已经注册
        if self._state_machine.state == 'disconnect':
            self._state_machine.set_state('connect')
            self._state_machine.run(data)
            return
        device = self.factory.get_device_by_socket(socket)
        if not device:
            hex_repr = ' '.join([f'{byte:02x}' for byte in data]).upper()
            tcp_server_logger.error(f's <- c[{len(data)}]: {hex_repr}')
            tcp_server_logger.error(f'device:{device} data：{data}')
            return
        device_info = shadow.get_info(device)
        if not device_info or 'category' not in device_info:
            tcp_server_logger.debug(f'device：{device}')
            tcp_server_logger.debug(f'device_info：{device_info}')
            return
        category = device_info['category']['id']
        # tcp_server_logger.info(f'category：{category}')
        bind_tcp_li = self._get_data_stream_bind_tcp(device, category)
        # tcp_server_logger.info(f'bind_tcp_li：{bind_tcp_li}')
        if bind_tcp_li:
            up_msg = {
                'type': 'data',
                'username': device,  # 计划废弃
                'device_username': device,
                'payload': data,
                'time': get_utc_timestamp(),
                'identifier': bind_tcp_li[0],
                'communication_type': 'TCP'
            }
            tcp_server_logger.debug(f'up_msg：{up_msg}')
            self._up_mq.put_msg(pickle.dumps(up_msg))

    def dataReceived(self, data):
        """
        收到消息时，
        :param data: 接收到的消息, 放入上行队列中的数据有可能是一个JSON字符串
        :return:
        """

        try:
            self.parse_data(data)
        except Exception as _:
            tcp_server_logger.error(traceback.format_exc())


class DeviceFactory(protocol.Factory):
    """
    设备工厂
    """

    def __init__(self):
        self.devices = {}

    def buildProtocol(self, addr):
        """
        当一个设备连接时会先执行， 将设备工厂对象赋值为设备的factory属性
        :param addr:
        :return:
        """
        _protocol = DeviceServer()
        _protocol.factory = self
        return _protocol

    def add_device(self, device_id, socket):
        self.devices[device_id] = socket

    def remove_device(self, socket):
        device_id = self.get_device_by_socket(socket)
        if device_id:
            del self.devices[device_id]

    def get_socket_by_device(self, device_id):
        return self.devices.get(device_id)

    def get_device_by_socket(self, socket):
        for device_id, s in self.devices.items():
            if s == socket:
                return device_id
        return None


def send_message_to_device(device_username):
    """
    向设备下发消息
    :param device_username: 设备Key
    """
    device_tcp_mq = MqFactory().get_mq(mq_name='tcp_down_mq', sub_mq_name=device_username)

    try:
        device_info = shadow.get_info(device_username)
        access_protocol = device_info['category']['access_protocol']
        down_interval = device_info['category']['down_interval']
        tcp_server_logger.debug(f'下发时间间隔:{down_interval}毫秒')
        while True:
            data = device_tcp_mq.get_msg()
            if not data:
                break
            # todo 是否每发一次数据就检查一次socket对象
            socket = factory.get_socket_by_device(device_username)
            data = json.loads(data)
            if not socket:
                RuleEngineInterface().save_down_msg_log(device_username, data, err_msg='设备断开连接')
                tcp_server_logger.debug(f'{device_username}不存在socket对象!')
                continue
            RuleEngineInterface().save_down_msg_log(device_username, data)
            if access_protocol not in ['MRP', 'MGRP']:
                content, _ = process_payload_by_msg_data_type(data, logger=tcp_server_logger)
                log_msg_out(content)
                socket.write(content)
                tcp_server_logger.debug(f'{device_username}tcp服务下发数据{content}')
                time.sleep(down_interval / 1000)
            else:
                MRP.down_tcp_msg(device_info, socket, data, tcp_server_logger)
                time.sleep(0.5)
    except Exception as e:
        tcp_server_logger.error(traceback.format_exc())
    finally:
        redis_unexpired.unlink(f'is_processing_tcp:{device_username}')


def parse_msg(msg: dict):
    """
    tcp 下发消息回调函数
    :param msg:
    :return:
    """
    try:
        device_username = msg['username']
        device_tcp_mq = MqFactory().get_mq(mq_name='tcp_down_mq', sub_mq_name=device_username)
        device_tcp_mq.put_msg(json.dumps(msg))
        tcp_server_logger.debug(f'device_username: {device_username} 收到设备下发数据{msg}')
        if redis_unexpired.set(f'is_processing_tcp:{device_username}', 1, nx=True):
            tcp_server_logger.debug('开始拉起任务')
            # deferToThread(send_message_to_device, device_username)
            p = threading.Thread(target=send_message_to_device, args=(device_username,))
            p.start()
    except Exception as e:
        tcp_server_logger.error(traceback.format_exc())


def process_messages_from_queue():
    """
    下发消息任务
    :return:
    """
    tcp_server_logger.info('tcp_down_mq.wait_msg_blocked start')
    tcp_down_mq.wait_msg_blocked()


def monitor_and_disconnect():
    """
    监听设备禁用，禁用之后移除相应的socket,使之通信立刻断开
    """
    disable_channel = r'redis/device/disable'
    redis_pubsub_client.subscribe(disable_channel)
    for msg in redis_pubsub_client.listen():
        if msg['type'] == 'message' and str(msg['channel']) == disable_channel:
            data = msg['data']
            if isinstance(data, (bytes, bytearray)):
                data = data.decode()
            if data in factory.devices:
                device_socket = factory.get_socket_by_device(data)
                device_socket.loseConnection()
                shadow.set_online(data, False, tcp_server_mqtt_client)
                del factory.devices[data]


def clean_up_redis_key():

    # 删除队列
    if not (res := is_generator_empty(redis_down_mq.scan_iter('tcp_down_mq*')))[0]:
        redis_down_mq.unlink(*res[1])
    # 删除标记
    if not (res := is_generator_empty(redis_unexpired.scan_iter('is_processing_tcp*')))[0]:
        redis_unexpired.unlink(*res[1])


if __name__ == '__main__':
    redis_unexpired = redis.Redis(connection_pool=unexpired_device_pool)
    redis_pubsub_client = redis_unexpired.pubsub()

    redis_down_mq = redis.Redis(connection_pool=down_mq_pool)
    shadow = DeviceShadow(tcp_server_logger)
    _params_obj = InternalPublishClientParams(client_name=PublishClientNames.down_sender, send_to_mq=False)
    tcp_server_mqtt_client = MQTTPublishClientFactory.get_mqtt_client(_params_obj)
    tcp_down_mq = MqFactory().get_mq('tcp_down_mq', callback=parse_msg, logger=tcp_server_logger)

    clean_up_redis_key()

    factory = DeviceFactory()

    # 创建一个 TCP4ServerEndpoint 实例，指定监听 TCP_SERVER_HOST 和相应的端口
    endpoint = endpoints.TCP4ServerEndpoint(
        reactor, TCP_SERVER_PORT, interface=TCP_SERVER_HOST)

    # 使用 endpoint.listen 来启动监听
    endpoint.listen(factory)

    reactor.callInThread(process_messages_from_queue)
    reactor.callInThread(monitor_and_disconnect)
    reactor.run()
