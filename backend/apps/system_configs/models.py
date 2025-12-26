from django.db import models


class SystemConfig(models.Model):
    key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='配置键',
        help_text='配置键，例如 auth_code',
    )
    value = models.TextField(
        verbose_name='配置值',
        help_text='配置值内容，auth_code 等',
        null=True,
        blank=True,
    )
    updated_time = models.DateTimeField(
        auto_now=True,
        verbose_name='最后修改时间',
        help_text='最后修改时间',
    )

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.key


