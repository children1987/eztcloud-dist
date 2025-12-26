from django.db import models
from django.utils import timezone
from backend.apps.common.models import BaseModel
from backend.apps.proj_common.const import DEVICE_NODE_TYPE, GATEWAY_TYPE_, \
    QUOTE_PRODUCT_TYPE, ACCESS_PROTOCOL_, NET_TYPE_, DATA_STREAM_FORMAT, \
    ATTR_TYPE, DATA_TYPE, DEVICE_ORIGIN
from backend.apps.users.models import Projects, User, DeviceGroups, ProjectMembers


class ManufacturerInfo(models.Model):
    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = verbose_name

    name = models.CharField(
        verbose_name='名称',
        help_text='厂商名称',
        max_length=60,
        unique=True
    )
    code = models.CharField(
        verbose_name='厂商识别码',
        help_text='如："ibm", "apple"',
        max_length=30,
        unique=True,
        null=True,
        default=None
    )
    remark = models.TextField(
        verbose_name='备注说明',
        help_text='备注说明',
        null=True,
        blank=True,
    )
    logo = models.TextField(
        verbose_name='厂商logo',
        help_text='厂商logo',
        null=True,
        blank=True,
    )
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

    def __str__(self):
        return self.name


class ManufacturerUser(models.Model):
    P_LEVEL_ = (
        (10, '拥有者'),
        (20, '管理员'),
        (30, '应用用户'),
    )

    manufacturer = models.ForeignKey(
        ManufacturerInfo,
        related_name='mf_users',
        verbose_name='厂商',
        help_text='厂商',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='user_manufacturers',
        verbose_name='厂商成员',
        on_delete=models.CASCADE
    )
    created_time = models.DateTimeField(
        verbose_name="创建时间",
        help_text="创建时间",
        default=timezone.now,
    )
    level = models.IntegerField(
        verbose_name='权限级别',
        help_text="权限级别",
        choices=P_LEVEL_,
        default=10,
    )
    desc = models.TextField(
        verbose_name='描述',
        help_text="描述",
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        User,
        related_name='create_mf_users',
        verbose_name="项目成员邀请人",
        help_text="项目成员邀请人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = '厂商成员'
        verbose_name_plural = verbose_name
        unique_together = ('manufacturer', 'user')


class FixedProduct(models.Model):

    class Meta:
        verbose_name = '公共产品'
        verbose_name_plural = verbose_name

    PUBLISH_STATE_ = (
        ('unpublished', '未发布'),
        ('published', '已发布'),
        ('recalled', '已撤回'),
    )

    code = models.CharField(
        verbose_name='产品识别码',
        max_length=200,
        unique=True,
        default=None,
        null=True,
        help_text='形如: company.product.specification.version'
    )
    key = models.CharField(
        verbose_name='产品Key',
        max_length=20,  # 目前实际使用8个字符
        default=None,
        unique=True,
        help_text='与“产品识别码”功能相同，由系统自动生成，不可修改，形如: PK_Ab123'
    )
    name = models.CharField(
        verbose_name='产品名称',
        help_text='产品名称',
        null=True,
        blank=True,
        max_length=60
    )
    model = models.CharField(
        verbose_name='产品型号',
        help_text='产品型号',
        null=True,
        blank=True,
        max_length=50
    )
    version = models.CharField(
        verbose_name='版本号',
        help_text='版本号',
        null=True,
        blank=True,
        max_length=20
    )
    trade_name = models.CharField(
        verbose_name='厂商名称',
        help_text='厂商名称',
        null=True,
        blank=True,
        max_length=20
    )
    manufacturer = models.ForeignKey(
        ManufacturerInfo,
        related_name='mf_fixed_products',
        verbose_name='厂商',
        help_text='厂商',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    conf = models.JSONField(
        verbose_name='设备类型相关的全量配置信息',
        help_text='设备类型相关的全量配置信息',
    )
    remark = models.TextField(
        verbose_name='备注说明',
        help_text='备注说明',
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(
        verbose_name='是否已发布',
        help_text='是否已发布',
        default=True
    )
    publish_state = models.CharField(
        verbose_name='发布状态',
        help_text='发布状态',
        max_length=20,
        choices=PUBLISH_STATE_,
        default='published'
    )
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


class FixedProductFiles(models.Model):

    class Meta:
        verbose_name = "公共产品文档"
        verbose_name_plural = verbose_name

    f_product = models.ForeignKey(
        FixedProduct,
        verbose_name='产品类型',
        related_name='fixed_product_files',
        on_delete=models.CASCADE,
        help_text='产品类型'
    )
    file_path = models.TextField(
        verbose_name='文件路径',
        help_text='文件路径',
    )
    created_time = models.DateTimeField(
        verbose_name='创建时间',
        help_text='创建时间',
        default=timezone.now
    )
    file_info = models.JSONField(
        verbose_name='文件信息',
        help_text='文件信息',
        null=True,
        blank=True,
    )


class DeviceCategory(models.Model):
    """
    设备类型
    """

    project = models.ForeignKey(
        Projects,
        related_name='project_device_category',
        on_delete=models.CASCADE,
        verbose_name='项目',
        help_text='项目',
        null=True,
        blank=True,
    )
    name = models.CharField(
        verbose_name='设备类型名称',
        help_text='设备类型名称',
        max_length=100,
        null=True,
        blank=True,
    )
    key = models.CharField(
        verbose_name='设备类型唯一标识',
        help_text='设备类型唯一标识：以"DC_XXX"开头，如"DC_NRXse678"',
        max_length=16,
        unique=True,
        null=True,
        blank=True
    )
    desc = models.TextField(
        verbose_name='设备类型描述',
        help_text='设备类型描述',
        null=True,
        blank=True,
    )
    quote_product = models.CharField(
        verbose_name='类型分类',
        help_text='类型分类',
        choices=QUOTE_PRODUCT_TYPE,
        default='S',
        max_length=20,
    )
    node_type = models.CharField(
        verbose_name='设备接入类型',
        help_text='设备接入类型',
        choices=DEVICE_NODE_TYPE,
        max_length=20,
    )
    version = models.CharField(
        verbose_name='版本号',
        help_text='版本号',
        max_length=10,
        default='v1'
    )
    access_protocol = models.CharField(
        verbose_name='设备接入协议',
        help_text='设备接入协议',
        choices=ACCESS_PROTOCOL_,
        max_length=30,
        null=True,
        blank=True,
    )
    net_type = models.CharField(
        verbose_name='设备通信方式',
        help_text='设备通信方式',
        choices=NET_TYPE_,
        max_length=50,
        null=True,
        blank=True,
    )
    cfg_info = models.JSONField(
        verbose_name='配置信息',
        help_text='配置信息',
        null=True,
        blank=True,
    )
    other_info = models.JSONField(
        verbose_name='扩展信息',
        help_text='扩展信息',
        null=True,
        blank=True,
    )
    conn_cfg = models.TextField(
        verbose_name='连接信息',
        help_text='连接信息',
        null=True,
        blank=True,
    )
    scene_action = models.BooleanField(
        verbose_name='是否参与场景动作',
        help_text="是否参与场景动作",
        default=False,
    )
    scene_condition = models.BooleanField(
        verbose_name='是否参与场景条件',
        help_text="是否参与场景条件",
        default=False,
    )
    online_delay_time = models.IntegerField(
        verbose_name='设备在线延迟时间',
        help_text='设备在线延迟时间',
        default=300,
        null=True,
        blank=True,
    )
    alive_delay_time = models.IntegerField(
        verbose_name='设备活跃延迟时间',
        help_text='设备活跃延迟时间',
        default=300,
    )
    logo = models.ImageField(
        verbose_name='设备类型logo',
        help_text='设备类型logo',
        null=True,
        blank=True,
    )
    f_product = models.ForeignKey(
        FixedProduct,
        verbose_name='产品类型',
        related_name='fixed_product_categorise',
        on_delete=models.SET_NULL,
        help_text='当产品类型quote_product为产品类型（P）时，必传',
        max_length=20,
        null=True,
        blank=True,
    )
    down_interval = models.IntegerField(
        verbose_name='下发间隔',
        help_text="下发间隔",
        null=True,
        blank=True,
        default=2000
    )
    communication_waiting_time = models.IntegerField(
        verbose_name='通讯等待时间',
        help_text="通讯等待时间",
        null=True,
        blank=True,
        default=30000
    )
    timout_retry_count = models.PositiveIntegerField(
        verbose_name="超时重发次数",
        help_text="超时重发次数",
        null=True,
        blank=True,
        default=2
    )
    tag_conf = models.JSONField(
        verbose_name='标签',
        help_text='标签',
        null=True,
        blank=True,
    )
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
    ignore_disconnection = models.BooleanField(
        verbose_name='是否忽略设备链路断开',
        help_text="是否忽略设备链路断开",
        default=False,
    )
    is_send_response = models.BooleanField(
        verbose_name='是否接收响应',
        help_text="是否接收响应",
        default=False,
    )
    is_auto_create = models.BooleanField(
        verbose_name='是否允许自动创建设备',
        help_text="是否允许自动创建设备",
        default=True,
    )
    is_deleted = models.BooleanField(
        verbose_name='是否已删除',
        help_text="是否已删除",
        default=False,
    )
    ui_params = models.JSONField(
        verbose_name='个性化UI',
        help_text='json字符串。包含个性化UI标识（如“UK_xxxxxxxxxx”）及相关配置信息',
        null=True,
        blank=True,
    )
    online_cfg = models.JSONField(
        verbose_name='设备在线状态基于属性配置',
        help_text='设备在线状态基于属性配置{"attr_key": "state", "attr_value": 1, "attr_type": "N"}',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = '设备类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.id}-{self.key}-{self.name}'


class TcpRegistFrame(models.Model):
    class Meta:
        verbose_name = 'TCP注册帧'
        verbose_name_plural = verbose_name
    
    key = models.CharField(
        verbose_name='注册帧标识符',
        help_text='注册帧标识符',
        max_length=20,
    )
    device_category = models.OneToOneField(
        DeviceCategory,
        related_name='tcp_register_frame',
        null=False,
        blank=False,
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE,
    )


class DeviceCategoryCommands(models.Model):
    """
    设备类型-命令
    """

    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='commands',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='命令名称',
        help_text='命令名称',
        max_length=100,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='命令描述',
        help_text="命令描述",
        null=True,
        blank=True,
    )
    key = models.CharField(
        verbose_name='命令标识符',
        help_text='命令标识符',
        max_length=100
    )

    request_params = models.JSONField(
        verbose_name='命令参数',
        help_text='命令参数',
        null=True,
        blank=True,
    )

    response_params = models.JSONField(
        verbose_name='命令回复参数',
        help_text='命令回复参数',
        null=True,
        blank=True,
    )

    order = models.IntegerField(
        verbose_name='序号',
        help_text='序号',
        default=1,
    )

    class Meta:
        verbose_name = '设备类型-命令'
        verbose_name_plural = verbose_name
        unique_together = ('device_category', 'key')


class Command(models.Model):
    """
    命令实例
    """

    instance_name = models.CharField(
        max_length=20,
        verbose_name='实例名称',
        help_text='实例名称',
    )

    category_command = models.ForeignKey(
        to='DeviceCategoryCommands',
        related_name='command_instance',
        verbose_name='设备类型命令',
        help_text='设备类型命令',
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        to='DeviceCategory',
        related_name='command_instance',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    device = models.ForeignKey(
        to='Device',
        related_name='command_instance',
        verbose_name='设备',
        help_text='设备',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    parameters = models.JSONField(
        verbose_name='命令实例内容',
        help_text='参数key和参数值组成的键值对'
    )

    device_origin = models.CharField(
        verbose_name='设备源类型',
        help_text='设备源类型',
        max_length=5,
        choices=DEVICE_ORIGIN
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = '命令实例'
        verbose_name_plural = verbose_name


class DeviceCategoryEvents(models.Model):
    """
    设备类型-事件
    """

    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='events',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='事件名称',
        help_text='事件名称',
        max_length=100,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='事件描述',
        help_text="事件描述",
        null=True,
        blank=True,
    )
    key = models.CharField(
        verbose_name='事件标识符',
        help_text='事件标识符',
        max_length=100
    )
    params = models.JSONField(
        verbose_name='事件参数',
        help_text='事件参数',
        null=True,
        blank=True,
    )
    order = models.IntegerField(
        verbose_name='序号',
        help_text='序号',
        default=1,
    )

    class Meta:
        verbose_name = '设备类型-事件'
        verbose_name_plural = verbose_name
        unique_together = ('device_category', 'key')


class DeviceCategoryAttrs(models.Model):
    """
    设备类型-属性
    """

    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='attrs',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='属性名称',
        help_text='属性名称',
        max_length=100,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='属性描述',
        help_text="属性描述",
        null=True,
        blank=True,
    )
    key = models.CharField(
        verbose_name='属性标识符',
        help_text='属性标识符',
        max_length=100
    )
    attr_type = models.CharField(
        verbose_name='属性类型',
        help_text='属性类型',
        max_length=50,
        choices=ATTR_TYPE,
        null=True,
        blank=True,
    )
    data_type = models.CharField(
        verbose_name='属性数据类型',
        help_text='属性数据类型',
        choices=DATA_TYPE,
        max_length=20,
    )
    is_manual_updated = models.BooleanField(
        verbose_name='是否可手动更新',
        help_text='是否可手动更新',
        default=False,
    )
    is_required = models.BooleanField(
        verbose_name='是否必要',
        help_text='设备可否弃用该属性',
        default=False,
    )
    is_show_app = models.BooleanField(
        verbose_name='是否在移动端展示',
        help_text="是否在移动端展示",
        default=True,
    )
    condition_info = models.JSONField(
        verbose_name='属性计算配置',
        help_text='属性计算配置',
        null=True,
        blank=True,
    )
    data_specs = models.JSONField(
        verbose_name='属性约束',
        help_text='属性约束',
        null=True,
        blank=True,
    )
    order = models.IntegerField(
        verbose_name='序号',
        help_text='序号',
        default=1,
    )

    attr_scene_action = models.BooleanField(
        verbose_name='是否参与场景动作',
        help_text="是否参与场景动作",
        default=True,
    )
    attr_scene_condition = models.BooleanField(
        verbose_name='是否参与场景条件',
        help_text="是否参与场景条件",
        default=True,
    )

    class Meta:
        verbose_name = '设备类型-属性'
        verbose_name_plural = verbose_name
        unique_together = ('device_category', 'key')


class DeviceCategoryAttrTemplates(models.Model):

    class Meta:
        verbose_name = '设备类型-属性模板'
        verbose_name_plural = verbose_name

    name = models.CharField(
        verbose_name='属性名称',
        help_text='属性名称',
        max_length=100,
        null=True,
        blank=True,
        unique=True,
    )
    desc = models.TextField(
        verbose_name='属性描述',
        help_text="属性描述",
        null=True,
        blank=True,
    )
    key = models.CharField(
        verbose_name='属性标识符',
        help_text='属性标识符',
        max_length=100
    )
    attr_type = models.CharField(
        verbose_name='属性类型',
        help_text='属性类型',
        max_length=50,
        choices=ATTR_TYPE,
        null=True,
        blank=True,
    )
    data_type = models.CharField(
        verbose_name='属性数据类型',
        help_text='属性数据类型',
        choices=DATA_TYPE,
        max_length=20,
    )
    data_specs = models.JSONField(
        verbose_name='属性约束',
        help_text='属性约束',
        null=True,
        blank=True,
    )
    attr_scene_action = models.BooleanField(
        verbose_name='是否参与场景动作',
        help_text="是否参与场景动作，上报属性必须设置为False",
        default=True,
    )
    attr_scene_condition = models.BooleanField(
        verbose_name='是否参与场景条件',
        help_text="是否参与场景条件，下发属性必须设置为False",
        default=True,
    )


class DeviceCategoryDataStream(models.Model):
    """
    设备类型-自定义数据流
    """
    TOPIC_TYPE_ = (
        ('parameter', '自定义参数'),
        ('mapping', 'topic映射'),
    )

    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='data_streams',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='数据流名称',
        help_text='数据流名称',
        max_length=100,
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='数据流描述',
        help_text="数据流描述",
        null=True,
        blank=True,
    )
    key = models.CharField(
        verbose_name='数据流标识符',
        help_text='数据流标识符',
        max_length=100,
    )
    data_type = models.CharField(
        verbose_name='消息格式',
        help_text='消息格式',
        choices=DATA_STREAM_FORMAT,
        max_length=20,
    )
    topic_mode = models.BooleanField(
        verbose_name='是否支持自定义topic',
        help_text='是否支持自定义topic',
        default=False,
    )
    topic_type = models.CharField(
        verbose_name='自定义Topic模式',
        help_text='自定义Topic模式',
        max_length=100,
        choices=TOPIC_TYPE_,
        db_index=True,
        null=True,
        blank=True,
    )
    publish_topic = models.CharField(
        verbose_name='发布 Topic',
        help_text='发布 Topic',
        max_length=100,
        null=True,
        blank=True,
    )
    subscribe_topic = models.CharField(
        verbose_name='订阅 Topic',
        help_text='订阅 Topic',
        max_length=100,
        null=True,
        blank=True,
    )
    publish_topic_key = models.CharField(
        verbose_name='高级模式发布Topic',
        help_text='高级模式发布Topic',
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
    )
    subscribe_topic_key = models.CharField(
        verbose_name='高级模式订阅Topic',
        help_text='高级模式订阅Topic',
        max_length=100,
        null=True,
        blank=True,
    )
    device_subscribe_topic = models.CharField(
        verbose_name='设备订阅Topic通配符',
        help_text='设备订阅需开放权限',
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
    )
    is_auth = models.BooleanField(
        verbose_name='topic权限是否认证',
        help_text='topic权限是否认证',
        default=True
    )
    bind_tcp = models.BooleanField(
        verbose_name='绑定tcp',
        help_text='绑定tcp',
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name='是否启用',
        default=True
    )
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
        verbose_name = '自定义数据流'
        verbose_name_plural = verbose_name
        unique_together = ('device_category', 'key')


class DeviceCategoryModBus(models.Model):
    """
    ModBus 配置
    """

    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='mod_bus_conf',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE
    )
    data_stream = models.ForeignKey(
        DeviceCategoryDataStream,
        verbose_name='自定义数据流',
        help_text='自定义数据流',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    down_publish_type = models.CharField(
        verbose_name='下发推送方式',
        help_text='下发推送方式',
        max_length=20,
        null=True,
        blank=True,
    )
    it_switch = models.BooleanField(
        verbose_name='智能属性切换',
        help_text='智能属性切换',
        default=True,
    )
    io_register = models.JSONField(
        verbose_name='io 寄存器设置',
        help_text='io 寄存器设置',
        null=True,
        blank=True,
    )
    data_register = models.JSONField(
        verbose_name='数据寄存器设置',
        help_text='数据寄存器设置',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'ModBus 配置'
        verbose_name_plural = verbose_name


class MQTTBroker(models.Model):
    """
    设备-MQTT连接ip,port
    """
    broker_address = models.CharField(max_length=100)
    broker_port = models.CharField(max_length=20)
    broker_port_tls = models.CharField(max_length=20)

    class Meta:
        verbose_name = '设备-MQTT连接信息'
        verbose_name_plural = verbose_name


class TCPServer(models.Model):
    """
    设备-TCP连接ip,port
    """
    address = models.CharField(max_length=100)
    port = models.CharField(max_length=20)

    class Meta:
        verbose_name = '设备-TCP连接信息'
        verbose_name_plural = verbose_name


class Device(BaseModel):
    """
    设备
    """

    project = models.ForeignKey(
        Projects,
        related_name='project_device',
        on_delete=models.CASCADE,
        verbose_name='项目',
        help_text='项目',
    )
    category = models.ForeignKey(
        DeviceCategory,
        related_name='category_devices',
        verbose_name="设备类型",
        help_text='设备类型',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    serial_id = models.CharField(
        max_length=64,
        verbose_name='设备序列号',
        help_text='在同一个设备类型下唯一',
        null=True,
        blank=True,
    )
    com_gateway = models.ForeignKey(
        'self',
        verbose_name='所属设备',
        help_text='所属设备',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    members = models.ManyToManyField(
        ProjectMembers,
        related_name='member_devices',
        verbose_name='设备用户',
    )
    name = models.CharField(
        verbose_name='设备名称',
        help_text='设备名称',
        max_length=100,
        default='尚未命名',
    )
    cfg_info = models.JSONField(
        verbose_name='设备配置参数',
        help_text='设备配置参数',
        null=True,
        blank=True,
    )
    exclude_attrs = models.JSONField(
        verbose_name='设备排除属性',
        help_text='设备排除属性',
        null=True,
        blank=True,
    )
    logo = models.ImageField(
        verbose_name='设备logo',
        help_text='设备logo',
        null=True,
        blank=True,
    )
    location = models.CharField(
        verbose_name='设备安裝位置',
        help_text='设备安裝位置',
        max_length=100,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="是否启用",
    )
    belong_unit = models.ForeignKey(
        DeviceGroups,
        related_name='unit_devices',
        verbose_name='所属单元',
        help_text='所属单元',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    unit_order = models.IntegerField(
        verbose_name='单元内序号',
        help_text='单元内序号',
        default=1,
    )
    creator = models.ForeignKey(
        User,
        verbose_name='创建人',
        help_text='创建人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # 设备连接信息
    conn_broker = models.ForeignKey(
        MQTTBroker,
        verbose_name='mqtt连接地址-端口',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    conn_tcp = models.ForeignKey(
        TCPServer,
        verbose_name='tcp连接地址-端口',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    username = models.CharField(
        verbose_name='设备连接名称',
        max_length=100,
        unique=True)

    qr = models.CharField(
        verbose_name='二维码标识',
        help_text='二维码标识：通常以"QR_"开头，如"QR_A250300001"',
        max_length=16,
        unique=True,
        null=True,
        blank=True
    )
    password = models.CharField(verbose_name='设备连接密码', max_length=50)
    client_id = models.CharField(verbose_name='设备连接client_id', max_length=100)
    code = models.CharField(
        verbose_name='子设备标识符',
        help_text='子设备标识符',
        max_length=50,
        null=True,
        blank=True
    )
    desc = models.TextField(
        verbose_name='设备描述',
        help_text='设备描述',
        null=True,
        blank=True,
    )
    is_record = models.BooleanField(
        verbose_name='设备调试消息日志按钮',
        help_text='设备调试消息日志按钮',
        default=False,
    )

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DeviceCommandRecords(models.Model):
    """
    设备命令记录
    """

    device = models.ForeignKey(
        Device,
        related_name='command_records',
        verbose_name='设备',
        help_text='设备',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='命令名称',
        help_text='命令名称',
        max_length=100
    )
    key = models.CharField(
        verbose_name='命令标识符',
        help_text='命令标识符',
        max_length=100
    )
    request_time = models.DateTimeField(
        verbose_name='命令下发时间',
        help_text='命令下发时间',
        null=True,
        blank=True,
    )
    request_content = models.TextField(
        verbose_name='命令下发内容',
        help_text='命令下发内容',
        null=True,
        blank=True,
    )
    response_time = models.DateTimeField(
        verbose_name='命令回复时间',
        help_text='命令回复时间',
        null=True,
        blank=True,
    )
    response_content = models.TextField(
        verbose_name='命令回复内容',
        help_text='命令回复内容',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = '设备命令记录'
        verbose_name_plural = verbose_name


class DeviceState(models.Model):
    """
    设备状态变化表
    """
    device = models.ForeignKey(
        Device,
        verbose_name='设备',
        help_text='设备',
        on_delete=models.CASCADE,
    )
    state = models.BooleanField(verbose_name='当前状态', help_text='当前状态')
    timestamp = models.DateTimeField(
        verbose_name='时间戳',
        default=timezone.now,
        db_index=True,
        help_text='时间',
    )

    class Meta:
        verbose_name = '设备状态变化表'
        verbose_name_plural = verbose_name


class OperatingRecord(models.Model):
    """
    设备操作记录
    """

    device = models.ForeignKey(
        Device,
        verbose_name='设备',
        help_text='设备',
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        verbose_name='操作描述',
        help_text='操作描述',
        null=True,
        blank=True,
    )
    result = models.CharField(
        verbose_name='执行结果',
        help_text='执行结果',
        max_length=100,
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        User,
        verbose_name='创建人',
        on_delete=models.SET_NULL,
        help_text='创建人',
        null=True,
        blank=True,
    )
    created_time = models.DateTimeField(
        verbose_name='创建时间',
        help_text="创建时间",
        default=timezone.now,
    )

    class Meta:
        verbose_name = '设备操作记录'
        verbose_name_plural = verbose_name


class TopicTransferCfg(models.Model):

    class Meta:
        verbose_name = 'topic映射'
        verbose_name_plural = verbose_name

    DATA_FLOW_ = (
        ('up', '上行'),
        ('down', '下行'),
    )
    DATA_FLOW_MAP = dict(DATA_FLOW_)
    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='topic_cfgs',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE
    )
    data_stream = models.ForeignKey(
        DeviceCategoryDataStream,
        verbose_name='自定义数据流',
        help_text='自定义数据流',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    data_flow = models.CharField(
        verbose_name='数据流向',
        help_text='数据流向',
        max_length=10,
        choices=DATA_FLOW_
    )
    topic = models.CharField(
        verbose_name='映射topic',
        help_text='映射topic',
        max_length=200,
        db_index=True
    )
    subscribe_topic = models.CharField(
        verbose_name='订阅topic',
        help_text='订阅topic',
        max_length=200,
        null=True,
        blank=True
    )
    creator = models.ForeignKey(
        User,
        verbose_name='创建人',
        on_delete=models.SET_NULL,
        help_text='创建人',
        null=True,
        blank=True,
    )
    created_time = models.DateTimeField(
        verbose_name='创建时间',
        help_text="创建时间",
        default=timezone.now,
    )


class CloudGateway(models.Model):
    """
    云网关
    """
    project = models.ForeignKey(
        Projects,
        related_name='project_cloud_gateways',
        on_delete=models.CASCADE,
        verbose_name='项目',
        help_text='项目',
        null=True,
        blank=True,
    )
    name = models.CharField(
        verbose_name='云网关名称',
        help_text='云网关名称',
        max_length=100
    )
    device_category = models.ForeignKey(
        DeviceCategory,
        related_name='cloud_gateways',
        verbose_name='设备类型',
        help_text='设备类型',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    data_stream = models.ForeignKey(
        DeviceCategoryDataStream,
        verbose_name='自定义数据流',
        help_text='自定义数据流',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    key = models.CharField(
        verbose_name='云网关唯一标识',
        help_text='云网关唯一标识：以"CG_"开头，如"CG_XXX"',
        max_length=68,
        unique=True
    )
    device_field = models.CharField(
        verbose_name='设备标识字段',
        help_text='设备标识字段',
        max_length=100,
        null=True,
        blank=True
    )
    client_ips = models.JSONField(
        verbose_name='ip白名单',
        help_text='ip白名单',
        null=True,
        blank=True,
    )
    is_custom_resp = models.BooleanField(
        verbose_name='是否自定义响应',
        help_text='是否自定义响应',
        default=False
    )
    action_conf = models.JSONField(
        verbose_name='自定义响应云函数配置',
        help_text='自定义响应云函数配置',
        null=True,
        blank=True,
    )
    desc = models.TextField(
        verbose_name='描述',
        help_text="描述",
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        User,
        verbose_name='创建人',
        on_delete=models.SET_NULL,
        help_text='创建人',
        null=True,
        blank=True,
    )
    created_time = models.DateTimeField(
        verbose_name='创建时间',
        help_text="创建时间",
        default=timezone.now,
    )

    class Meta:
        verbose_name = '云网关'
        verbose_name_plural = verbose_name
