from django.db import models
from django.contrib.auth import get_user_model

from django.utils import timezone

from backend.apps.equipments.models import DeviceCategory, Device
from backend.apps.proj_common.const import DEVICE_ORIGIN, ALARM_DEGREE
from backend.apps.users.models import Projects

User = get_user_model()


class AlarmNoticeGroup(models.Model):
    """告警通知组"""

    project = models.ForeignKey(
        Projects,
        related_name='alarm_notice_groups',
        verbose_name='项目',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    name = models.CharField(
        verbose_name='告警通知组名称',
        help_text='告警通知组名称',
        max_length=50,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='告警通知组描述',
        help_text='告警通知组描述',
        null=True,
        blank=True,
    )
    use_member = models.BooleanField(
        verbose_name='是否启用成员通知',
        help_text='是否启用成员通知',
        default=False
    )
    use_ding_robot = models.BooleanField(
        verbose_name='是否启用钉钉机器人通知',
        help_text='是否启用钉钉机器人通知',
        default=False
    )
    use_webhook = models.BooleanField(
        verbose_name='是否推送到外部URL',
        help_text='是否推送到外部URL',
        default=False
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        default=True
    )
    notice_conf = models.JSONField(
        verbose_name='告警组配置',
        help_text='告警组配置',
    )
    creator = models.ForeignKey(
        User,
        related_name='creator_user',
        verbose_name='创建人',
        help_text='创建人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_time = models.DateTimeField(
        verbose_name="创建时间",
        help_text="创建时间",
        default=timezone.now,
    )
    updated_time = models.DateTimeField(
        verbose_name="更新时间",
        help_text="更新时间",
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        verbose_name='是否已删除',
        help_text="是否已删除",
        default=False,
    )

    class Meta:
        verbose_name = '告警通知组'
        verbose_name_plural = verbose_name


class Alarms(models.Model):

    class Meta:
        verbose_name = '告警配置'
        verbose_name_plural = verbose_name

    STATE_MAP = {
        'normal': '正常',
        'pending': '告警待定',
        'alerting': '告警'
    }

    TRIGGER_SOURCE = (
        ('device_offline', '设备下线'),
        ('device_attr', '设备属性')
    )

    project = models.ForeignKey(
        Projects,
        related_name='project_alarms',
        verbose_name='项目',
        on_delete=models.CASCADE,
    )
    notice_group = models.ForeignKey(
        AlarmNoticeGroup,
        verbose_name='告警通知组',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    device_origin = models.CharField(
        verbose_name='设备源类型',
        help_text='设备源类型',
        choices=DEVICE_ORIGIN,
        max_length=20,
    )
    trigger_source = models.CharField(
        verbose_name='告警触发源',
        help_text='告警触发源',
        choices=TRIGGER_SOURCE,
        max_length=20,
        default='device_attr'
    )
    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='category_alarms',
        verbose_name='设备类型',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='告警配置名称',
        help_text='告警配置名称',
        max_length=50,
        null=True,
        blank=True)
    condition = models.JSONField(
        verbose_name='告警触发条件',
        help_text='告警触发条件',
        null=True,
        blank=True
    )
    is_set_action = models.BooleanField(
        verbose_name='是否告警联动',
        default=False
    )
    is_external_sys = models.BooleanField(
        verbose_name='是否外部系统',
        help_text='是否外部系统',
        default=False
    )
    action_cfg = models.JSONField(
        verbose_name='告警联动配置',
        help_text='告警联动配置',
        null=True,
        blank=True,
    )
    degree = models.CharField(
        verbose_name='告警级别',
        help_text='告警级别',
        max_length=20,
        choices=ALARM_DEGREE,
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        default=True
    )
    is_again_notify = models.BooleanField(
        verbose_name='告警持续时是否再次通知',
        help_text="告警持续时是否再次通知",
        default=False,
    )
    again_notify_numb = models.SmallIntegerField(
        verbose_name='再次通知次数',
        help_text='再次通知次数',
        default=0
    )
    interval_hours = models.SmallIntegerField(
        verbose_name='通知间隔(小时)',
        help_text='通知间隔(小时)',
        default=1
    )
    remark = models.TextField(
        verbose_name='告警备注',
        help_text='告警备注',
        null=True,
        blank=True,
    )
    daily_notice_times_max = models.IntegerField(
        verbose_name='每日通知次数上限',
        help_text='每日通知次数上限',
        null=True,
        blank=True,
    )
    daily_notice_times_max_device = models.IntegerField(
        verbose_name='单设备每日通知次数上限',
        help_text='但设备每日通知次数上限',
        null=True,
        blank=True,
    )
    repeat_times = models.IntegerField(
        verbose_name='重复次数',
        help_text='重复次数',
        default=0
    )
    endure_seconds = models.IntegerField(
        verbose_name='持续时间',
        help_text='持续时间 (秒)',
        default=0
    )
    allow_manual_clear = models.BooleanField(
        verbose_name='是否允许手动解除告警',
        help_text='是否允许手动解除告警',
        default=False,
    )
    extra_conf = models.JSONField(
        verbose_name='告警额外配置',
        help_text='告警额外配置',
        null=True,
        blank=True,
    )
    tag_conf = models.JSONField(
        verbose_name='告警标签',
        help_text='告警标签',
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        User,
        verbose_name='创建人',
        help_text='创建人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_time = models.DateTimeField(
        verbose_name="创建时间",
        help_text="创建时间",
        default=timezone.now,
    )
    updated_time = models.DateTimeField(
        verbose_name="更新时间",
        help_text="更新时间",
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        verbose_name='是否已删除',
        help_text="是否已删除",
        default=False,
    )


class DeviceAlarms(models.Model):

    class Meta:
        verbose_name = '告警配置-设备级'
        verbose_name_plural = verbose_name

    device = models.ForeignKey(
        Device,
        related_name='device_alarms',
        verbose_name='设备',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    alarm = models.ForeignKey(
        Alarms,
        related_name='alarm_devices',
        verbose_name='告警',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    is_allow = models.BooleanField(verbose_name='是否允许设备使用', default=True)
