from django.db import models

from backend.apps.users.models import User


class CustomRequestLogs(models.Model):
    """
    请求日志
    todo: 考虑按年度分表
    """
    action_name = models.CharField(
        verbose_name='请求内容', default='', max_length=50, db_index=True)
    execution_time = models.CharField(
        verbose_name='耗时', max_length=50)
    timestamp = models.DateTimeField(verbose_name='请求时间')
    ip_address = models.GenericIPAddressField(verbose_name='客户端ip')
    user = models.ForeignKey(User, verbose_name='请求人',
                             on_delete=models.CASCADE, null=True, blank=True)
    request_method = models.CharField(verbose_name='请求方式', max_length=20)
    full_path = models.TextField(verbose_name='请求地址')
    query_params = models.TextField(verbose_name='请求参数')
    data = models.TextField(verbose_name='请求体')
    res_code = models.IntegerField(verbose_name='响应code', null=True, blank=True)
    res_data = models.CharField(verbose_name='返回数据', max_length=500,
                                null=True, blank=True)

    class Meta:
        verbose_name = '请求操作日志'
        verbose_name_plural = verbose_name
