from django.db import models
from django.contrib.auth import get_user_model

from django.utils import timezone

from backend.apps.equipments.models import DeviceCategory, Device
from backend.apps.proj_common.const import DEVICE_ORIGIN, TASK_TYPE, TIMING_TYPES, \
    TASK_ACTION_TYPE
from backend.apps.users.models import Projects

User = get_user_model()


class Tasks(models.Model):
    """任务"""

    project = models.ForeignKey(
        Projects,
        related_name='project_tasks',
        verbose_name='项目',
        on_delete=models.CASCADE,
    )
    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='category_tasks',
        verbose_name='设备类型',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    device_origin = models.CharField(
        verbose_name='设备源类型',
        help_text='设备源类型',
        max_length=20,
        choices=DEVICE_ORIGIN,
    )
    name = models.CharField(
        verbose_name='任务名称',
        help_text='任务名称',
        max_length=50,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='任务描述',
        help_text='任务描述',
        null=True,
        blank=True,
    )
    task_type = models.CharField(
        verbose_name='任务类型',
        help_text='任务类型',
        max_length=50,
        choices=TASK_TYPE,
    )
    timing_type = models.CharField(
        verbose_name='定时类型',
        help_text='定时类型',
        max_length=50,
        choices=TIMING_TYPES,
        null=True,
        blank=True,
    )
    handel = models.CharField(
        verbose_name='操作内容',
        help_text='操作内容',
        max_length=100,
        null=True,
        blank=True,
    )
    timing_conf = models.JSONField(
        verbose_name='定时配置',
        help_text='定时配置',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name='是否启用', default=True)
    conf_for_type = models.JSONField(
        verbose_name='基于任务类型的相关配置',
        help_text='类型为自定义数据下发需要pubish_type推送方式和data_stream自定义数据流',
        null=True,
        blank=True,
    )
    is_record = models.BooleanField(
        verbose_name='任务 调试状态',
        help_text='任务 调试状态',
        default=False,
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

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = verbose_name


class TaskActions(models.Model):
    """任务操作"""
    task = models.ForeignKey(
        Tasks,
        related_name='task_actions',
        verbose_name='任务',
        on_delete=models.CASCADE,
    )
    action_type = models.CharField(
        verbose_name='操作类型',
        help_text='操作类型',
        max_length=100,
        choices=TASK_ACTION_TYPE,
        null=True,
        blank=True,
    )
    exec_conf = models.JSONField(
        verbose_name='操作配置',
        help_text='操作配置',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = '任务操作'
        verbose_name_plural = verbose_name


class DeviceTasks(models.Model):

    class Meta:
        verbose_name = '任务-设备级'
        verbose_name_plural = verbose_name

    device = models.ForeignKey(
        Device,
        related_name='device_tasks',
        verbose_name='设备',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(
        Tasks,
        related_name='task_devices',
        verbose_name='任务',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    last_run_time = models.DateTimeField(
        verbose_name='执行时间',
        help_text='执行时间',
        null=True,
        blank=True,
    )
    is_allow = models.BooleanField(verbose_name='是否允许设备使用', default=True)
