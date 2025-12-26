#!/usr/bin/env python3
"""
EMQX 自动化安装脚本（本地环境）。

功能：
1. 随机生成 dashboard 管理员密码（用户名固定为 admin）。
2. 将凭证写入 /workspace/isw-helper/output/deploy_credentials.json。
3. 准备持久化目录 /workspace/isw_v2/mqtt_broker/emqx/persist/{data,log}。
4. 删除旧容器（如存在），并使用环境变量启动 emqx/emqx:5.8.0 容器。
"""

from __future__ import annotations

import argparse
import json
import secrets
import string
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict

CONTAINER_NAME = "isw_v2_emqx5.8.0"
IMAGE_NAME = "emqx/emqx:5.8.0"

BASE_DIR = Path("/workspace/isw_v2/mqtt_broker/emqx")
PERSIST_DIR = BASE_DIR / "persist"

CREDENTIAL_FILE = Path("/workspace/isw-helper/output/deploy_credentials.json")


def run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    """执行命令并输出日志。"""
    print(f"→ 执行命令: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, text=True, capture_output=False)


def generate_password(length: int = 20) -> str:
    """生成适合做 Web 登录密码的随机字符串（避免过多奇怪符号）。"""
    alphabet = string.ascii_letters + string.digits + "_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def load_existing_credentials() -> Dict[str, Any] | None:
    """从凭证文件中加载现有的 EMQX 凭证。"""
    if not CREDENTIAL_FILE.exists():
        return None
    try:
        payload = json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        return payload.get("emqx")
    except (json.JSONDecodeError, KeyError):
        return None


def write_credentials(
    username: str,
    password: str,
    ip: str | None = None,
    *,
    dashboard_port: int = 18084,
    update_password: bool = True,
) -> None:
    """将 EMQX 凭证写入 JSON 文件，保留其他条目。

    Args:
        username: 用户名
        password: 密码（仅在 update_password=True 时更新）
        ip: 服务器 IP，用于生成 dashboard_url
        update_password: 是否更新密码（如果容器已存在，应设为 False 以保留旧密码）
    """
    CREDENTIAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {}
    if CREDENTIAL_FILE.exists():
        try:
            payload = json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("⚠️ 现有凭证文件无法解析，将被覆盖。")
            payload = {}

    # 记录直连 EMQX Dashboard/HTTP API 的端口（默认 18084，避免依赖 Nginx 反代的 58084）
    dashboard_url = f"http://{ip}:{dashboard_port}"

    # 如果容器已存在且不更新密码，则保留现有密码（使用凭证文件中的密码）
    if not update_password:
        existing_emqx = payload.get("emqx", {})
        existing_password = existing_emqx.get("password")
        if existing_password:
            password = existing_password
            print(f"⚠️ 检测到容器已存在，保留现有密码（不更新 deploy_credentials.json 中的密码）")
        else:
            # 如果凭证文件中没有密码，仍然使用传入的密码（可能是从其他地方读取的）
            print(f"⚠️ 检测到容器已存在，但凭证文件中无密码，使用传入的密码")

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
        print(f"✓ EMQX dashboard_url 已更新（密码保持不变）")


def ensure_persist_dirs() -> None:
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
            text=True,
        )
        print(f"✓ 持久化目录权限已调整: {PERSIST_DIR}")
    except FileNotFoundError:
        # 没有 chmod（例如在纯 Windows 环境），忽略即可
        print("⚠️ 未找到 chmod 命令，跳过权限设置。")


def container_exists() -> bool:
    """检查容器是否存在（包括运行中和已停止的）。"""
    result = subprocess.run(
        ["docker", "ps", "-a", "-q", "-f", f"name={CONTAINER_NAME}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return bool(result.stdout.strip())


def remove_existing_container() -> None:
    """如有同名容器则删除。"""
    if container_exists():
        print(f"发现已有容器 {CONTAINER_NAME}，尝试删除...")
        subprocess.run(
            ["docker", "rm", "-f", CONTAINER_NAME],
            check=False,
            text=True,
        )
        print("✓ 旧 EMQX 容器已删除")


def start_emqx(username: str, password: str) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="EMQX 自动化安装脚本")
    parser.add_argument(
        "--ip",
        required=True,
        help="EMQX 所在服务器 IP，用于生成 dashboard_url（必填）",
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=18084,
        help="EMQX Dashboard/API 直连端口，默认 18084（避免依赖 Nginx 58084 反代）",
    )
    args = parser.parse_args()

    try:
        ensure_persist_dirs()
        
        # 检查容器是否已存在
        container_already_exists = container_exists()
        
        username = "admin"
        
        # 如果容器已存在，尝试从凭证文件读取现有密码
        should_update_password = True
        if container_already_exists:
            existing_creds = load_existing_credentials()
            if existing_creds and existing_creds.get("password"):
                password = existing_creds["password"]
                should_update_password = False  # 容器已存在且凭证文件中有密码，不更新密码
                print(f"✓ 检测到容器已存在，使用现有密码（从 deploy_credentials.json 读取，不更新密码）")
            else:
                # 如果凭证文件中没有密码，说明持久化数据中可能有密码，但我们无法确定
                # 注意：环境变量只在首次初始化时生效，如果持久化数据已存在，不会更新密码
                print(f"⚠️ 警告：容器已存在但凭证文件中无密码")
                print(f"   由于 EMQX 持久化数据可能已存在，环境变量无法更新密码")
                print(f"   建议：")
                print(f"   1. 手动登录 EMQX Dashboard 查看/修改密码")
                print(f"   2. 或者删除持久化数据目录 {PERSIST_DIR}/data 后重新安装（会丢失所有配置）")
                print(f"   3. 或者手动将实际密码写入 deploy_credentials.json")
                # 仍然生成一个占位密码写入凭证文件，但提示用户这不会生效
                password = generate_password()
                should_update_password = True  # 写入占位密码到凭证文件
                print(f"   已生成占位密码并写入凭证文件，但此密码不会生效（容器仍使用持久化数据中的密码）")
        else:
            # 容器不存在，生成新密码
            password = generate_password()
            should_update_password = True
        
        # 删除旧容器（如果存在）
        remove_existing_container()
        
        # 写入凭证：根据 should_update_password 决定是否更新密码
        write_credentials(
            username,
            password,
            ip=args.ip,
            dashboard_port=args.dashboard_port,
            update_password=should_update_password,
        )
        
        # 启动新容器
        start_emqx(username, password)

        print("EMQX 部署完成。")
        # 同步 nginx 配置并重启 nginx（用于 EMQX 反向代理）
        nginx_conf_src = BASE_DIR / "emqx_nginx.conf"
        nginx_conf_dst_dir = Path("/workspace/nginx/projects")
        nginx_conf_dst_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["cp", str(nginx_conf_src), str(nginx_conf_dst_dir)],
                check=True,
                text=True,
            )
            print(f"✓ 已复制 nginx 配置到 {nginx_conf_dst_dir}")
        except subprocess.CalledProcessError as exc:
            print(f"⚠️ 复制 nginx 配置失败: {exc}")
        try:
            subprocess.run(["docker", "restart", "nginx"], check=False, text=True)
            print("✓ 已重启 nginx")
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️ 重启 nginx 失败: {exc}")
    except subprocess.CalledProcessError as exc:
        print(f"命令执行失败: {exc}")
        sys.exit(exc.returncode or 1)
    except Exception as exc:  # noqa: BLE001
        print(f"发生错误: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()


