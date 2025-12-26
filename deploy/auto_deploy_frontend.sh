#!/bin/sh
# 本文件用于重新部署后端服务

# nginx配置文件名
project_name="isw_v2"

echo "git pull 开始"
git pull
chmod +x auto_deploy*.sh
echo "git pull 完成"

# 前端静态文件生成
# 方式1: 适用于服务器本地存放
# echo "本地前端打包 开始"
# docker run -it --rm --name mycnpm --network host -v /workspace/$project_name:/workspace/$project_name -w /workspace/$project_name/frontend_web_v5 children1987/mycnpm:12-alpine cnpm i
# docker run -it --rm --name mycnpm --network host -v /workspace/$project_name:/workspace/$project_name -w /workspace/$project_name/frontend_web_v5 children1987/mycnpm:12-alpine cnpm run build
# echo "本地前端打包 完成"
# 方式2: 适用于cos存放
echo "注意：请确保codeup流水线打包已完成"

echo "重启 ${project_name}_web_server 开始，此步骤含 migrate、collectstatic、重启uwsgi"
docker restart ${project_name}_web_server
echo "重启 ${project_name}_web_server 完成"
