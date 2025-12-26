#!/usr/bin/env bash

set -e

BASE_DIR=/workspace/isw_v2/mqtt_broker/emqx
PERSIST_DIR="$BASE_DIR/persist"

echo "准备 EMQX 持久化目录..."
mkdir -p "$PERSIST_DIR/data" "$PERSIST_DIR/log"
chmod -R 777 "$PERSIST_DIR"
echo "持久化目录已就绪：$PERSIST_DIR"

echo "启动 EMQX 容器 isw_v2_emqx5.8.0 ..."
docker run --network=host -d --name isw_v2_emqx5.8.0 --restart unless-stopped \
    -v "$PERSIST_DIR/data":/opt/emqx/data \
    -v "$PERSIST_DIR/log":/opt/emqx/log \
    -v "$BASE_DIR/emqx_local.conf":/opt/emqx/etc/emqx.conf \
    -v "$BASE_DIR/acl.conf":/opt/emqx/etc/acl.conf \
    emqx/emqx:5.8.0

echo "EMQX 容器启动命令已执行。"
