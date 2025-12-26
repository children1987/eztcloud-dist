from django.db import models

from backend.apps.common.models import BaseModel
from backend.apps.users.models import User, Projects
from backend.apps.equipments.models import Device


class SceneConfig(BaseModel):
    """
    场景设置
    """

    name = models.CharField(
        verbose_name='场景名称',
        help_text='场景名称',
        max_length=100
    )
    description = models.TextField(
        verbose_name='场景描述',
        help_text='场景描述',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        Projects,
        related_name='project_scenes',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='所属组织',
        help_text='所属组织'
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        default=True,
        help_text='是否启用'
    )
    # 场景 生效时间{一次、每天、week } - 触发条件  json{定时、温度、湿度、PM2.5、日出日落}
    cfg_info = models.JSONField(
        verbose_name='场景配置详情',
        help_text='场景配置详情',
        null=True,
        blank=True
    )
    trigger_type = models.CharField(
        verbose_name='触发类型',
        help_text='触发类型',
        max_length=100,
        null=True,
        blank=True,
    )
    tag_conf = models.JSONField(
        verbose_name='标签',
        help_text='标签',
        null=True,
        blank=True,
    )
    is_external_sys = models.BooleanField(
        verbose_name='是否外部系统',
        help_text='是否外部系统',
        default=False
    )
    order = models.IntegerField(
        verbose_name='场景序号',
        help_text='场景序号',
        default=0,
        db_index=True
    )
    creator = models.ForeignKey(
        User,
        verbose_name='创建人',
        on_delete=models.SET_NULL,
        help_text='创建人',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = '场景设置'
        verbose_name_plural = verbose_name


class SceneDevice(models.Model):
    """
    场景动作
    """

    scene = models.ForeignKey(
        SceneConfig,
        verbose_name='场景',
        on_delete=models.CASCADE,
        related_name='scene_devices',
        blank=True,
        null=True,
        help_text='场景'
    )
    device = models.ForeignKey(
        Device,
        verbose_name='设备',
        on_delete=models.SET_NULL,
        related_name='device_scenes',
        blank=True,
        null=True
    )
    action_msg = models.JSONField(
        verbose_name='设备执行动作',
        help_text='设备执行动作',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = '场景动作'
        verbose_name_plural = verbose_name

