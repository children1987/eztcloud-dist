#!/bin/sh
# 本文件用于重新部署后端服务

# nginx配置文件名
project_name="isw_v2"

echo "git pull 开始"
git pull
chmod +x auto_deploy*.sh
echo "git pull 完成"

echo "重启 ${project_name}_web_server 开始，此步骤含 migrate、collectstatic、重启uwsgi"
docker restart ${project_name}_web_server
echo "重启 ${project_name}_web_server 完成"

echo "docker restart com server"
docker restart ${project_name}_com_server
echo "restart docker com_server finished."

echo "docker restart celery server"
docker restart ${project_name}_celery
echo "restart docker celery finished."
