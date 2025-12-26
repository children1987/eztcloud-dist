import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone

from backend.apps.common.fields import CharNullField
from backend.apps.common.models import BaseModel
from backend.apps.proj_common.const import USER_LEVEL_
from backend.apps.areas.models import Area


class User(AbstractUser):

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    nickname = models.CharField(
        verbose_name='中文名',
        help_text='中文名',
        max_length=50,
        default='匿名',
    )
    mobile = CharNullField(
        verbose_name='手机号',
        help_text='手机号',
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )
    email = CharNullField(
        verbose_name='邮箱',
        help_text='邮箱',
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )

    avatar = models.TextField(
        verbose_name="用户头像",
        help_text="用户头像",
        null=True,
        blank=True,
    )
    remark = models.TextField(
        verbose_name="备注",
        help_text="备注",
        null=True,
        blank=True,
    )
    address = models.CharField(
        verbose_name="地址",
        help_text="地址",
        max_length=150,
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        'self',
        related_name='created_users',
        verbose_name="创建者",
        help_text="创建者",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_sys = models.BooleanField(
        verbose_name='是否系统内用户',
        help_text="是否系统内用户",
        default=True,
    )
    is_deleted = models.BooleanField(
        verbose_name='是否已删除',
        help_text="是否已删除",
        default=False,
    )
    token = models.CharField(
        help_text="机器用户可基于token访问API",
        max_length=64,
        null=True,
        blank=True
    )

    default_project = models.ForeignKey(
        to='Projects',
        verbose_name='默认项目',
        help_text="移动端用户默认项目",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    default_city = models.ForeignKey(
        to=Area,
        help_text="默认城市",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    uuid = models.UUIDField(
        verbose_name='UUID',
        help_text='跨系统用户关联的唯一标识',
        unique=True,        # 重新启用唯一约束
        default=uuid.uuid4, # 恢复默认值
        null=False,         # 禁止空值
        blank=False,        # 禁止表单空白
    )
    last_updated = models.DateTimeField(
        verbose_name='最后更新时间',
        help_text='记录用户信息最后修改时间',
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self):
        return self.nickname
    
    @property
    def masked_mobile(self):
        """
        返回脱敏后的手机号，格式如：189****6586
        """
        if not self.mobile:
            return None
        
        mobile = str(self.mobile)
        if len(mobile) < 7:
            return mobile  # 如果手机号长度不足7位，直接返回原值
        
        # 保留前3位和后4位，中间用*替换
        return mobile[:3] + '****' + mobile[-4:]
    
    @property
    def masked_email(self):
        """
        返回脱敏后的邮箱，格式如：abc****@example.com
        """
        if not self.email:
            return None
        
        email = str(self.email)
        if '@' not in email:
            return email  # 如果不是有效的邮箱格式，直接返回原值
        
        # 分割用户名和域名
        username, domain = email.split('@', 1)
        
        if len(username) <= 2:
            # 如果用户名长度小于等于2，只显示第一个字符
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            # 保留前2位和后1位，中间用*替换
            masked_username = username[:2] + '*' * (len(username) - 3) + username[-1]
        
        return f"{masked_username}@{domain}"


class Projects(models.Model):

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name

    id = models.CharField(
        primary_key=True,
        help_text='通常以"PR_"开头，如"PR_xxxxxxxxxx',
        max_length=30
    )
    name = models.CharField(
        verbose_name='项目名称',
        help_text="项目名称",
        max_length=100,
        default='尚未命名',
    )
    monitor_screen_params = models.JSONField(
        verbose_name='看板参数',
        help_text='不同的看板模板，其参数结构不同，前端自存自取',
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='项目描述',
        help_text="项目描述",
        null=True,
        blank=True,
    )
    project_password = models.CharField(
        verbose_name='ProjectSecret',
        help_text='项目连接秘钥',
        max_length=100,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        help_text='是否启用',
        default=True,
    )
    creator = models.ForeignKey(
        User,
        verbose_name="创建人",
        help_text="创建人",
        on_delete=models.PROTECT,
        null=True
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
    is_open_mqtt = models.BooleanField(
        verbose_name='是否开启open mqtt 推送',
        help_text="是否开启open mqtt 推送",
        default=False,
    )
    bucket_id = models.CharField(
        verbose_name='bucket_id',
        help_text="时序数据库中的bucket的id",
        max_length=32,
        null=True,
        blank=True,
        default=None
    )
    bucket_disk_usage = models.IntegerField(
        verbose_name="硬盘使用量（MB）",
        help_text="硬盘使用量（MB）",
        null=True,
        blank=True,
        default=None
    )
    auth_code = models.TextField(
        verbose_name='项目授权码',
        help_text='项目授权码（明文+签名的JSON字符串）',
        null=True,
        blank=True,
        default=None
    )
    bucket_disk_usage_time = models.DateTimeField(
        verbose_name="硬盘使用量更新时间",
        help_text="硬盘使用量更新时间",
        null=True,
        blank=True,
        default=None
    )
    ordering = models.IntegerField(
        verbose_name='项目排序',
        help_text="对自己创建的项目排序",
        default=0,
    )

    def get_member_count(self):
        return self.project_members.filter(is_deleted=False).count()
    get_member_count.short_description = '成员数量'

    def get_device_count(self):
        return self.project_device.filter(is_deleted=False).count()
    get_device_count.short_description = '设备数量'

    def __str__(self):
        return self.name


class ProjectMembers(models.Model):

    class Meta:
        verbose_name = '项目成员'
        verbose_name_plural = verbose_name
        unique_together = ('project', 'user')

    user = models.ForeignKey(
        User,
        related_name='user_members',
        verbose_name="项目成员",
        help_text="项目成员",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        Projects,
        related_name='project_members',
        verbose_name="项目",
        help_text="项目",
        on_delete=models.CASCADE,
    )
    project_ordering = models.IntegerField(
        verbose_name='用户项目排序',
        help_text="用户项目排序",
        default=0,
    )
    level = models.IntegerField(
        verbose_name='权限级别',
        help_text="权限级别",
        choices=USER_LEVEL_,
        default=10,
    )
    desc = models.TextField(
        verbose_name='描述',
        help_text="描述",
        null=True,
        blank=True,
    )
    is_join_project = models.BooleanField(
        verbose_name='是否加入项目',
        default=False,
    )
    creator = models.ForeignKey(
        User,
        related_name='project_users',
        verbose_name="项目成员记录创建人",
        help_text="项目成员记录创建人",
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
        verbose_name='是否从项目中移除',
        help_text="是否从项目中移除",
        default=False,
    )


class DeviceGroups(BaseModel):

    class Meta:
        verbose_name = '设备组'
        verbose_name_plural = verbose_name

    project = models.ForeignKey(
        Projects,
        related_name='project_units',
        verbose_name='所属项目',
        help_text='所属组织',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(
        verbose_name='设备组名称',
        help_text="设备组名称",
        max_length=100,
    )
    order = models.IntegerField(
        verbose_name='序号',
        help_text='序号',
        default=0,
    )
    is_deleted = models.BooleanField(
        verbose_name='是否已删除',
        help_text="是否已删除",
        default=False,
    )

    desc = models.TextField(
        verbose_name='设备分组描述信息',
        help_text='设备分组描述信息',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
