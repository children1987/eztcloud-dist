# 内置 MQTT 用户模板（统一维护，部署相关脚本共享）
# frontend 密码固定，其他密码在首次生成时随机。
INTERNAL_USER_TEMPLATES = [
    {"username": "frontend", "password": "df3efi30Fdf8eizSSFEfz9zfz9"},
    {"username": "SU_telegraf_ro"},
    {"username": "SU_mqtt_receiver"},
    {"username": "SU_reader"},
    {"username": "SU_down_sender"},
    {"username": "SU_up_worker"},
    {"username": "SU_web_server"},
    {"username": "SU_rule_engine"},
    {"username": "SU_task_engine"},
    {"username": "SU_scene_engine"},
    {"username": "SU_alarm_engine"},
    {"username": "SU_device_shadow"},
    {"username": "SU_device_monitor"},
    {"username": "SU_notifier"},
    {"username": "mcp_server"},
    {"username": "SU_mqtt_sender"},
    {"username": "SU_topic_transfer"},
    {"username": "SU_mcq"},
]

