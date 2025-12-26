from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from backend.apps.users.models import Projects

User = get_user_model()


class EzvizConfig(models.Model):
    """萤石云配置"""
    
    REGION_CHOICES = (
        ('china', '中国大陆'),
        ('europe', '欧洲'),
        ('north_america', '北美'),
        ('south_america', '南美'),
        ('singapore', '新加坡'),
        ('india', '印度'),
        ('russia', '俄罗斯'),
    )
    
    project = models.OneToOneField(
        Projects,
        on_delete=models.CASCADE,
        verbose_name='项目',
        help_text='项目'
    )
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        verbose_name='区域',
        help_text='萤石云服务区域'
    )
    app_key = models.CharField(
        max_length=32,
        verbose_name='AppKey',
        help_text='萤石云应用Key'
    )
    secret = models.CharField(
        max_length=32,
        verbose_name='Secret',
        help_text='萤石云应用密钥'
    )
    last_test_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后测试时间',
        help_text='最后测试连接时间'
    )
    product_code = models.CharField(
        max_length=50,
        verbose_name='产品识别码',
        help_text='萤石云摄像头产品识别码'
    )
    webhook_secret = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Webhook签名密钥',
        help_text='用于验证Webhook回调的签名密钥'
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='创建时间'
    )
    updated_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='更新时间'
    )
    
    class Meta:
        verbose_name = '萤石云配置'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f'{self.project.name} - {self.get_region_display()}'


class CameraAlarm(models.Model):
    """视频通道告警记录"""
    
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        verbose_name='项目',
        help_text='所属项目'
    )
    device_serial = models.CharField(
        max_length=32,
        verbose_name='设备序列号',
        help_text='设备序列号'
    )
    alarm_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='告警ID',
        help_text='告警ID'
    )
    channel = models.IntegerField(
        verbose_name='通道',
        help_text='通道'
    )
    channel_type = models.IntegerField(
        verbose_name='通道类型',
        help_text='通道类型'
    )
    alarm_type = models.CharField(
        max_length=50,
        verbose_name='告警类型',
        help_text='告警类型'
    )
    relation_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='关联ID',
        help_text='关联ID'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='位置',
        help_text='位置'
    )
    describe = models.TextField(
        blank=True,
        verbose_name='描述',
        help_text='描述'
    )
    alarm_time = models.DateTimeField(
        verbose_name='告警时间',
        help_text='告警时间'
    )
    custom_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='自定义类型',
        help_text='自定义类型'
    )
    request_time = models.BigIntegerField(
        verbose_name='请求时间',
        help_text='请求时间戳'
    )
    channel_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='通道名称',
        help_text='通道名称'
    )
    checksum = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='校验和',
        help_text='校验和'
    )
    crypt = models.IntegerField(
        default=0,
        verbose_name='加密',
        help_text='加密标识'
    )
    custom_info = models.TextField(
        blank=True,
        verbose_name='自定义信息',
        help_text='自定义信息'
    )
    picture_list = models.JSONField(
        default=list,
        verbose_name='图片列表',
        help_text='图片列表'
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='创建时间'
    )
    
    class Meta:
        verbose_name = '视频通道告警记录'
        verbose_name_plural = verbose_name
        ordering = ['-alarm_time']
        
    def __str__(self):
        return f'{self.device_serial} - {self.alarm_type} - {self.alarm_time}'
