from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.decorators.cache import cache_page
from django.views.static import serve
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_nested import routers

def root_view(request):
    """根路径视图，返回简单的API信息"""
    return JsonResponse({
        'message': 'EZtCloud API Server',
        'version': '2.0',
        'status': 'running',
        'docs': '/swagger-ui/' if settings.DEBUG else None
    })

from backend.apps.areas.views import AreasViewSet, WeatherViewSet
from backend.apps.alarms.views import AlarmNoticeGroupViewSet, AlarmDeviceViewSet, \
    AlarmViewSet, AlarmLogViewSet
from backend.apps.common.emqx_webhook.views import EmqxWebhookView
from backend.apps.control_panels.views import ControlPanelViewSet, ControlPanelButtonViewSet
from backend.apps.custom_servers.views import DomainView
from backend.apps.camera.views import EzvizConfigViewSet, CameraChannelViewSet, CameraAlarmViewSet, \
    EzvizWebhookView, AccessTokenView
from backend.apps.equipments.views import TcpRegisterView, DevicesViewSet, \
    DeviceCategoryViewSet, CommandInstanceViewSet, \
    CategoryCommandViewSet, CategoryEventViewSet, CategoryAttrViewSet, \
    CategoryDataStreamViewSet, CategoryModBusViewSet, \
    FixedProductViewSet, ManufacturerInfoViewSet, \
    DeviceCategoryAttrTemplatesViewSet, DeviceDataViewSet, \
    DeviceConnect1View, DeviceConnect2View, ManufacturerUserViewSet, \
    ManufacturerUserNestedViewSet, CloudGatewayViewSet, FixedProductFilesViewSet
from backend.apps.notice.views import NoticeViewSet, NotifyRecordUserViewSet, SmsRecordViewSet
from backend.apps.ota_versions.views import OtaConfigViewSet
from backend.apps.tag.views import TagViewSet
from backend.apps.tasks.views import TaskViewSet, TaskDeviceViewSet, TaskActionViewSet, TaskLogViewSet, TaskRunLogViewSet
from backend.apps.proj_common.views import ConstDataAPI
from backend.apps.rules.views import RuleViewSet, RuleActionViewSet, \
    RuleDeviceViewSet, RuleLogViewSet
from backend.apps.scenes.views import SceneConfigViewSet, SceneLogViewSet, DeviceSceneLogViewSet
from backend.apps.uploader.views import UploadViewSet
from backend.apps.users.views import ErrorTimesView, UserViewSet, ProjectViewSet, ExtraLogin, \
    DeviceGroupViewSet, ProjectMemberViewSet, RegisterViewSet, ImageCaptchaView, \
    ProjectsDailyStatsViewSet
from backend.apps.system_configs.views import SystemLicenseView
from backend.apps.iam_client.urls import iam_client_urls

router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('project_members', ProjectMemberViewSet, 'project_members')
router.register('uploader', UploadViewSet, 'uploader')
router.register('device_category', DeviceCategoryViewSet, 'device_category')
router.register('category_commands', CategoryCommandViewSet, 'category_commands')
router.register('category_events', CategoryEventViewSet, 'category_events')
router.register('category_attrs', CategoryAttrViewSet, 'category_attrs')
router.register('category_data_streams', CategoryDataStreamViewSet, 'category_data_streams')
router.register('category_mod_bus', CategoryModBusViewSet, 'category_mod_bus')
router.register('devices', DevicesViewSet, 'devices')
router.register('alarm_notice_group', AlarmNoticeGroupViewSet, 'alarm_notice_group')
router.register('alarms', AlarmViewSet, 'alarms')
router.register('alarm_devices', AlarmDeviceViewSet, 'alarm_devices')
router.register('tasks', TaskViewSet, 'tasks')
router.register('task_actions', TaskActionViewSet, 'task_actions')
router.register('task_devices', TaskDeviceViewSet, 'task_devices')
router.register('rules', RuleViewSet, 'rules')
router.register('rule_actions', RuleActionViewSet, 'rule_actions')
router.register('rule_devices', RuleDeviceViewSet, 'rule_devices')
router.register('scenes', SceneConfigViewSet, 'scenes')
router.register('areas', AreasViewSet, 'areas')
router.register('device_groups', DeviceGroupViewSet, 'device_groups')
router.register('weather', WeatherViewSet, 'weather')
router.register('register', RegisterViewSet, 'register')
router.register('fix_product_types', FixedProductViewSet, 'fix_product_types')
router.register('fix_products', FixedProductViewSet, 'fix_products')
router.register('manufacturers', ManufacturerInfoViewSet, 'manufacturers')
# 待废弃，使用 ManufacturerUserNestedViewSet 代替
router.register('manufacturer_users', ManufacturerUserViewSet, 'manufacturer_user')
router.register('emqx_webhook', EmqxWebhookView, 'emqx_webhook')
router.register('command_instance', CommandInstanceViewSet, 'command_instance')
router.register('attr_templates', DeviceCategoryAttrTemplatesViewSet, 'attr_templates')
router.register('ota_cfgs', OtaConfigViewSet, 'ota_cfgs')
router.register('notice', NoticeViewSet, 'notice')
router.register('notice_users', NotifyRecordUserViewSet, 'notice_users')
router.register('users', UserViewSet, 'users')
router.register('sms_records', SmsRecordViewSet, 'sms_records')
router.register('project_daily_stats', ProjectsDailyStatsViewSet, 'project_daily_stats')

manufacturer_router = routers.NestedSimpleRouter(router, 'manufacturers', lookup='manufacturer')
manufacturer_router.register('users', ManufacturerUserNestedViewSet, 'manufacturer_user')

fix_product_router = routers.NestedSimpleRouter(router, 'fix_products', lookup='product')
fix_product_router.register('files', FixedProductFilesViewSet, 'fix_product_files')

project_router = routers.NestedSimpleRouter(router, 'projects', lookup='project')
project_router.register('tags', TagViewSet)
project_router.register('devices', DevicesViewSet, basename='devices')
project_router.register('device_categories', DeviceCategoryViewSet, basename='device_categories')
project_router.register('device_data', DeviceDataViewSet)
project_router.register('alarm_logs', AlarmLogViewSet)
project_router.register('rule_logs', RuleLogViewSet)
project_router.register('task_logs', TaskLogViewSet)
project_router.register('task_run_logs', TaskRunLogViewSet, basename='task-run-logs')
project_router.register('scene_logs', SceneLogViewSet)
project_router.register('device_scene_logs', DeviceSceneLogViewSet, basename='device-scene-logs')
project_router.register('cloud_gateways', CloudGatewayViewSet, basename='cloud-gateways')
project_router.register('control_panels', ControlPanelViewSet, basename='control-panels')
project_router.register('control_panel_buttons', ControlPanelButtonViewSet, basename='cp-buttons')
project_router.register('camera/ezviz/config', EzvizConfigViewSet, basename='ezviz-config')
project_router.register('camera/ezviz/channels', CameraChannelViewSet, basename='ezviz-channels')
project_router.register('camera/ezviz/alarms', CameraAlarmViewSet, basename='ezviz-alarms')

api_v1 = [
    path('iam/', include((iam_client_urls, 'iam'), namespace="iam")),
]

urlpatterns = [
    re_path('^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(router.urls)),
    path('api/', include(manufacturer_router.urls)),
    path('api/', include(project_router.urls)),
    path('api/', include(fix_product_router.urls)),
    path('api/connect/1/', DeviceConnect1View.as_view(), name='connect_1'),
    path('api/connect/2/', DeviceConnect2View.as_view(), name='connect_2'),
    path('api/const_data/', ConstDataAPI.as_view(), name='const_data'),
    path(settings.ADMIN_URL, admin.site.urls),
    path('s/', include('backend.apps.url_shortener.urls')),
    path('api/wechat/', include('backend.apps.wechat.urls')),
    path('api/ai/', include('backend.apps.ai_chat.urls')),  # AI聊天API
    path('api/projects/<str:project_key>/camera/ezviz/webhook/', EzvizWebhookView.as_view(), name='ezviz-webhook'),
    path('api/projects/<str:project_key>/camera/ezviz/token/', AccessTokenView.as_view(), name='ezviz-token'),
    path('api/domain/', DomainView.as_view(), name="domain"),
    path('api/system/license/', SystemLicenseView.as_view(), name='system-license'),
    path('i18n/', include('django.conf.urls.i18n')),

    # iam
    path('api/v1/', include((api_v1, 'api_v1'), namespace="api_v1")),

    # tcp server
    path('api/tcp_registers/', TcpRegisterView.as_view(), name='tcp_registers'),

    path('api_login/', ExtraLogin.as_view()),
    path('api/error_times/', ErrorTimesView.as_view(), name='error_times'),
    path('api/image_captcha/', ImageCaptchaView.as_view(), name='image_captcha'),
]

if settings.IS_USE_COS:
    from backend.apps.common.views import StsAuth, StsAuthToken

    urlpatterns += [
        path("", root_view, name="home"),
        path('api/sts-auth/', StsAuth.as_view(), name="sts-auth"),
        path('api/sts-auth-token/', StsAuthToken.as_view(), name="sts-auth"),
    ]
else:
    from django.views.generic import TemplateView
    urlpatterns += [
        path("", TemplateView.as_view(template_name="index.html"), name="home"),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 文档相关路由
doc_patterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# 文档相关路由
if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
else:
    urlpatterns += [
        path('api/schema/', cache_page(3600)(SpectacularAPIView.as_view()), name='schema'),
        path('swagger-ui/', cache_page(3600)(SpectacularSwaggerView.as_view(url_name='schema')), name='swagger-ui'),
        path('redoc/', cache_page(3600)(SpectacularRedocView.as_view(url_name='schema')), name='redoc'),
    ]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
