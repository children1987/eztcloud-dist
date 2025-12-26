from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from backend.apps.equipments.models import Command, Device, DeviceCategoryAttrs
from backend.apps.scenes.models import SceneConfig
from backend.apps.users.models import Projects

User = get_user_model()


class ControlPanel(models.Model):
    """
    操控面板
    """

    project = models.ForeignKey(
        Projects,
        related_name='project_control_panels',
        verbose_name='项目',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='操控面板名称',
        help_text='操控面板名称',
        max_length=100
    )
    key = models.CharField(
        verbose_name='操控面板唯一标识',
        help_text='操控面板唯一标识：以"CK_"开头，如"CK_XXX"',
        max_length=64,
        unique=True
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        help_text='是否启用',
        default=True
    )
    secret_key = models.CharField(
        verbose_name='面板口令',
        help_text='面板口令',
        max_length=64,
        null=True,
        blank=True
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

    class Meta:
        verbose_name = '操控面板'
        verbose_name_plural = verbose_name


class ControlPanelButton(models.Model):
    """
    操控面板按钮
    """
    BUTTON_TYPE_ = (
        ('command', '命令实例'),
        ('scene', '智能场景'),
        ('attr', '设备属性'),
    )

    name = models.CharField(
        verbose_name='按钮名称',
        help_text='按钮名称',
        max_length=100
    )
    control_panel = models.ForeignKey(
        ControlPanel,
        related_name='buttons',
        verbose_name='操控面板',
        help_text='操控面板',
        on_delete=models.CASCADE,
    )
    button_type = models.CharField(
        verbose_name='按钮类型',
        help_text='按钮类型',
        choices=BUTTON_TYPE_,
        max_length=20,
    )
    scene = models.ForeignKey(
        SceneConfig,
        verbose_name='智能场景',
        help_text='智能场景',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    command = models.ForeignKey(
        Command,
        verbose_name='命令实例',
        help_text='命令实例',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    device = models.ForeignKey(
        Device,
        verbose_name='设备',
        help_text='设备',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    attr = models.ForeignKey(
        DeviceCategoryAttrs,
        verbose_name='设备属性',
        help_text='设备属性',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    password = models.CharField(
        verbose_name='按钮口令',
        help_text='按钮口令',
        max_length=64,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        help_text='是否启用',
        default=True
    )
    ordering = models.PositiveBigIntegerField(
        verbose_name='分组排序',
        help_text='分组排序',
        default=0
    )

    class Meta:
        verbose_name = '操控面板按钮'
        verbose_name_plural = verbose_name

