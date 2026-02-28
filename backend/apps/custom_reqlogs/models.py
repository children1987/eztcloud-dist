from django.db import models
from django.conf import settings
from backend.apps.users.models import User, Projects
from psqlextra.types import PostgresPartitioningMethod
from psqlextra.models import PostgresPartitionedModel


class CustomRequestLogs(PostgresPartitionedModel):
    """
    请求日志
    """

    # 用于 pgmakemigrations 命令
    # pgmakemigrations 命令创建了一个 migration 文件，这个迁移文件包含：
    # 创建分表的总表(可把它理解为一个分表的路由，实际不能存储任何数据) 和
    # 一个 {app}_{model}_default 表(正常情况下应保持为空表)
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["id"]

    # 用于 check_db_partition 命令
    # check_db_partition 命令检查是否应该创建新的分表，并在需要时创建新的分表
    custom_partitioned = {
        "column": "id",
        "size": settings.PARTITIONS_RECORD_CNT,
    }

    action_name = models.CharField(
        verbose_name='请求内容',
        default='',
        max_length=50,
        db_index=True
    )
    project = models.ForeignKey(
        Projects,
        verbose_name="项目",
        help_text="项目",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    execution_time = models.CharField(
        verbose_name='耗时',
        max_length=50
    )
    timestamp = models.DateTimeField(
        verbose_name='请求时间'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='客户端ip',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        verbose_name='请求人',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    request_method = models.CharField(
        verbose_name='请求方式',
        max_length=20
    )
    full_path = models.TextField(
        verbose_name='请求地址',
        null=True,
        blank=True
    )
    query_params = models.TextField(
        verbose_name='请求参数',
        null=True,
        blank=True
    )
    data = models.TextField(
        verbose_name='请求体',
        null=True,
        blank=True
    )
    res_code = models.IntegerField(
        verbose_name='响应code',
        null=True,
        blank=True
    )
    res_data = models.TextField(
        verbose_name='返回数据',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = '请求操作日志'
        verbose_name_plural = verbose_name
