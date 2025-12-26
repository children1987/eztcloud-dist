import json
import time
import traceback
import uuid
from copy import deepcopy

import _add_sys_path
import backend.notifier._setup_django
import backend.m_common.set_timezone

from django.contrib.auth import get_user_model

from backend.apps.wechat.biz.mp import WechatPublicAccount
from backend.apps.dingtalk.biz.dingtalk_agent import DingtalkAgent
from backend.apps.notice.models import NotifyRecord, NotifyRecordUser, SmsRecord
from backend.m_common.dingtalk.dingtalk import SendMsg as SendDingtalk
from backend.m_common.my_email import MyEmail
from backend.m_common.mqtt_pub_client_factory import MQTTPublishClientFactory, PublishClientNames, InternalPublishClientParams
from backend.m_common.sms.tencent.sms_sender import send as send_sms
from backend.m_common.mq_factory import MqFactory
from backend.notifier.config import SMS_ID
from backend.notifier.log import logger
from backend.notifier.notify_template import NOTIFY_TEMPLATE

User = get_user_model()


class Notifier(object):
    """
    读取notify MQ 中待发的通知，并通过短信，电子邮件，钉钉群机器人，企业微信群机器人(待实现)，
    飞书机器人（待实现）通知用户
    """
    _dingtalk_agent = DingtalkAgent()
    _params_obj = InternalPublishClientParams(client_name=PublishClientNames.notifier, send_to_mq=False, logger=logger)
    _mqtt_client = MQTTPublishClientFactory.get_mqtt_client(params_obj=_params_obj)

    @staticmethod
    def _sms(aims: list, template_key, params: list, **kwargs):
        """
        以短信的形式通知用户
        """
        sms_id = SMS_ID[template_key]
        project_id = kwargs.get('project_id')
        logger.info(f'aims = {aims}, sms_id = {type(sms_id)}{sms_id} , params = {params}')
        res_data, err_data = send_sms(aims, sms_id, params, logger=logger)
        if template_key == 'common_verify':
            params[0] = '****'
        # 记录短信发送日志
        create_data = {
            'project_id': project_id,
            'template_key': template_key,
            'params': params,
        }
        if res_data:
            create_data['request_id'] = res_data['RequestId']
            for each_info in res_data['SendStatusSet']:
                mobile = each_info['PhoneNumber']
                fee = each_info['Fee']
                if fee == 0:
                    is_succeed = False
                    error_msg = each_info['Message']
                else:
                    is_succeed = True
                    error_msg = None
                SmsRecord.objects.create(
                    mobile=mobile,
                    fee=fee,
                    is_succeed=is_succeed,
                    error_msg=error_msg,
                    **create_data
                )
        else:
            create_data['error_msg'] = err_data['message']
            create_data['request_id'] = err_data.get('request_id')
            for mobile in aims:
                if not mobile:
                    continue
                SmsRecord.objects.create(
                    mobile=mobile,
                    **create_data
                )



    @staticmethod
    def _email(aims: list, template_key, params: list, **kwargs):
        """
        以email的形式通知用户
        """
        title_params = kwargs['title_params']

        em = MyEmail()
        em_subject_template = NOTIFY_TEMPLATE[template_key]['template']['email']['title']
        em_content_template = NOTIFY_TEMPLATE[template_key]['template']['email']['content']
        em_content_html = em_content_template.format(*params)

        logger.debug(f'content_text={em_content_html}')

        em.Subject = em_subject_template.format(*title_params)
        em.to_list = aims
        em_msg = em.get_mail_content(html_msg=em_content_html)
        em.send(em_msg)

    @classmethod
    def _ding_robot(cls, aims: dict, template_key, params: list, **kwargs):
        """
        以钉钉群消息的形式通知用户
        """
        url = aims['url']
        secret = aims['secret']
        sender = SendDingtalk(url, secret, logger=logger)
        assert template_key in NOTIFY_TEMPLATE
        msg_body = deepcopy(NOTIFY_TEMPLATE[template_key]['template']['ding_work'])
        res = sender.send(msg_body, params=params, **kwargs)
        logger.debug(f"ding_robot message_status: {res}")

    @classmethod
    def _ding_work(cls, aims: list, template_key, params: list, **kwargs):
        title_params = kwargs['title_params']
        ding_work_template = NOTIFY_TEMPLATE[template_key]['template']['ding_work']
        msg_body = {
            "msgtype": ding_work_template["msgtype"],
            "markdown": {
                "title": ding_work_template["markdown"]["title"].format(*title_params),
                "text": ding_work_template['markdown']["text"].format(*params),
            }
        }
        res = cls._dingtalk_agent.send_corp_conversation(
            mobiles=aims,
            msg=msg_body
        )
        logger.debug(res)

    @classmethod
    def _wechat(cls, aims: list, template_key, params: list, **kwargs):
        wx_info = kwargs['wx_info']
        wx_template = deepcopy(NOTIFY_TEMPLATE[template_key]["template"]['wechat'])
        wx_template['data'] = json.loads(wx_template['data'].format(*params))
        wx_template['template_id'] = wx_info['tpl_id']
        logger.info(wx_template)
        wechat_account = WechatPublicAccount(
            wx_info['app_id'],
            wx_info['app_secret']
        )
        for touser in aims:
            wx_template['touser'] = touser
            res = wechat_account.send_template_message(wx_template)
            logger.info(res)

    @classmethod
    def _mqtt(cls, aims: list, template_key, params: list, **kwargs):
        """
        Args:
            aims: ["topic",]
            template_key: "device_online_message"
            params: ["device_name", "is_online"]
        """
        mqtt_template = NOTIFY_TEMPLATE[template_key]["template"]["mqtt"]
        topic_str = mqtt_template["topic"]
        payload_str = mqtt_template["payload"]
        for aim in aims:
            topic = topic_str.format(aim)
            payload = payload_str.format(*params)
            cls._mqtt_client.publish(topic, payload)
            logger.info(f"topic: {topic}, payload: {payload}")

    @classmethod
    def _site_msg(cls, aims: list, template_key, params: list, **kwargs):
        """
        以站内信的形式发送通知
        Args:
            aims: 目标人员账号列表
            template_key: alarm 或 announcement ，详情 backend/apps/notice/models.py: MSG_SOURCE_MAP
            params: 其它参数
            title_params: 标题参数
        """
        title_params = kwargs['title_params']
        site_msg_template = deepcopy(NOTIFY_TEMPLATE[template_key]["template"]["site_msg"])
        create_params = site_msg_template["create_params"].format(*params)
        title = site_msg_template["title"].format(*title_params)
        notify_record = NotifyRecord.objects.create(title=title, **json.loads(create_params))
        msgs = []
        logger.info(f'create_params: {create_params}')
        for user in User.objects.filter(username__in=aims):
            msgs.append(NotifyRecordUser(
                notify_record=notify_record,
                recipient=user
            ))
        if msgs:
            NotifyRecordUser.objects.bulk_create(msgs)

    def notify(self, msg: dict):
        """
        向用户发送通知
        """
        logger.debug(f'got a msg:{msg}')
        # 公共参数
        method = msg['method']
        aims = msg['aims']
        params = msg["params"]
        template_key = msg['template_key']
        # 邮件和钉钉额外参数
        title_params = msg.get("title_params", [])
        # 微信额外参数
        wx_info = msg.get("wx_info", {})
        # time = msg['time']
        if not hasattr(self, f'_{method}'):
            logger.error(f'method={method} is invalid!')
            return
        # 项目ID
        project_id = msg["project_id"] if "project_id" in msg else None
        try:
            getattr(self, f'_{method}')(
                aims,
                template_key,
                params,
                title_params=title_params,
                wx_info=wx_info,
                project_id=project_id
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(f'msg:{msg}, reason:{e}')


if __name__ == "__main__":
    while True:
        logger.info('notifier started.')
        try:
            notifier = Notifier()
            notify_mq = MqFactory().get_mq('notify', callback=notifier.notify, logger=logger)
            notify_mq.wait_msg_blocked(concurrency=4)
        except Exception as e:
            logger.error(traceback.format_exc())

    # email_test
    # aims = ['v1150121351@126.com', ]
    # template_key = 'alarm_message'
    # params = ['device', 'rule', 'remark']
    # title_params = ['device']
    # Notifier()._email(aims, template_key, params, title_params)

    # msg = {
    #     'method': 'email',
    #     'aims': ['v1150121351@126.com'],
    #     'template_key': 'register_invite',
    #     'title_params': ['梁凯', 'EZtCloud', '周智鹏专用测试项目'],
    #     'params': ['梁凯', 'EZtCloud', '周智鹏专用测试项目', '邮箱', '邮箱', '39188043@qq.com',
    #                'https://api.isw.hotanzn.com', 'email', '39188043@qq.com'],
    #     'time': 1683785949493
    # }
    # # Notifier()._notify(msg)
