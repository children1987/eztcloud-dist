from os import path
from django.apps import AppConfig


VERBOSE_APP_NAME = "账号"


def get_current_app_name(f):
    return path.dirname(f).replace('\\', '/').split('/')[-1]


class AppVerboseNameConfig(AppConfig):
    name = 'backend.apps.users'
    label = 'users'
    verbose_name = VERBOSE_APP_NAME


default_app_config = 'backend.apps.users.__init__.AppVerboseNameConfig'
