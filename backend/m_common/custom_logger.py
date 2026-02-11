import logging
import importlib
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import environ
env = environ.Env()

BACKEND_PATH = environ.Path(__file__) - 2
LOG_PATH = BACKEND_PATH.path("log_level")


# 需要热更新等级的日志管理器列表
CHANGE_LOGGER = [
    # 'django',
    'my',
    "alarm_engine",
    "requestlogs",
    "emqx_action",
    "scene_engine_log",
    "task_engine_log",
    "celerylogs",
    "celery_send_sms",
    "device_monitor",
    "device_shadow",
    "down_sender",
    "up_worker",
    "mqtt_receiver",
    "mqtt_sender",
    "notifier",
    "rule_engine",
    "tcp_server",
    "data_saver",
    "weather_log",
    "topic_transfer",
]


LEVEL_MAP = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET',
}


def get_log_level(is_str=True):
    """
    获取日志级别
    :param is_str:
    :return:
    """
    log_level_module = importlib.import_module('backend.log_level.level_cfg')
    importlib.reload(log_level_module)
    log_level = int(log_level_module.LOG_LEVEL)
    if is_str:
        return LEVEL_MAP.get(log_level, 'INFO')
    return log_level


class TruncatingFilter(logging.Filter):
    """
    日志内容自动截断过滤器 - 升级版
    同时处理直接消息(record.msg)和参数化日志(record.args)
    """
    def __init__(self, max_len=512):
        super().__init__()
        self.max_len = max_len

    def _truncate(self, obj):
        try:
            s = str(obj)
            if len(s) > self.max_len:
                return s[:self.max_len] + "... [auto-truncated]"
            return obj # 保持原样，减少不必要的字符串转换
        except Exception:
            return "[truncate-error]"

    def filter(self, record):
        # 避免重复过滤
        if getattr(record, '_truncated', False):
            return True
        
        try:
            # 1. 处理直接消息
            if isinstance(record.msg, str):
                if len(record.msg) > self.max_len:
                    record.msg = record.msg[:self.max_len] + "... [auto-truncated]"
            elif not record.args: # logger.info(big_dict) 这种 record.msg 是对象
                record.msg = self._truncate(record.msg)

            # 2. 处理参数化日志 logger.info("msg: %s", big_dict)
            if record.args:
                if isinstance(record.args, dict):
                    new_args = {k: self._truncate(v) for k, v in record.args.items()}
                    record.args = new_args
                else:
                    new_args = tuple(self._truncate(arg) for arg in record.args)
                    record.args = new_args
            
            record._truncated = True
        except Exception:
            pass
        return True


class LogLevelHandler(FileSystemEventHandler):

    LEVEL_NAME_MAP = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }

    def __init__(self):
        self.log_level = None
        self.logger_obj = None
        # self.set_log_level()
        super().__init__()

    def set_log_level(self):
        """
        设置日志级别
        :return:
        """
        try:
            c_log_level = get_log_level(is_str=False)
            if c_log_level not in LEVEL_MAP:
                return

            old_log_level = self.log_level
            self.log_level = c_log_level

            trunc_filter = TruncatingFilter(max_len=512)

            for logger_obj in logging.root.manager.loggerDict.values():
                if not isinstance(logger_obj, logging.Logger):
                    continue
                if logger_obj.name not in CHANGE_LOGGER:
                    continue

                # Apply level
                if logger_obj.level != c_log_level:
                    logger_obj.setLevel(c_log_level)

                # Apply truncation filter once
                has_filter = False
                for f in list(getattr(logger_obj, 'filters', [])):
                    if isinstance(f, TruncatingFilter):
                        has_filter = True
                        break
                if not has_filter:
                    logger_obj.addFilter(trunc_filter)

                logger_obj.info(
                    f'logger: {logger_obj.name}, level_change: {old_log_level} --> {c_log_level}, '
                    f'c_log_level: {logger_obj.level}'
                )

                if logger_obj.name == 'my' or self.logger_obj is None:
                    self.logger_obj = logger_obj
        except Exception as e:
            err_msg = f'日志级别改变失败：{e}'
            if self.logger_obj is None:
                print(err_msg)
            else:
                self.logger_obj.error(err_msg)
    def on_modified(self, event):
        """
        文件修改事件
        :param event:
        :return:
        """
        if str(event.src_path).endswith('__init__.py'):
            self.set_log_level()
            if self.logger_obj is not None:
                self.logger_obj.debug(f'on_modified: {event}')



class WatchLogLevel(object):
    """
    日志等级文件监听器
    """
    WATCHED_PID = {}
    def __init__(self, log_level_path):
        self.observer = Observer(timeout=10)
        self.event_handler = LogLevelHandler()
        self.pid = os.getpid()
        self.to_watch_start(log_level_path)

    def to_watch_start(self, log_level_path):
        """
        启用监听器
        :param log_level_path:
        :return:
        """
        # 确保要监控的目录存在，如果不存在则创建
        if not os.path.exists(log_level_path):
            try:
                os.makedirs(log_level_path, exist_ok=True)
            except OSError as e:
                # 如果创建目录失败，记录错误但不抛出异常，避免影响 Django 启动
                print(f"警告: 无法创建日志级别监控目录 {log_level_path}: {e}")
                return
        
        # if self.pid not in self.WATCHED_PID:
        #     self.WATCHED_PID[self.pid] = 1
        #     self.event_handler.set_log_level()
        # else:
        #     self.WATCHED_PID[self.pid] += 1
        #     if self.event_handler.logger_obj is not None:
        #         count = self.WATCHED_PID[self.pid]
        #         self.event_handler.logger_obj.info(
        #             f'pid: {self.pid}, count: {count}'
        #         )
        try:
            self.observer.schedule(
                self.event_handler,
                log_level_path,
                recursive=True
            )
            self.observer.start()
        except OSError as e:
            # 如果监控启动失败（例如目录不存在或权限问题），记录错误但不抛出异常
            print(f"警告: 无法启动日志级别监控器 {log_level_path}: {e}")



WATCH_LOG_LEVEL = WatchLogLevel(str(LOG_PATH))
