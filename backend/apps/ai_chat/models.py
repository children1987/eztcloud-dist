from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatSession(models.Model):

    class Meta:
        verbose_name = 'AI聊天-会话'
        verbose_name_plural = verbose_name

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    session_id = models.CharField(max_length=255, unique=True, verbose_name='会话ID')
    title = models.CharField(max_length=255, blank=True, verbose_name='会话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')

    def __str__(self):
        return f"{self.user.username} - {self.title or self.session_id}"


class ChatMessage(models.Model):

    class Meta:
        verbose_name = 'AI聊天-消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    MESSAGE_TYPE_CHOICES = [
        ('user', '用户消息'),
        ('assistant', '助手消息'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='会话')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.session.title} - {self.message_type} - {self.content[:50]}"
