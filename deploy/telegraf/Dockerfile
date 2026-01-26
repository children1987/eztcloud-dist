# 使用 Python 3.11 作为基础镜像，然后安装 Telegraf（匹配主 Dockerfile 的 Python 版本）
FROM python:3.11
LABEL maintainer="Shihow Inc <public@shihow.cn>"

WORKDIR /workspace/isw_v2/backend

ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 使用本地镜像源并正确导入 InfluxData key
COPY sources.list /etc/apt/sources.list
RUN rm -rf /etc/apt/sources.list.d && mkdir -p /etc/apt/sources.list.d && \
    apt-get update -o Acquire::Retries=3 -o Acquire::http::Timeout=30 && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      wget \
      curl \
      gnupg && \
    mkdir -p /usr/share/keyrings && \
    (wget -q https://repos.influxdata.com/influxdata-archive_compat.key -O /tmp/influxdata-archive_compat.key || \
     curl -fsSL https://repos.influxdata.com/influxdata-archive_compat.key -o /tmp/influxdata-archive_compat.key) && \
    gpg --dearmor /tmp/influxdata-archive_compat.key > /usr/share/keyrings/influxdata-archive_compat.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main" > /etc/apt/sources.list.d/influxdata.list && \
    apt-get update -o Acquire::Retries=3 -o Acquire::http::Timeout=30 && \
    apt-get install -y --no-install-recommends telegraf=1.26.1-1 && \
    rm -rf /var/lib/apt/lists/* /tmp/influxdata-archive_compat.key

COPY telegraf/requirements.txt /workspace/isw_v2/deploy/telegraf/

RUN python3 -m pip install --upgrade pip setuptools wheel Cython -i https://pypi.doubanio.com/simple/
RUN pip install -r ../deploy/telegraf/requirements.txt

# 设置 Telegraf 作为入口点
ENTRYPOINT ["telegraf"]
