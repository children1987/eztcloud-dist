from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from backend.apps.users.models import User, Projects

MSG_SOURCE_MAP = {
    'alarm': '告警',
    'alarm_restored': '告警恢复',
    'alarm_ongoing': '告警持续',
    'announcement': '公告',
}


class NotifyRecord(models.Model):
    """
     消息模型
    """
    MSG_TYPE = (
        ('text', '文本'),
        ('markdown', 'Markdown格式'),
        ('html', '网页格式')
    )
    is_all = models.BooleanField(
        default=False,
        blank=True,
        db_index=True,
        verbose_name='是否全站通告',
        help_text='是否全站通告'
    )
    description = models.TextField(
        blank=True, null=True, help_text='消息描述', verbose_name='消息描述'
    )
    title = models.CharField(
        max_length=200,
        help_text='消息标题', verbose_name='消息标题'
    )
    msg_type = models.CharField(
        max_length=20, default='text', choices=MSG_TYPE,
        help_text='消息类型', verbose_name='消息类型'
    )
    msg_source = models.CharField(
        max_length=20, default='announcement',
        help_text='消息来源', verbose_name='消息来源'
    )
    content = models.TextField(
        help_text='消息内容', verbose_name='消息内容'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '消息'
        verbose_name_plural = verbose_name
        ordering = ('-timestamp',)


class NotifyRecordUser(models.Model):

    class Meta:
        verbose_name = '消息状态'
        verbose_name_plural = verbose_name
        ordering = ('-id',)
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    notify_record = models.ForeignKey(
        NotifyRecord,
        related_name='notify_users',
        on_delete=models.CASCADE,
        verbose_name='消息',
        help_text='消息'
    )
    recipient = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='user_notifications',
        on_delete=models.CASCADE,
        verbose_name='接收人', help_text='接收人'
    )
    is_read = models.BooleanField(
        default=False,
        blank=False,
        db_index=True,
        verbose_name='是否已读',
        help_text='是否已读'
    )
    read_time = models.DateTimeField(
        verbose_name='读取时间',
        help_text='读取时间',
        null=True,
        blank=True,
    )


class SmsRecord(models.Model):
    """
    短信发送记录
    """

    class Meta:
        verbose_name = '短信记录'
        verbose_name_plural = verbose_name
        ordering = ('-id',)
        indexes = [
            models.Index(fields=['template_key', 'mobile', 'is_succeed']),
        ]

    SMS_KEY_MAP_ = (
        ('register_invite', '注册邀请'),
        ('common_verify', '验证码'),
        ('alarm_message', '告警通知'),
        ('alarm_restored', '告警恢复通知'),
        ('alarm_ongoing', '告警持续通知')
    )

    project = models.ForeignKey(
        Projects,
        related_name='project_sms_records',
        verbose_name='项目',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    template_key = models.CharField(
        verbose_name='模板key',
        help_text='模板key',
        max_length=30,
        choices=SMS_KEY_MAP_
    )
    mobile = models.CharField(
        verbose_name='手机号',
        help_text='手机号',
        max_length=20,
    )
    request_id = models.CharField(
        verbose_name='请求标识',
        help_text='请求标识',
        max_length=64,
        null=True,
        blank=True
    )
    fee = models.PositiveSmallIntegerField(
        verbose_name='计费条数',
        help_text='计费条数',
        default=0
    )
    params = models.JSONField(
        verbose_name='短信参数',
        help_text='短信参数',
        null=True,
        blank=True
    )
    is_succeed = models.BooleanField(
        verbose_name='是否发送成功',
        help_text='是否发送成功',
        default=False
    )
    error_msg = models.TextField(
        verbose_name='失败原因',
        help_text='失败原因',
        null=True,
        blank=True
    )
    created_time = models.DateTimeField(
        verbose_name='发送时间',
        help_text='发送时间',
        default=timezone.now
    )
