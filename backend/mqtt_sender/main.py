import time
import uuid

import _setup_backend
import backend.m_common.set_timezone
from backend.m_common.debugger import rerun, catch_exception
from backend.m_common.mq_factory import MqFactory
from backend.m_common.custom_logger import WATCH_LOG_LEVEL
from backend.m_common.mqtt_pub_client_factory import (MQTTPublishClientFactory, PublishClientNames,
                                              InternalPublishClientParams, ExternalPublishClientParams)
from backend.mqtt_sender.config import mqtt_sender_logger


def get_mqtt_sender_publish_client(link_params=None):
    if link_params is None:
        mqtt_sender_logger.debug('no link params, use default.')
        params_obj = InternalPublishClientParams(client_name=PublishClientNames.mqtt_sender, is_reuse=True,
                                                 logger=mqtt_sender_logger, send_to_mq=False)
        return MQTTPublishClientFactory.get_mqtt_client(params_obj=params_obj)
    else:
        """
        :param link_params:
        {
            'mqtt_host': 'broker.mcp.leadot.com.cn',
            'mqtt_port': '9883',
            'client_id': 'isw_adapter_', 
            'username': 'isw_adapter', 
            'password': 'jdfg2234rf9tert453fwert43', 
            'tls': False, 
            'topic': 'open/mcp/isw_adapter'
        }
        """
        mqtt_sender_logger.debug(f'to external broker: {link_params}')

        client_id = link_params['client_id']
        broker_url = link_params["mqtt_host"]
        port = link_params["mqtt_port"]
        ident_name = (client_id, broker_url, port)

        _link_params = {
            'client_id': client_id,
            'broker_url': broker_url,
            'port': port,
            'username': link_params['username'],
            'password': link_params['password'],
            'tls': link_params['tls'],
        }
        params_obj = ExternalPublishClientParams(client_name=ident_name, link_params=_link_params,
                                                 logger=mqtt_sender_logger)
        return MQTTPublishClientFactory.get_mqtt_client(
            params_obj=params_obj,
            external_broker=True
        )


def parse_mq_msg(msg: dict):
    """
    mqtt_sender mq 的回调函数
    Args:
        msg: 收到的字典{"topic": "topic", "payload": "payload", ....}， 不关心payload格式，发送的地方处理好
    """
    link_params = msg.pop('link_params', None)
    mqtt_sender_logger.debug(f'new message: {msg}')
    mqtt_pub_client = get_mqtt_sender_publish_client(link_params)
    if mqtt_pub_client.external:
        pass
        # 保证收到1次消息
        # qos = msg.get('qos', 2)
        # 保证超时未发送成功后将消息丢弃
        # properties = msg.get('properties', {})
        # properties.update({'message_expiry_interval': 300})
        # msg.update(qos=qos, properties=properties)

    ret = mqtt_pub_client.publish(**msg)
    # mqtt_sender_logger.info(f'is_published: {(is_published := ret.is_published())}')
    # if not is_published:
    #     mqtt_sender_logger.info(f"waiting for publish...")
    #     ret.wait_for_publish()
    #     mqtt_sender_logger.info(f"is_published: {ret.is_published()}")


@rerun(default_rerun_message="mqtt_sender is restarting", logger=mqtt_sender_logger)
@catch_exception(default_error_message="mqtt_sender error", logger=mqtt_sender_logger)
def main():
    mqtt_sender_mq = MqFactory.get_mq("mqtt_sender", callback=parse_mq_msg)
    mqtt_sender_mq.wait_msg_blocked(concurrency=4, multi_process=True)


if __name__ == '__main__':
    main()



