from django.urls import path, include
from rest_framework_nested import routers

from .views import AsyncChatView, ChatSessionViewSet, ChatMessageViewSet, test_page


# 创建路由器
router = routers.SimpleRouter()
router.register('sessions', ChatSessionViewSet, basename='chat_session')

# 创建嵌套路由器，用于会话下的消息
session_router = routers.NestedSimpleRouter(router, 'sessions', lookup='session')
session_router.register('messages', ChatMessageViewSet, basename='chat_message')

urlpatterns = [
    # 测试页面
    path('test/', test_page, name='ai_chat_test'),

    # 聊天API
    path('chat/', AsyncChatView.as_view(), name='ai_chat'),

    # 会话和消息管理API
    path('', include(router.urls)),
    path('', include(session_router.urls)),
]
