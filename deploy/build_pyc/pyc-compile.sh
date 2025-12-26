#!/bin/bash
# 项目目录
project_path="/workspace/isw_v2"

# 删除目录下的所有旧pyc文件
find $project_path -type f -name "*.pyc" -delete
echo "删除旧pyc文件完成"

# 将目录下的所有py文件编译成pyc文件，排除指定文件
find "$project_path" -type f -name "*.py" \
    -not -path "$project_path/backend/log_savers/main.py" \
    -exec python3 -m compileall {} +
echo "编译完成"


# 删除已编译的py文件
find "$project_path" -type f -name "*.py" \
    -not -path "$project_path/backend/log_savers/main.py" \
    -delete
echo "删除源py文件完成"

# 拷贝__pycache__中的pyc文件到同级目录
find $project_path -type d -name "__pycache__" -exec sh -c 'cp -R {}/* "$(dirname {})"; rm -rf {}' \;
echo "__pycache__完成"

# 查找目录下的所有pyc文件，将其重命名为去掉版本号的名字
find $project_path -type f -name "*.pyc" | while read -r file; do
    dir=$(dirname "$file")
    file_name=$(basename "$file")
    new_name=$(echo "$file_name" | sed 's/\..*\.pyc/.pyc/')
    mv "$file" "$dir/$new_name"
done
echo "重命名完成"