#!/bin/bash

echo -e "upgrade chinesecalendar start \n"

install_command="pip install -U chinesecalendar https://pypi.doubanio.com/simple/"
container_list=("isw_v2_scene_engine" "isw_v2_celery" "isw_v2_topic_transfer" "isw_v2_log_scene_run_saver" "isw_v2_web_server" "isw_v2_task_engine" "isw_v2_alarm_engine" "isw_v2_device_monitor" "isw_v2_down_sender" "isw_v2_mqtt_sender" "isw_v2_mqtt_receiver" "isw_v2_up_worker" "isw_v2_tcp_server" "isw_v2_celery_beat" "isw_v2_data_saver")

for container in "${container_list[@]}"
do
    docker exec $container $install_command
done
