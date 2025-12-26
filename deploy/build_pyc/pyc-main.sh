#!/bin/bash

project_path="/workspace/isw_v2"

# 异常捕获函数
check_status() {
    local status=$?
    if [ $status -ne 0 ]; then
        if [ "$1" = "init" ]; then
            rm -rf ".git"
        fi
        exit $status
    fi
}

# 拉取新代码
cd $project_path
if [ -d ".git" ]; then
    branch=$(git branch)
    new_branch="${branch//\*\ /}"

    # 错误捕捉如果密码错误，直接结束脚本
    check_status
    git reset --hard
    # git reset --hard origin/$new_branch
    git pull
    check_status
else
    git init
    git remote add origin https://codeup.aliyun.com/shihow/xian/isw_v2.git
    git fetch --all
    check_status "init"
    git checkout -f -b dev origin/dev
fi




cd "$project_path/deploy/build_pyc"
chmod +x pyc-backup.sh pyc-compile.sh pyc-main.sh

if docker images | grep -q 'isw\s*latest'; then
    docker_image="isw:latest"
else
    docker_image="python:3.11"
fi

docker run --rm -v /workspace/isw_v2:/workspace/isw_v2 -v /opt:/opt $docker_image $project_path/deploy/build_pyc/pyc-compile.sh

cd $project_path
rm -rf ".git"

echo "已完成"
echo "若需重启容器，可执行："
echo "deploy/restart.sh"
