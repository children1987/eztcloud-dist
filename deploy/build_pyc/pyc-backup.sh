#!/bin/bash
# 该脚本应用于重要数据进行增量备份

# 需要备份项目名
project_name="isw_v2"
# 项目根路径
base_path="/workspace/$project_name"
# 保存备份文件的位置
save_dir="/opt/isw_v2_back"

# 检查保存备份文件的目录是否存在，如果不存在则创建
if [ ! -d "$save_dir" ]; then
    mkdir -p "$save_dir"
fi

# 需要备份的文件夹列表
backup_dirs=("media" "redis_data" "influxdb" "mqtt_broker")

# 进入保存备份文件的目录
cd "$save_dir"

# 遍历需要备份的文件夹列表
for backups_dir in "${backup_dirs[@]}"
do
    file_name="$save_dir/$project_name-$backups_dir.tar.gz"

    # 根据不同目录设置备份时的源路径
    if [ "$backups_dir" = "media" ]; then
        source_path="$base_path/backend"
    else
        source_path="$base_path"
    fi

    # 如果文件已经进行过压缩备份，直接进行增量备份
    if [ -f "$file_name" ]; then
        # 将已经备份好的文件夹解压缩
        gzip -d "$file_name"
        # 进行增量备份
        tar -uf "$project_name-$backups_dir.tar" -C "$source_path" "$backups_dir"
        # 将备份好的文件压缩
        gzip -f "$project_name-$backups_dir.tar"
    # 如果没有就先进行压缩备份
    else
        tar -zcf "$file_name" -C "$source_path" "$backups_dir"
    fi
done