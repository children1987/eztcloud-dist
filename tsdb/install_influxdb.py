#!/usr/bin/env python3
"""
InfluxDB 初始化与启动脚本。

职责：
1. 随机生成 DOCKER_INFLUXDB_INIT_PASSWORD 与 INFLUXDB_TOKEN。
2. 将凭证写入 /workspace/isw-helper/output/deploy_credentials.json。
3. 使用生成的凭证启动 InfluxDB Docker 容器。
"""

from __future__ import annotations

import json
import secrets
import string
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any

CONTAINER_NAME = "isw_v2_influxdb"
IMAGE_NAME = "influxdb:2.7-alpine"

DATA_DIR = Path("/workspace/isw_v2/influxdb/data")
CONFIG_DIR = Path("/workspace/isw_v2/influxdb/config")

CREDENTIAL_FILE = Path("/workspace/isw-helper/output/deploy_credentials.json")


def run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    """执行子进程命令并输出日志。"""
    print(f"→ 执行命令: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, text=True, capture_output=False)


def generate_password(length: int = 24) -> str:
    """生成适用于环境变量的随机密码。"""
    alphabet = string.ascii_letters + string.digits + "_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_token() -> str:
    """生成高熵 token。"""
    return secrets.token_hex(32)


def container_exists() -> bool:
    """检查容器是否存在（包括运行中和已停止的）。"""
    result = subprocess.run(
        ["docker", "ps", "-a", "-q", "-f", f"name={CONTAINER_NAME}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return bool(result.stdout.strip())


def load_existing_credentials() -> Dict[str, Any] | None:
    """从凭证文件中加载现有的 InfluxDB 凭证。"""
    if not CREDENTIAL_FILE.exists():
        return None
    try:
        payload = json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        return payload.get("influxdb")
    except (json.JSONDecodeError, KeyError):
        return None


def write_credentials(password: str, token: str, update_password: bool = True) -> None:
    """将凭证写入 JSON 文件，保留其他条目。

    Args:
        password: 密码（仅在 update_password=True 时更新）
        token: Token（仅在 update_password=True 时更新）
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

    # 如果容器已存在且不更新密码，则保留现有密码和 token
    if not update_password:
        existing_influx = payload.get("influxdb", {})
        existing_password = existing_influx.get("DOCKER_INFLUXDB_INIT_PASSWORD")
        existing_token = existing_influx.get("INFLUXDB_TOKEN")
        if existing_password:
            password = existing_password
        if existing_token:
            token = existing_token
        print(f"⚠️ 检测到容器已存在，保留现有密码和 token（不更新 deploy_credentials.json）")

    payload["influxdb"] = {
        "DOCKER_INFLUXDB_INIT_PASSWORD": password,
        "INFLUXDB_TOKEN": token,
        "updated_at": datetime.now(timezone(timedelta(hours=8))).isoformat()
    }

    CREDENTIAL_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    if update_password:
        print(f"✓ 凭证已写入 {CREDENTIAL_FILE}")
    else:
        print(f"✓ InfluxDB 凭证已更新（密码和 token 保持不变）")


def ensure_directories() -> None:
    """保证 InfluxDB 数据与配置目录存在。"""
    for folder in (DATA_DIR, CONFIG_DIR):
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✓ 目录已准备: {folder}")


def remove_existing_container() -> None:
    """删除同名容器，避免冲突。"""
    if container_exists():
        print(f"发现已有容器 {CONTAINER_NAME}，尝试删除...")
        subprocess.run(
            ["docker", "rm", "-f", CONTAINER_NAME],
            check=False,
            text=True
        )
        print("✓ 旧容器已删除")


def start_container(password: str, token: str) -> None:
    """启动 InfluxDB 容器。"""
    cmd = [
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "--restart", "unless-stopped",
        "--network", "host",
        "-e", "DOCKER_INFLUXDB_INIT_MODE=setup",
        "-e", "DOCKER_INFLUXDB_INIT_USERNAME=admin",
        "-e", f"DOCKER_INFLUXDB_INIT_PASSWORD={password}",
        "-e", "DOCKER_INFLUXDB_INIT_ORG=shhk",
        "-e", "DOCKER_INFLUXDB_INIT_BUCKET=isw2-bucket",
        "-e", f"DOCKER_INFLUXDB_INIT_ADMIN_TOKEN={token}",
        "-e", "DOCKER_INFLUXD_SESSION_LENGTH=1",
        "-v", f"{DATA_DIR}:/var/lib/influxdb2",
        "-v", f"{CONFIG_DIR}:/etc/influxdb2",
        IMAGE_NAME
    ]

    run_command(cmd)
    print(f"✓ 容器 {CONTAINER_NAME} 启动完成")


def main() -> None:
    try:
        ensure_directories()
        
        # 检查容器是否已存在
        container_already_exists = container_exists()
        
        # 如果容器已存在，尝试从凭证文件读取现有密码和 token
        should_update_password = True
        if container_already_exists:
            existing_creds = load_existing_credentials()
            if existing_creds:
                password = existing_creds.get("DOCKER_INFLUXDB_INIT_PASSWORD")
                token = existing_creds.get("INFLUXDB_TOKEN")
                if password and token:
                    should_update_password = False  # 容器已存在且凭证文件中有密码，不更新密码
                    print(f"✓ 检测到容器已存在，使用现有密码和 token（从 deploy_credentials.json 读取，不更新密码）")
                else:
                    # 如果凭证文件中没有密码或 token，说明持久化数据中可能有，但我们无法确定
                    # 注意：环境变量只在首次初始化时生效，如果持久化数据已存在，不会更新密码
                    print(f"⚠️ 警告：容器已存在但凭证文件中缺少密码或 token")
                    print(f"   由于 InfluxDB 持久化数据可能已存在，环境变量无法更新密码")
                    print(f"   建议：")
                    print(f"   1. 手动登录 InfluxDB 查看/修改密码和 token")
                    print(f"   2. 或者删除持久化数据目录 {DATA_DIR} 后重新安装（会丢失所有数据）")
                    print(f"   3. 或者手动将实际密码和 token 写入 deploy_credentials.json")
                    # 仍然生成占位密码和 token 写入凭证文件，但提示用户这不会生效
                    password = generate_password()
                    token = generate_token()
                    should_update_password = True  # 写入占位密码到凭证文件
                    print(f"   已生成占位密码和 token 并写入凭证文件，但此密码不会生效（容器仍使用持久化数据中的密码）")
            else:
                # 凭证文件中没有 influxdb 部分
                password = generate_password()
                token = generate_token()
                should_update_password = True
                print(f"⚠️ 容器已存在但凭证文件中无 InfluxDB 凭证，生成新密码和 token（注意：可能需要手动同步）")
        else:
            # 容器不存在，生成新密码和 token
            password = generate_password()
            token = generate_token()
            should_update_password = True
        
        # 删除旧容器（如果存在）
        remove_existing_container()
        
        # 写入凭证：根据 should_update_password 决定是否更新密码
        write_credentials(password, token, update_password=should_update_password)
        
        # 启动新容器
        start_container(password, token)

        print("InfluxDB 部署完成。")
    except subprocess.CalledProcessError as exc:
        print(f"命令执行失败: {exc}")
        sys.exit(exc.returncode or 1)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"发生错误: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

