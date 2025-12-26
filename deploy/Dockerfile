FROM python:3.11
LABEL maintainer="Shihow Inc <public@shihow.cn>"

WORKDIR /workspace/isw_v2/backend

COPY backend/Pipfile ./
COPY backend/Pipfile.lock ./

RUN rm -rf /etc/apt/sources.list.d
COPY deploy/sources.list /etc/apt/sources.list
RUN apt-get update 2>&1 | tee /tmp/apt-update.log || true && \
    if grep -q "not signed\|NO_PUBKEY" /tmp/apt-update.log 2>/dev/null; then \
        apt-get update --allow-insecure-repositories && \
        apt-get install -y --allow-unauthenticated debian-archive-keyring ca-certificates gnupg2 && \
        apt-key update && \
        apt-get update; \
    else \
        apt-get update; \
    fi
RUN apt-get install -y curl ca-certificates gnupg
RUN mkdir -p /etc/apt/sources.list.d
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list
RUN apt-get update
RUN apt install -y nodejs

RUN python -m pip install --upgrade pip setuptools wheel Cython -i https://pypi.doubanio.com/simple/
RUN python -m pip install -i https://pypi.doubanio.com/simple/ pipenv
RUN pipenv requirements > requirements.txt && \
    pip install -r requirements.txt
