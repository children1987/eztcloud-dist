# 使用 Python 3.11 作为基础镜像，然后安装 Telegraf（匹配主 Dockerfile 的 Python 版本）
FROM python:3.11-slim
LABEL maintainer="Shihow Inc <public@shihow.cn>"

WORKDIR /workspace/isw_v2/backend

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 安装 Telegraf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    gnupg \
    && wget -q https://repos.influxdata.com/influxdata-archive_compat.key -O /etc/apt/trusted.gpg.d/influxdata-archive_compat.key.gpg && \
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.key.gpg] https://repos.influxdata.com/debian stable main" > /etc/apt/sources.list.d/influxdata.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends telegraf=1.26.1-1 && \
    rm -rf /var/lib/apt/lists/*

COPY telegraf/requirements.txt /workspace/isw_v2/deploy/telegraf/

RUN python3 -m pip install --upgrade pip setuptools wheel Cython -i https://pypi.doubanio.com/simple/
RUN pip install -r ../deploy/telegraf/requirements.txt

# 设置 Telegraf 作为入口点
ENTRYPOINT ["telegraf"]
