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

    git fetch --all
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

# 删除所有pyc文件
find $project_path -type f -name "*.pyc" -delete
echo "删除pyc文件完成"

echo "回滚完成"
