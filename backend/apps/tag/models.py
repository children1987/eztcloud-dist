from django.conf import settings
from django.db import models

from backend.apps.users.models import Projects


logger = settings.LOGGER


class Tag(models.Model):
    """
    tag将被用来标记其它资源，一个资源的key仅允许标记一个value
    """
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, blank=True, null=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.key}: {self.value}'

    class Meta:
        # 在一个项目下，key+value唯一
        unique_together = ('project', 'key', 'value')
        ordering = ['key', 'value']
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    @classmethod
    def add_tags(cls, project_key: str, tags: list):
        """
        批量添加tag
        :param project_key: str, 项目的key
        :param tags: list, [{ 'key': 'key1', 'value': 'value1'}, ...]key为tag的key，value为tag的value
        :return: {
            'total': int, 添加的tag总数
            'success': int, 添加成功的tag数量
            'results': [
                {
                    'key': 'key1',
                    'value': 'value1',
                    'success': False,
                    'detail': 'tag已存在'
                },
                ...
            ]
        }
        """
        # 输入验证
        if not isinstance(project_key, str) or not isinstance(tags, list):
            raise ValueError("项目key必须是字符串，tags必须是数组")

        try:
            project = Projects.objects.get(pk=project_key)
        except Projects.DoesNotExist:
            logger.error(f"项目 {project_key} 不存在")
            raise ValueError(f"项目 {project_key} 不存在")

        total = len(tags)
        success = 0
        results = []

        for tag_info in tags:
            key, value = tag_info.get('key'), tag_info.get('value')
            try:
                cls.objects.create(project=project, key=key, value=value)
            except Exception as e:
                logger.error(f"插入标签失败(key={key}, value={value}): {str(e)}")
                results.append({
                    'key': key,
                    'value': value,
                    'success': False,
                    'detail': str(e)
                })
                continue
            success += 1
            results.append({
                'key': key,
                'value': value,
                'success': True,
                'detail': ''
            })
        return {
            'total': total,
            'success': success,
            'results': results
        }
