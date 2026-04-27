#!/usr/bin/env python3
"""
EMQX 自动化安装脚本（本地环境）。

功能：
1. 随机生成 dashboard 管理员密码（用户名固定为 admin）。
2. 将凭证写入 /workspace/isw-helper/output/deploy_credentials.json。
3. 准备持久化目录 /workspace/isw_v2/mqtt_broker/emqx/persist/{data,log}。
4. 删除旧容器（如存在），并使用环境变量启动 emqx/emqx:5.8.0 容器。
"""

import argparse
import http.client
import json
import secrets
import string
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONTAINER_NAME = "isw_v2_emqx5.8.0"
IMAGE_NAME = "emqx/emqx:5.8.0"

BASE_DIR = Path("/workspace/isw_v2/mqtt_broker/emqx")
PERSIST_DIR = BASE_DIR / "persist"

CREDENTIAL_FILE = Path("/workspace/isw-helper/output/deploy_credentials.json")


def run_command(cmd):
    """执行命令并输出日志。"""
    print(f"→ 执行命令: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, universal_newlines=True)


def generate_password(length=20):
    """生成适合做 Web 登录密码的随机字符串（避免过多奇怪符号）。"""
    alphabet = string.ascii_letters + string.digits + "_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def load_existing_credentials():
    """从凭证文件中加载现有的 EMQX 凭证。"""
    if not CREDENTIAL_FILE.exists():
        return None
    try:
        payload = json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        return payload.get("emqx")
    except (json.JSONDecodeError, KeyError):
        return None


def write_credentials(
    username,
    password,
    ip=None,
    dashboard_port=58084,
    update_password=True,
):
    """将 EMQX 凭证写入 JSON 文件，保留其他条目。

    Args:
        username: 用户名
        password: 密码（仅在 update_password=True 时更新）
        ip: 服务器 IP，用于生成 dashboard_url
        update_password: 是否更新密码（如果容器已存在，应设为 False 以保留旧密码）
    """
    CREDENTIAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    payload = {}
    if CREDENTIAL_FILE.exists():
        try:
            payload = json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("⚠️ 现有凭证文件无法解析，将被覆盖。")
            payload = {}

    dashboard_url = f"http://{ip}:{dashboard_port}"

    # 如果容器已存在且不更新密码，则保留现有密码（使用凭证文件中的密码）
    if not update_password:
        existing_emqx = payload.get("emqx", {})
        existing_password = existing_emqx.get("password")
        if existing_password:
            password = existing_password
            print("⚠️ 检测到容器已存在，保留现有密码（不更新 deploy_credentials.json 中的密码）")
        else:
            # 如果凭证文件中没有密码，仍然使用传入的密码（可能是从其他地方读取的）
            print("⚠️ 检测到容器已存在，但凭证文件中无密码，使用传入的密码")

    payload["emqx"] = {
        "username": username,
        "password": password,
        "dashboard_url": dashboard_url,
        "dashboard_port": dashboard_port,
        "updated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    }

    CREDENTIAL_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if update_password:
        print(f"✓ EMQX 凭证已写入 {CREDENTIAL_FILE}")
    else:
        print("✓ EMQX dashboard_url 已更新（密码保持不变）")


def ensure_persist_dirs():
    """准备持久化目录。"""
    data_dir = PERSIST_DIR / "data"
    log_dir = PERSIST_DIR / "log"

    for d in (data_dir, log_dir):
        d.mkdir(parents=True, exist_ok=True)
        print(f"✓ 目录已准备: {d}")

    try:
        # 权限调整在 Linux 环境下有效；在 Windows 下可忽略失败
        subprocess.run(
            ["chmod", "-R", "777", str(PERSIST_DIR)],
            check=False,
            universal_newlines=True,
        )
        print(f"✓ 持久化目录权限已调整: {PERSIST_DIR}")
    except FileNotFoundError:
        # 没有 chmod（例如在纯 Windows 环境），忽略即可
        print("⚠️ 未找到 chmod 命令，跳过权限设置。")


def container_exists():
    """检查容器是否存在（包括运行中和已停止的）。"""
    result = subprocess.run(
        ["docker", "ps", "-a", "-q", "-f", f"name={CONTAINER_NAME}"],
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return bool((result.stdout or "").strip())


def _wait_emqx_api_ready(host: str, port: int, timeout: int = 120):
    """等待 EMQX Dashboard API 可访问。"""
    start = datetime.now()
    while (datetime.now() - start).total_seconds() < timeout:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=3)
            conn.request("GET", "/api/v5/status")
            resp = conn.getresponse()
            _ = resp.read()
            conn.close()
            if resp.status in (200, 401, 403):
                return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"等待 EMQX API 就绪超时: {host}:{port}")


def _verify_dashboard_login(host: str, port: int, username: str, password: str) -> bool:
    """校验 dashboard 账号密码是否可登录。"""
    try:
        conn = http.client.HTTPConnection(host, port, timeout=8)
        payload = json.dumps({"username": username, "password": password})
        conn.request("POST", "/api/v5/login", body=payload, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="ignore")
        conn.close()
        if resp.status != 200:
            return False
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        return bool(data.get("token"))
    except Exception:
        return False


def remove_existing_container():
    """如有同名容器则删除。"""
    if container_exists():
        print(f"发现已有容器 {CONTAINER_NAME}，尝试删除...")
        subprocess.run(
            ["docker", "rm", "-f", CONTAINER_NAME],
            check=False,
            universal_newlines=True,
        )
        print("✓ 旧 EMQX 容器已删除")


def start_emqx(username, password):
    """使用环境变量启动 EMQX 容器，并设置 dashboard 默认账号密码。"""
    # EMQX 5.x 支持通过 EMQX_DASHBOARD__DEFAULT_USERNAME / PASSWORD 设置 dashboard 默认账号
    cmd = [
        "docker",
        "run",
        "--network=host",
        "-d",
        "--name",
        CONTAINER_NAME,
        "--restart",
        "unless-stopped",
        "-v",
        f"{PERSIST_DIR}/data:/opt/emqx/data",
        "-v",
        f"{PERSIST_DIR}/log:/opt/emqx/log",
        "-v",
        f"{BASE_DIR}/emqx_local.conf:/opt/emqx/etc/emqx.conf",
        "-v",
        f"{BASE_DIR}/acl.conf:/opt/emqx/etc/acl.conf",
        "-e",
        f"EMQX_DASHBOARD__DEFAULT_USERNAME={username}",
        "-e",
        f"EMQX_DASHBOARD__DEFAULT_PASSWORD={password}",
        IMAGE_NAME,
    ]

    run_command(cmd)
    print(f"✓ EMQX 容器 {CONTAINER_NAME} 启动完成")


def main():
    parser = argparse.ArgumentParser(description="EMQX 自动化安装脚本")
    parser.add_argument(
        "--ip",
        required=True,
        help="EMQX 所在服务器 IP，用于生成 dashboard_url（必填）",
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=58084,
        help="需要 Nginx 58084 反代是因为静态资源不想用官方的，官方的太慢",
    )
    args = parser.parse_args()

    try:
        ensure_persist_dirs()
        
        # 检查容器是否已存在
        container_already_exists = container_exists()

        username = "admin"
        existing_creds = load_existing_credentials() or {}
        existing_password = existing_creds.get("password")

        # 优先使用现有凭证中的密码，避免在持久化数据已存在时写入错误密码
        if existing_password:
            password = existing_password
            if container_already_exists:
                print("✓ 检测到容器已存在，优先使用 deploy_credentials.json 中的现有密码")
        else:
            password = generate_password()
            if container_already_exists:
                print("⚠️ 容器已存在但凭证文件无密码，将尝试使用新密码启动并进行登录校验")

        # 删除旧容器（如果存在）
        remove_existing_container()

        # 先写入凭证（后续会通过登录校验确认是否有效）
        write_credentials(
            username,
            password,
            ip=args.ip,
            dashboard_port=args.dashboard_port,
            update_password=True,
        )

        # 启动新容器
        start_emqx(username, password)

        # 强校验：确保 deploy_credentials.json 中的密码确实能登录 EMQX
        _wait_emqx_api_ready("127.0.0.1", int(args.dashboard_port), timeout=120)
        if not _verify_dashboard_login("127.0.0.1", int(args.dashboard_port), username, password):
            raise RuntimeError(
                "EMQX 已启动，但 deploy_credentials.json 中的 admin 密码登录校验失败。"
                "这通常表示存在历史持久化数据且密码与凭证文件不一致。"
                "请先修正 deploy_credentials.json 为真实密码，或清理持久化目录后重装。"
            )

        print("EMQX 部署完成，且凭证已通过登录校验。")
        # 同步 nginx 配置并重启 nginx（用于 EMQX 反向代理）
        nginx_conf_src = BASE_DIR / 'nginx_conf' / "emqx_local_nginx.conf"
        nginx_conf_dst_dir = Path("/workspace/nginx/projects")
        nginx_conf_dst_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["cp", "-f", str(nginx_conf_src), str(nginx_conf_dst_dir)],
                check=False,
                universal_newlines=True,
            )
            subprocess.run(["docker", "restart", "nginx"], check=False, universal_newlines=True)
        except Exception as exc:
            print(f"⚠️ 同步 nginx 配置失败: {exc}")
    except subprocess.CalledProcessError as exc:
        print(f"命令执行失败: {exc}")
        sys.exit(exc.returncode or 1)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"发生错误: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
