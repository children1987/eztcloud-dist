from django.contrib.auth import get_user_model
from django.db import models

from backend.apps.custom_servers.models import Domain

User = get_user_model()


class WechatUser(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    service_account_openid = models.CharField(
        max_length=64,
        verbose_name="微信服务号openid",
        default=None,
        null=True,
        blank=True,
    )

    domain = models.ForeignKey(
        Domain,
        help_text='服务域名',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )

    unionid = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="微信开放平台unionid",
    )

    class Meta:
        unique_together = (
            ('user', 'domain', ),
        )


class WeappUser(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    openid = models.CharField(
        max_length=64,
        verbose_name="微信小程序openid",
    )

    domain = models.ForeignKey(
        Domain,
        help_text='服务域名',
        on_delete=models.CASCADE,
        default=None
    )

    class Meta:
        unique_together = (
            ('user', 'domain', ),
        )
