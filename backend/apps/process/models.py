import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation, \
    GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

User = get_user_model()


class CommonApproveRecord(models.Model):
    """
    通用审批记录
    """
    APPROVAL_TYPE_ = (
        ('10', '发起'),
        ('20', '审批'),
        ('30', '转交'),
    )

    approver = models.ForeignKey(
        User, verbose_name='审批人', on_delete=models.PROTECT, help_text='审批人')
    result = models.BooleanField(verbose_name='审批结果', null=True,
                                 help_text='审批结果')
    node_id = models.SmallIntegerField(verbose_name='审批节点', default=0,
                                       help_text='审批节点')
    remark = models.CharField(verbose_name='审批意见', max_length=100,
                              help_text='审批意见',
                              null=True, blank=True)
    type = models.CharField(
        verbose_name='审批类型', max_length=10, help_text='审批类型',
        choices=APPROVAL_TYPE_, default='20')
    created_time = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now, help_text='创建时间')
    approve_time = models.DateTimeField(
        verbose_name='审批时间', null=True, blank=True, help_text='审批时间')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     help_text='审批内容类型')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = '通用审批记录'
        verbose_name_plural = verbose_name


class AbstractProcess(models.Model):
    """
    流程基类
    """
    PROCESS_CLASS = None

    STATES = (
        ('un_submit', '待发起'),
        ('approving', '审批中'),
        ('pass', '已通过'),
        ('refused', '已驳回'),
    )

    creator = models.ForeignKey(
        User, verbose_name='创建人', on_delete=models.PROTECT,
        related_name="%(class)s_creator", help_text='创建人')
    created_time = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now, help_text='创建时间')
    cur_approvers = models.ManyToManyField(
        User, verbose_name='当前审批人列表', related_name='%(class)s_approvers',
        help_text='当前审批人列表')
    cur_node_id = models.SmallIntegerField(verbose_name='当前审批节点',
                                           default=0, help_text='当前审批节点')
    records = GenericRelation(
        CommonApproveRecord, related_query_name='%(class)s_records',
        help_text='审批记录')
    state = models.CharField(verbose_name='状态', max_length=20,
                             default='approving', choices=STATES,
                             help_text='状态')
    is_deleted = models.BooleanField(verbose_name='是否已删除', default=False)

    def handle_approve(self, result, remark, user, callback=None,
                       *args, **kwargs):
        """
        处理审批
        """
        # 1. 创建审批记录
        record = CommonApproveRecord()
        record.approver = user
        record.node_id = self.cur_node_id
        record.result = result
        record.remark = remark
        record.content_object = self
        record.approve_time = datetime.datetime.now()
        record.save()

        # 1.1. 如果为拒绝，则直接删除当前审批人列表，更新审批状态，直接结束
        if not result:
            self.cur_approvers.clear()
            self.state = 'refused'
            self.cur_node_id = -1
            self.save()
            return True

        # 2. 删除当前审批人中的人员
        self.cur_approvers.remove(user)

        # 3. 获取当前节点信息，判断如果是或签，则直接进入下一个审批节点
        proc = self.PROCESS_CLASS(
            creator=self.creator, cur_node_id=self.cur_node_id, record=self)
        node_info = proc.get_node_info(self.cur_node_id)
        if node_info.get('approveType') == 'and' and self.cur_approvers.count():
            pass
        else:
            next_node = proc.get_next_node(self.cur_node_id)
            self.cur_approvers.clear()

            # 判断流程是否结束
            if next_node['nodeType'] == 'end':  # 流程结束
                self.state = 'pass'
                self.cur_node_id = -1
                self.pass_time = datetime.datetime.now()

                # 流程结束后，调用回调函数
                if callable(callback):
                    callback(*args, **kwargs)
            else:
                users = next_node['approvers']
                node_id = next_node['nodeId']
                self.cur_node_id = node_id
                if users:
                    self.cur_approvers.add(*users)
                else:  # 未找到审批人
                    # todo: 需要单独适配一个方法
                    self.cur_approvers.add(
                        *self.handle_no_approvers())
            self.save()
        return True

    def handle_no_approvers(self):
        return User.objects.filter(is_superuser=True)

    def set_next_approvers(self):
        creator = self.creator
        proc = self.PROCESS_CLASS(creator=creator, record=self)
        node = proc.get_next_node(0)
        users = node.get('approvers')
        node_id = node['nodeId']
        self.cur_node_id = node_id
        if users:
            self.cur_approvers.add(*users)
        else:  # 未找到审批人
            self.cur_approvers.add(*User.objects.filter(is_superuser=True))
        self.save()

    class Meta:
        abstract = True
