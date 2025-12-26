from django.urls import path
from .views import URLRedirectView


urlpatterns = [
    path('<slug:shortcode>/', URLRedirectView.as_view(), name='scode'),
]
