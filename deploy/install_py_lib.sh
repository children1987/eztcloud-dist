#!/bin/bash

echo -e "请输入第三方库和版本号，例：xxxx==0.94.1 \n"
read choice
echo -e "\n"
echo -e "请输入指定源URL，默认清华源，如不指定，直接按回车跳过 \n"
read URL


if [ -n "$URL" ]; then
    install_command="pip install $choice -i $URL"
else
    install_command="pip install $choice -i http://pypi.tuna.tsinghua.edu.cn/simple/"
fi


container_list=("isw_v2_scene_engine" "isw_v2_celery" "isw_v2_topic_transfer" "isw_v2_log_scene_run_saver" "isw_v2_web_server" "isw_v2_task_engine" "isw_v2_alarm_engine" "isw_v2_device_monitor" "isw_v2_down_sender" "isw_v2_mqtt_sender" "isw_v2_mqtt_receiver" "isw_v2_up_worker" "isw_v2_tcp_server" "isw_v2_celery_beat" "isw_v2_data_saver")

for container in "${container_list[@]}"
do
    docker exec $container $install_command
done
