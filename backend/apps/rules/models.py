from django.db import models
from django.contrib.auth import get_user_model

from django.utils import timezone

from backend.apps.equipments.models import DeviceCategory, Device
from backend.apps.proj_common.const import DEVICE_ORIGIN, RULE_TYPE
from backend.apps.users.models import Projects

User = get_user_model()


class Rules(models.Model):
    """规则"""

    project = models.ForeignKey(
        Projects,
        related_name='project_rules',
        verbose_name='项目',
        on_delete=models.CASCADE
    )
    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='category_rules',
        verbose_name='设备类型',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    device_origin = models.CharField(
        verbose_name='设备源类型',
        help_text='设备源类型',
        max_length=20,
        choices=DEVICE_ORIGIN,
    )
    name = models.CharField(
        verbose_name='规则名称',
        help_text='规则名称',
        max_length=50,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='规则描述',
        help_text='规则描述',
        null=True,
        blank=True,
    )

    rule_type = models.CharField(
        verbose_name='规则类型',
        help_text='规则类型',
        max_length=50,
        choices=RULE_TYPE,
    )

    condition = models.JSONField(
        verbose_name='属性条件配置',
        help_text='属性条件配置',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name='是否启用', default=True)
    event_identifier = models.CharField(
        verbose_name='事件标识符',
        help_text='规则类型为EU(事件上报)时，必传',
        null=True,
        blank=True,
        max_length=50,
    )
    data_stream_identifier = models.CharField(
        verbose_name='数据流标识符',
        help_text='规则类型为DU(自定义上报）时，必传',
        null=True,
        blank=True,
        max_length=50,
    )

    is_record = models.BooleanField(
        verbose_name='规则 调试状态',
        help_text='规则 调试状态',
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
        verbose_name = '规则'
        verbose_name_plural = verbose_name


class RuleActions(models.Model):
    """规则操作"""

    rule = models.ForeignKey(
        Rules,
        related_name='actions',
        on_delete=models.CASCADE,
        verbose_name='规则',
    )
    action_type = models.CharField(
        verbose_name='操作类型',
        help_text='操作类型',
        max_length=100,
    )
    exec_conf = models.JSONField(
        verbose_name='操作配置',
        help_text='操作配置',
        null=True,
        blank=True,
    )
    order = models.IntegerField(
        verbose_name='序号',
        help_text='序号',
        default=1,
    )

    class Meta:
        verbose_name = '规则操作'
        verbose_name_plural = verbose_name


class DeviceRules(models.Model):
    """设备规则"""

    device = models.ForeignKey(
        Device,
        related_name='device_rules',
        verbose_name='设备',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    rule = models.ForeignKey(
        Rules,
        related_name='rule_devices',
        verbose_name='规则',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    is_allow = models.BooleanField(verbose_name='是否允许设备使用', default=True)

    class Meta:
        verbose_name = '规则-设备级'
        verbose_name_plural = verbose_name
