from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from backend.apps.equipments.models import DeviceCategory, Device
from backend.apps.users.models import Projects

User = get_user_model()


class OtaConfig(models.Model):
    """
    OTA升级版本配置
    """

    project = models.ForeignKey(
        Projects,
        related_name='project_ota_cfgs',
        verbose_name='项目',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='版本名称',
        help_text='版本名称',
        max_length=100,
        null=True,
        blank=True,
    )
    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='category_ota_cfgs',
        verbose_name='所属设备类型',
        on_delete=models.CASCADE
    )
    version = models.CharField(
        verbose_name='版本号',
        help_text='version',
        max_length=20
    )
    module = models.CharField(
        verbose_name='所属模块',
        help_text='所属模块',
        max_length=60,
        default='main'
    )
    use_https = models.BooleanField(
        verbose_name='是否使用https',
        help_text='是否使用https',
        default=False
    )
    use_source_versions = models.BooleanField(
        verbose_name='是否指定待升级版本',
        help_text='是否指定待升级版本',
        default=False
    )
    source_versions = models.JSONField(
        verbose_name='待升级版本号列表',
        help_text='待升级版本号列表',
        null=True,
        blank=True,
    )
    use_source_devices = models.BooleanField(
        verbose_name='是否指定待升级设备',
        help_text='是否指定待升级设备',
        default=False
    )
    source_devices = models.ManyToManyField(
        Device,
        through='OtaDevice',
        verbose_name='待升级设备',
        help_text='待升级设备',
    )
    file_url = models.TextField(
        verbose_name='文件路径',
        help_text='文件路径',
    )
    file_size = models.IntegerField(
        verbose_name='文件大小',
        help_text='文件大小',
        default=0
    )
    file_md5 = models.CharField(
        verbose_name='文件md5',
        help_text='文件md5',
        max_length=64,
        default=''
    )
    desc = models.TextField(
        verbose_name='描述',
        help_text='描述',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name='是否启用', default=True)
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
        verbose_name = 'OTA升级版本配置'
        verbose_name_plural = verbose_name

    def get_full_url(self):
        """
        获取 完整的url
        :return:
        """
        file_url = 'media/uploads' + self.file_url.split('?q-sign-algorithm')[0].split('media/uploads')[-1]
        if hasattr(settings, 'COS_URL'):
            base_url = settings.COS_URL
        else:
            base_url = settings.BASE_URL
        if not base_url.endswith('/'):
            base_url += '/'
        full_url = base_url + file_url
        if full_url.startswith('http'):
            if self.use_https:
                full_url = full_url.replace('http://', 'https://')
            else:
                full_url = full_url.replace('https://', 'http://')
        else:
            if self.use_https:
                full_url = 'https://' + full_url
            else:
                full_url = 'http://' + full_url
        return full_url



class OtaDevice(models.Model):
    """
    OTA指定升级设备
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    ota_cfg = models.ForeignKey(OtaConfig, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'OTA升级版本配置'
        verbose_name_plural = verbose_name