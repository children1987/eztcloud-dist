#!/bin/sh
# 本文件用于重新部署后端服务

project_name="isw_v2"

# 固定到 deploy 目录运行，避免相对路径导致找不到文件
cd /workspace/isw_v2/deploy || exit 1


echo "git configging ..."
git config core.filemode false
echo "git configging finished. "


echo "git pull 开始"
echo "如果不需要重新拉取代码，则可输入空用户名密码"
cd /workspace/isw_v2 || exit 1
git pull
chmod +x auto_deploy*.sh 2>/dev/null || true
cd /workspace/isw_v2/deploy || exit 1
echo "git pull 完成"


echo "注意：请确保codeup流水线打包已完成"


# 配置nginx
nginx_cfg_file_name=$project_name"_local_nginx.conf"
nginx_stream_cfg_file_name=$project_name"_tcp_nginx_stream.conf"
if [ ! -f "/workspace/nginx/projects/$nginx_cfg_file_name" ]; then
    echo "copy Nginx config file"
    mkdir -p /workspace/nginx/projects

    echo "copy ./nginx/"$nginx_cfg_file_name" to /workspace/nginx/projects/"
    cp ./nginx/$nginx_cfg_file_name /workspace/nginx/projects/

    echo "copy ./nginx/"$nginx_stream_cfg_file_name" to /workspace/nginx/projects/"
    cp ./nginx/$nginx_stream_cfg_file_name /workspace/nginx/projects/

    echo "docker restart nginx"
    docker restart nginx
fi


TOKEN=${INFLUXDB_TOKEN}
if grep -q '^INFLUXDB_TOKEN=' /workspace/isw_v2/backend/.env; then
    sed -i "s#^INFLUXDB_TOKEN=.*#INFLUXDB_TOKEN=$TOKEN#" /workspace/isw_v2/backend/.env
else
    echo "DOCKER_INFLUXDB_TOKEN=$TOKEN" >> /workspace/isw_v2/backend/.env
fi

# backend/.env -> deploy/.env（容器编排依赖）
cp /workspace/isw_v2/backend/.env /workspace/isw_v2/deploy/.env 2>/dev/null || true

# 关键改动：共享镜像只构建一次，避免 docker-compose 对同一个 tag 并行 build 导致冲突
export COMPOSE_HTTP_TIMEOUT=300

echo "docker build isw:latest ..."
docker build -t isw:latest -f /workspace/isw_v2/deploy/Dockerfile /workspace/isw_v2

echo "docker build log_saver_by_telegraf:latest ..."
docker build -t log_saver_by_telegraf:latest -f /workspace/isw_v2/deploy/telegraf/Dockerfile /workspace/isw_v2/deploy

# 不再执行 docker-compose build，直接 up（会复用本地 isw:latest / log_saver_by_telegraf:latest）
echo "docker-compose up -d ..."
docker-compose -f /workspace/isw_v2/deploy/docker-compose.yml -p $project_name up -d

echo "docker-compose up -d finished."

# 使用 logrotate 管理日志（若目录不存在则忽略）
cp /workspace/isw_v2/deploy/logrotate/* /etc/logrotate.d/ 2>/dev/null || true

if [ `crontab -l | grep -c isw_v2` -eq 0 ];then
  crontab -l > old_crontab.backup
  echo "添加 cron task"
  (crontab -l ; echo "0 2 * * * docker exec -i isw_v2_web_server python manage.py clearsessions") | crontab
  (crontab -l ; echo "*/20 * * * * docker exec -i isw_v2_web_server python /workspace/isw_v2/backend/device_monitor/server_data_checker.py >> /workspace/isw_v2/backend/log/server_data_checker.out 2>&1") | crontab
else
  echo 'cron tasks 已存在'
fi
