#!/usr/bin/env python3
"""
EZtCloud (isw_v2) 自动化安装脚本。

目标：复现《部署指导_local.md》中“本地部署”流程，串联以下步骤：
1. 安装并初始化 InfluxDB、EMQX（依赖已有 install_influxdb.py / install_emqx.py）。
2. 准备 backend/.env，写入数据库 / InfluxDB / EMQX 所需的变量并复制给 docker-compose。
3. 调用 init_deploy_local.sh 构建并启动全部容器。
4. 在容器内创建系统内置用户、超级管理员以及 MQTT/TCP 基础数据。
5. 运行 backend/init_emqx.py 完成 EMQX 认证配置、导入 MQTT 用户，然后刷新容器。

脚本依赖 /workspace/isw-helper/output/deploy_credentials.json 作为统一凭证存储，
deploy_all.py 亦会复用该文件，因此本脚本统一对其进行读写。
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import textwrap
import time
import tempfile
import zipfile
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
DEPLOY_DIR = PROJECT_ROOT / "deploy"
TSDB_INSTALLER = PROJECT_ROOT / "tsdb" / "install_influxdb.py"
EMQX_INSTALLER = PROJECT_ROOT / "mqtt_broker" / "emqx" / "install_emqx.py"
BACKEND_ENV = BACKEND_DIR / ".env"
BACKEND_ENV_EXAMPLE = BACKEND_ENV.with_suffix(".env.example")
WORKSPACE = Path("/workspace")
DEFAULT_CREDENTIAL_PATH = WORKSPACE / "isw-helper" / "output" / "deploy_credentials.json"
# 兼容在非 /workspace 环境调试：如果不存在则尝试相对路径
if DEFAULT_CREDENTIAL_PATH.parent.exists():
    CREDENTIALS_FILE = DEFAULT_CREDENTIAL_PATH
else:
    CREDENTIALS_FILE = (PROJECT_ROOT.parent / "isw-helper" / "output" / "deploy_credentials.json").resolve()

CONTAINER_WEB = "isw_v2_web_server"
PROJECT_NAME = "isw_v2"
DEFAULT_DB_NAME = "isw"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_PORT = "55432"
DEFAULT_EMQX_API_PORT = "58084"
DEFAULT_INFLUX_URL = "http://127.0.0.1:8086"
DEFAULT_INFLUX_BUCKET = "isw2-bucket"

DEFAULT_BROKER_PORT = "7883"
DEFAULT_BROKER_TLS_PORT = "7885"
DEFAULT_TCP_PORT = "6879"

# username -> (env_username_key, env_password_key) 列表
MQTT_ENV_MAPPING: Dict[str, List[Tuple[str, str]]] = {
    "SU_down_sender": [("DOWN_SENDER_MQTT_USERNAME", "DOWN_SENDER_MQTT_PASSWORD")],
    "SU_up_worker": [("UP_WORKER_MQTT_USERNAME", "UP_WORKER_MQTT_PASSWORD")],
    "SU_notifier": [("NOTIFIER_MQTT_USERNAME", "NOTIFIER_MQTT_PASSWORD")],
    "SU_device_monitor": [("DEVICE_MONITOR_MQTT_USERNAME", "DEVICE_MONITOR_MQTT_PASSWORD")],
    "SU_device_shadow": [("DEVICE_SHADOW_MQTT_USERNAME", "DEVICE_SHADOW_MQTT_PASSWORD")],
    "SU_task_engine": [("TASK_MQTT_USERNAME", "TASK_MQTT_PASSWORD")],
    "SU_scene_engine": [("SCENE_MQTT_USERNAME", "SCENE_MQTT_PASSWORD")],
    "SU_rule_engine": [("RULE_MQTT_USERNAME", "RULE_MQTT_PASSWORD")],
    "SU_mqtt_receiver": [("RECEIVER_MQTT_USERNAME", "RECEIVER_MQTT_PASSWORD")],
    "SU_alarm_engine": [("ALARM_MQTT_USERNAME", "ALARM_MQTT_PASSWORD")],
    "SU_web_server": [("WEB_SERVER_MQTT_USERNAME", "WEB_SERVER_PASSWORD")],
    "SU_mqtt_sender": [("MQTT_SENDER_USERNAME", "MQTT_SENDER_PASSWORD")],
    "SU_topic_transfer": [("TOPIC_TRANSFER_MQTT_USERNAME", "TOPIC_TRANSFER_MQTT_PASSWORD")],
    "SU_telegraf_ro": [("TELEGRAF_MQTT_RO_USER", "TELEGRAF_MQTT_RO_PASSWORD")],
}

# username -> client_id 环境变量名（值固定等于 username）
MQTT_CLIENT_ID_ENV: Dict[str, str] = {
    "SU_alarm_engine": "ALARM_MQTT_CLIENT_ID",
    "SU_down_sender": "DOWN_SENDER_MQTT_CLIENT_ID",
    "SU_mqtt_receiver": "RECEIVER_MQTT_CLIENT_ID",
    "SU_rule_engine": "RULE_MQTT_CLIENT_ID",
    "SU_scene_engine": "SCENE_MQTT_CLIENT_ID",
    "SU_task_engine": "TASK_MQTT_CLIENT_ID",
    "SU_device_shadow": "DEVICE_SHADOW_MQTT_CLIENT_ID",
    "SU_device_monitor": "DEVICE_MONITOR_MQTT_CLIENT_ID",
    "SU_up_worker": "UP_WORKER_MQTT_CLIENT_ID",
    "SU_notifier": "NOTIFIER_MQTT_CLIENT_ID",
}

# 系统用户配置：用户名 -> (环境变量用户名键, 环境变量密码键)
SYSTEM_USERS_CONFIG: List[Tuple[str, str, str]] = [
    ("SU_device_shadow", "DEVICE_SHADOW_API_USER", "DEVICE_SHADOW_API_TOKEN"),
    ("SU_alarm_engine", "ALARM_ENGINE_API_USER", "ALARM_ENGINE_API_TOKEN"),
    ("SU_rule_engine", "RULE_ENGINE_API_USER", "RULE_ENGINE_API_TOKEN"),
    ("SU_tcp_server", "TCP_SERVER_API_USER", "TCP_SERVER_API_TOKEN"),
    ("SU_mcq", "SU_MCQ_API_USER", "SU_MCQ_API_TOKEN"),
]


class InstallError(RuntimeError):
    """用户友好的异常提示。"""


def generate_password(length: int = 32) -> str:
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    first = secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
    rest = "".join(secrets.choice(charset) for _ in range(length - 1))
    return first + rest


class IswInstaller:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.credentials: Dict[str, Any] = self._load_credentials()

    # ------------------------------------------------------------------ utils
    def _load_credentials(self) -> Dict[str, Any]:
        if CREDENTIALS_FILE.exists():
            try:
                with CREDENTIALS_FILE.open("r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    if isinstance(data, dict):
                        return data
            except Exception as exc:  # pylint: disable=broad-except
                print(f"⚠️ 读取 {CREDENTIALS_FILE} 失败，将重新生成: {exc}")
        return {}

    def _save_credentials(self) -> None:
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CREDENTIALS_FILE.open("w", encoding="utf-8") as fp:
            json.dump(self.credentials, fp, indent=2, ensure_ascii=False)
        os.chmod(CREDENTIALS_FILE, 0o600)

    def _reload_credentials(self) -> None:
        self.credentials = self._load_credentials()

    def _run(
        self,
        cmd: Sequence[str],
        *,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = True,
        capture: bool = False,
        timeout: Optional[int] = None,
    ) -> subprocess.CompletedProcess | str:
        display = " ".join(cmd)
        print(f"→ 执行命令: {display}")
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=full_env,
            text=True,
            capture_output=capture,
            check=check,
            timeout=timeout,
        )
        if capture:
            return (result.stdout or "").strip()
        return result

    def _ensure_backend_env(self) -> None:
        """确保 backend/.env 存在。

        优先使用 .env.example 作为模板；若两者都不存在，则创建一个空的 .env，
        后续由 _update_env_file 逐步写入所需键值，避免打断自动化部署流程。
        """
        if BACKEND_ENV.exists():
            return
        BACKEND_ENV.parent.mkdir(parents=True, exist_ok=True)
        if BACKEND_ENV_EXAMPLE.exists():
            shutil.copy2(BACKEND_ENV_EXAMPLE, BACKEND_ENV)
            print(f"✓ 已复制 {BACKEND_ENV_EXAMPLE} → {BACKEND_ENV}")
        else:
            BACKEND_ENV.write_text("# 自动创建的占位 .env，将在安装过程中补全关键配置。\n", encoding="utf-8")
            print(f"✓ 未找到 {BACKEND_ENV_EXAMPLE}，已创建空的 {BACKEND_ENV}")

    def _load_env_map(self) -> Dict[str, str]:
        if not BACKEND_ENV.exists():
            return {}
        data: Dict[str, str] = {}
        with BACKEND_ENV.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
        return data

    def _update_env_file(self, updates: Dict[str, Optional[str]]) -> None:
        if not updates:
            return
        self._ensure_backend_env()
        existing_lines: List[str] = []
        if BACKEND_ENV.exists():
            existing_lines = BACKEND_ENV.read_text(encoding="utf-8").splitlines()
        handled: set[str] = set()
        new_lines: List[str] = []
        for line in existing_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in line:
                new_lines.append(line)
                continue
            key, _ = line.split("=", 1)
            key = key.strip()
            if key in updates and updates[key] is not None:
                new_lines.append(f"{key}={updates[key]}")
                handled.add(key)
            else:
                new_lines.append(line)
        for key, value in updates.items():
            if value is None or key in handled:
                continue
            new_lines.append(f"{key}={value}")
        BACKEND_ENV.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"✓ 已更新 backend/.env 中的 {', '.join(updates.keys())}")

    def _copy_env_to_deploy(self) -> None:
        target = DEPLOY_DIR / ".env"
        shutil.copy2(BACKEND_ENV, target)
        print(f"✓ 已同步 backend/.env → {target}")

    def _copy_public_key(self) -> None:
        """复制 IAM 公钥到 isw_v2，需在 docker-compose build 前完成。"""
        src = WORKSPACE / "iam" / "iam" / "security" / "public.pem"
        dest = BACKEND_DIR / "security" / "public.pem"
        if not src.exists():
            print(f"⚠️ 未找到 IAM 公钥 {src}，跳过复制")
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"✓ 已复制 IAM 公钥到 {dest}")

    def _wait_for_container(self, name: str, timeout: int = 180) -> bool:
        print(f"等待容器 {name} 启动...")
        for _ in range(timeout):
            status = self._run(
                ["docker", "ps", "--filter", f"name={name}", "--format", "{{.Status}}"],
                capture=True,
                check=False,
            )
            text = status if isinstance(status, str) else ""
            if text.strip().startswith("Up"):
                print(f"✓ 容器 {name} 状态: {text.strip()}")
                return True
            time.sleep(1)
        print(f"⚠️ 容器 {name} 在 {timeout}s 内未就绪。")
        return False

    def _ensure_admin(self) -> None:
        """确保数据库凭证已保存，不处理 eztcloud admin（应从 IAM 同步）"""
        changed = False
        pg_section = self.credentials.setdefault("postgres", {})
        if self.args.db_password:
            if pg_section.get("password") != self.args.db_password:
                pg_section["password"] = self.args.db_password
                changed = True
        elif not pg_section.get("password"):
            raise InstallError("缺少 --db-password，且 deploy_credentials.json 中也未记录 postgres 密码。")

        if changed:
            self._save_credentials()
            print("✓ 已更新 deploy_credentials.json 中的数据库凭证。")

    def _sync_user_from_iam(self, username: str, password: str) -> None:
        """在容器内使用 Django 管理命令从 IAM 同步用户
        
        Args:
            username: IAM 用户名
            password: IAM 用户密码
            
        Raises:
            InstallError: 如果命令执行失败或同步失败
        """
        # 获取 IAM 基地址
        oauth_base = f"http://{self.args.ip}:8081/"
        
        # 使用 Django 管理命令同步用户（命令会自动从 IAM 获取数据）
        result = self._run_manage(
            "sync_user",
            "--username", username,
            "--password", password,
            "--iam-base", oauth_base,
            capture=True,
            check=False,
        )
        
        # 处理输出
        if isinstance(result, str):
            output = result.strip()
            print(output)
            
            # 检查是否有错误标记
            if "✗" in output or "ERROR" in output or "Exception" in output or "Traceback" in output:
                raise InstallError(f"同步用户时发生错误，请查看上面的错误信息")
            
            # 检查是否有成功信息
            if "✓" not in output and "SUCCESS" not in output:
                raise InstallError(f"同步用户未返回成功信息，输出: {output}")
        else:
            # 如果不是字符串，可能是 CompletedProcess，检查退出码
            if hasattr(result, 'returncode') and result.returncode != 0:
                raise InstallError(f"同步用户命令执行失败，退出码: {result.returncode}")

    def _sync_admin_from_iam(self) -> None:
        """从 IAM 同步 admin 用户到 eztcloud"""
        # 获取 IAM admin 凭证
        iam_admin = self.credentials.get("iam_admin", {})
        username = iam_admin.get("username", "admin")
        password = iam_admin.get("password")
        
        if not password:
            print("⚠️ 未找到 IAM admin 密码，跳过从 IAM 同步 admin 用户。")
            print("   提示：请确保 deploy_credentials.json 中包含 iam_admin.password")
            return
        
        try:
            print(f"正在从 IAM 同步 admin 用户 ({username})...")
            # 使用 Django 管理命令，命令会自动从 IAM 获取用户数据并同步
            self._sync_user_from_iam(username, password)
            print("✓ 已从 IAM 同步 admin 用户到 eztcloud")
        except InstallError:
            # InstallError 已经包含详细的错误信息，直接抛出
            raise
        except Exception as e:
            raise InstallError(f"同步用户时发生错误: {str(e)}")

    def _ensure_system_users_credentials(self) -> None:
        """生成并保存系统用户密码到 deploy_credentials.json"""
        changed = False
        system_users_section = self.credentials.setdefault("system_users", {})
        
        for username, user_env_key, token_env_key in SYSTEM_USERS_CONFIG:
            # 如果凭证文件中已有该用户的密码，则保留；否则生成新密码
            if username not in system_users_section:
                system_users_section[username] = {
                    "username": username,
                    "password": generate_password(32),
                }
                changed = True
                print(f"✓ 已为系统用户 {username} 生成密码")
        
        if changed:
            self._save_credentials()
            print("✓ 已更新 deploy_credentials.json 中的系统用户凭证。")

    # ------------------------------------------------------------------ installers
    def _install_influxdb(self) -> None:
        if self.args.skip_influx:
            print("跳过 InfluxDB 安装（--skip-influx）")
            return
        if not TSDB_INSTALLER.exists():
            raise InstallError(f"缺少 {TSDB_INSTALLER}，无法安装 InfluxDB。")
        self._run(["python3", str(TSDB_INSTALLER)])
        self._reload_credentials()

    def _install_emqx(self) -> None:
        if self.args.skip_emqx:
            print("跳过 EMQX 安装（--skip-emqx）")
            return
        if not EMQX_INSTALLER.exists():
            raise InstallError(f"缺少 {EMQX_INSTALLER}，无法安装 EMQX。")
        # 将用户选择的 IP 传递给 EMQX 安装脚本，用于生成 dashboard_url
        self._run(["python3", str(EMQX_INSTALLER), "--ip", self.args.ip])
        self._reload_credentials()

    # ------------------------------------------------------------------ env sync
    def _sync_basic_env(self) -> None:
        env_map = self._load_env_map()
        pg = self.credentials.get("postgres", {})
        influx = self.credentials.get("influxdb", {})
        emqx = self.credentials.get("emqx", {})
        oauth = self.credentials.get("iam_client_eztcloud", {})

        def _require_oauth_field(key: str) -> str:
            value = oauth.get(key)
            if not value:
                raise InstallError(
                    f"deploy_credentials.json 中缺少 iam_client_eztcloud.{key}，"
                    "请先在 IAM 容器内执行 ensure_iam_clients 生成凭据，"
                    "或重新运行 deploy_all.py 获取最新凭据。"
                )
            return value

        # OAuth Provider 基地址直接使用当前部署 IP 的 8081 端口，避免从 redirect/webhook 推导出错误域名
        oauth_base = f"http://{self.args.ip}:8081/"
        oauth_client_id = _require_oauth_field("client_id")
        oauth_client_secret = _require_oauth_field("client_secret")
        oauth_webhook_secret = _require_oauth_field("webhook_secret")
        updates = {
            # 基本项目信息
            "PROJ_NAME": env_map.get("PROJ_NAME", "isw_v2"),
            "DEBUG": env_map.get("DEBUG", "False"),
            # 随机密钥：如已有则尊重已有配置
            "SECRET_KEY": env_map.get("SECRET_KEY") or generate_password(50),
            "JWT_SECRET_KEY": env_map.get("JWT_SECRET_KEY") or generate_password(50),
            # COS 默认关闭，本地部署通常不启用云存储
            "USE_COS": env_map.get("USE_COS", "False"),
            # 数据库
            "DATABASE_NAME": env_map.get("DATABASE_NAME", self.args.db_name),
            "DATABASE_USER": env_map.get("DATABASE_USER", self.args.db_user),
            # 数据库密码优先使用 deploy_credentials.json，避免沿用旧的占位值
            "DATABASE_PASSWORD": pg.get("password") or env_map.get("DATABASE_PASSWORD"),
            # 数据库主机：默认直接使用用户选择的 IP，便于容器访问宿主机
            "DATABASE_HOST": env_map.get("DATABASE_HOST", self.args.ip),
            "DATABASE_PORT": env_map.get("DATABASE_PORT", self.args.db_port),
            # 时序数据库（本地默认使用 InfluxDB）
            "TSDB_TYPE": env_map.get("TSDB_TYPE", "influxdb"),
            "INFLUXDB_URL": env_map.get("INFLUXDB_URL", self.args.influx_url),
            "INFLUXDB_TOKEN": env_map.get("INFLUXDB_TOKEN", influx.get("INFLUXDB_TOKEN")),
            "INFLUXDB_BUCKET": env_map.get("INFLUXDB_BUCKET", influx.get("INFLUXDB_BUCKET", DEFAULT_INFLUX_BUCKET)),
            "INFLUXDB_ORG": env_map.get("INFLUXDB_ORG", "shhk"),
            # Redis / API
            "REDIS_HOST": env_map.get("REDIS_HOST", "127.0.0.1"),
            "REDIS_PORT": env_map.get("REDIS_PORT", "48025"),
            "API_HOST": env_map.get("API_HOST", "https://api.eztcloud.com/"),
            # TCP Server 配置（固定默认值）
            "TCP_SERVER_HOST": env_map.get("TCP_SERVER_HOST", "127.0.0.1"),
            "TCP_SERVER_PORT": env_map.get("TCP_SERVER_PORT", "56879"),
            "TCP_MAX_LISTEN_COUNT": env_map.get("TCP_MAX_LISTEN_COUNT", "1024"),
            # MQTT / EMQX 基础配置
            "MQTT_HOST": env_map.get("MQTT_HOST", self.args.ip),
            "MQTT_PORT": env_map.get("MQTT_PORT", self.args.mqtt_port),
            "MQTT_TLS": env_map.get("MQTT_TLS", "False"),
            "EMQX_API_HOST": env_map.get("EMQX_API_HOST", self.args.ip),
            "EMQX_API_PORT": env_map.get("EMQX_API_PORT", self.args.emqx_api_port),
            "EMQX_API_PROTOCOL": env_map.get("EMQX_API_PROTOCOL", "http"),
            # EMQX 节点 IP 列表（单机部署默认 127.0.0.1）
            "EMQX_IPS": env_map.get("EMQX_IPS", "127.0.0.1"),
            # 提前占位，避免 Django settings 在 init_emqx 之前因缺少变量而报错
            "EMQX_ACCOUNT": env_map.get("EMQX_ACCOUNT", ""),
            "EMQX_PASSWORD": env_map.get("EMQX_PASSWORD", ""),
            # OAuth2 （对接 IAM）
            "OAUTH2_PROVIDER_URL_BASE": oauth_base,
            "OAUTH2_CLIENT_ID": oauth_client_id,
            "OAUTH2_CLIENT_SECRET": oauth_client_secret,
            "OAUTH2_CLIENT_WEBHOOK_SECRET": oauth_webhook_secret,
            # AI Chat（固定默认值，可在 .env 中覆盖）
            "DASHSCOPE_APP_ID": env_map.get(
                "DASHSCOPE_APP_ID",
                "5a57053afaac44b49d134379e2ae215f",
            ),
            "DASHSCOPE_API_KEY": env_map.get(
                "DASHSCOPE_API_KEY",
                "sk-xxx",
            ),
            # 萤石摄像头产品码（固定默认值，可在 .env 中覆盖）
            "EZVIZ_CAMERA_PRODUCT_CODE": env_map.get(
                "EZVIZ_CAMERA_PRODUCT_CODE",
                "ezviz.camera.common.4",
            ),
            # 微信配置（固定默认值，可在 .env 中覆盖）
            "WECHAT_APPID": env_map.get("WECHAT_APPID", "wxxxx"),
            "WECHAT_APPSECRET": env_map.get("WECHAT_APPSECRET", "xxx"),
            "WECHAT_TOKEN": env_map.get("WECHAT_TOKEN", "xxx"),
            "WECHAT_CALLBACK_KEY": env_map.get("WECHAT_CALLBACK_KEY", "isw"),
            # 短信配置（固定默认值，可在 .env 中覆盖）
            "SMS_SECRET_ID": env_map.get("SMS_SECRET_ID", "AKIDvkZL6lGXkz8EJC3wshVHvV5TdeXCbtAJ"),
            "SMS_SECRET_KEY": env_map.get("SMS_SECRET_KEY", ""),
            "SMS_APP_ID": env_map.get("SMS_APP_ID", "1400816627"),
            "SMS_ID_REGISTER_INVITE": env_map.get("SMS_ID_REGISTER_INVITE", "1796355"),
            "SMS_ID_COMMON_VERIFY": env_map.get("SMS_ID_COMMON_VERIFY", "1794605"),
            "SMS_ID_ALARM_MESSAGE": env_map.get("SMS_ID_ALARM_MESSAGE", "2502956"),
            "SMS_ID_ALARM_RESTORED": env_map.get("SMS_ID_ALARM_RESTORED", "2502960"),
            "SMS_ID_ALARM_ONGOING": env_map.get("SMS_ID_ALARM_ONGOING", "2502959"),
            # 前端目录
            "FRONTEND_DIR_NAME": env_map.get("FRONTEND_DIR_NAME", "frontend_dist_local"),
        }
        self._update_env_file(updates)

    def _sync_system_users_env(self) -> None:
        """从 deploy_credentials.json 读取系统用户凭证并写入 .env 文件"""
        system_users = self.credentials.get("system_users", {})
        if not system_users:
            print("⚠️ 未在凭证文件中找到 system_users，跳过系统用户环境变量写入。")
            return
        
        updates: Dict[str, Optional[str]] = {}
        for username, user_env_key, token_env_key in SYSTEM_USERS_CONFIG:
            user_info = system_users.get(username, {})
            user_value = user_info.get("username", username)
            password = user_info.get("password")
            
            if password:
                updates[user_env_key] = user_value
                updates[token_env_key] = password
            else:
                print(f"⚠️ 系统用户 {username} 缺少密码，跳过写入环境变量。")
        
        if updates:
            self._update_env_file(updates)
            print("✓ 已更新 backend/.env 中的系统用户环境变量。")
        else:
            print("⚠️ 未找到可写入的系统用户凭证。")

    def _ensure_mqtt_internal_users(self) -> None:
        """确保 deploy_credentials.json 中有 internal_users（如果不存在则提前生成）。"""
        emqx = self.credentials.get("emqx", {})
        users = emqx.get("internal_users")
        if isinstance(users, list) and len(users) > 0:
            print(f"✓ deploy_credentials.json 中已有 {len(users)} 个 internal_users")
            return
        
        # 如果不存在，提前生成 internal_users（与 init_emqx.py 中的逻辑一致）
        print("⚠️ deploy_credentials.json 中未找到 internal_users，提前生成...")
        # INTERNAL_USER_TEMPLATES 与 init_emqx.py 保持一致
        internal_user_templates = [
            {"username": "frontend"},
            {"username": "SU_telegraf_ro"},
            {"username": "SU_mqtt_receiver"},
            {"username": "SU_reader"},
            {"username": "SU_down_sender"},
            {"username": "SU_up_worker"},
            {"username": "SU_web_server"},
            {"username": "SU_rule_engine"},
            {"username": "SU_task_engine"},
            {"username": "SU_scene_engine"},
            {"username": "SU_alarm_engine"},
            {"username": "SU_device_shadow"},
            {"username": "SU_device_monitor"},
            {"username": "SU_notifier"},
            {"username": "mcp_server"},
            {"username": "SU_mqtt_sender"},
            {"username": "SU_topic_transfer"},
            {"username": "SU_mcq"},
        ]
        
        generated_users = []
        for tmpl in internal_user_templates:
            username = tmpl["username"]
            pwd = generate_password(24)  # 使用与 init_emqx.py 相同的密码长度
            generated_users.append({
                "username": username,
                "password": pwd,
                "is_superuser": tmpl.get("is_superuser", False),
            })
        
        emqx["internal_users"] = generated_users
        self.credentials["emqx"] = emqx
        self._save_credentials()
        print(f"✓ 已生成 {len(generated_users)} 个 internal_users 并保存到 deploy_credentials.json")

    def _sync_mqtt_credentials(self) -> None:
        emqx = self.credentials.get("emqx", {})
        users = emqx.get("internal_users")
        if not isinstance(users, list):
            print("⚠️ 未在凭证文件中找到 emqx.internal_users，跳过 MQTT 账号写入。")
            return
        user_map = {item.get("username"): item.get("password") for item in users if item.get("username")}
        updates: Dict[str, Optional[str]] = {}
        for username, pairs in MQTT_ENV_MAPPING.items():
            password = user_map.get(username)
            if not password:
                continue
            for user_key, pwd_key in pairs:
                updates[user_key] = username
                updates[pwd_key] = password
            # 同步 client_id，固定等于用户名
            client_id_key = MQTT_CLIENT_ID_ENV.get(username)
            if client_id_key:
                updates[client_id_key] = username
        if updates:
            self._update_env_file(updates)
            print(f"✓ 已更新 backend/.env 中的 {len(updates)} 个 MQTT 用户环境变量")
        else:
            print("⚠️ 未找到可写入的 MQTT 用户凭证，可能 install_emqx.py 尚未生成 internal_users。")

    def _sync_emqx_api_credentials(self) -> None:
        emqx = self.credentials.get("emqx", {})
        api_key = emqx.get("api_key")
        api_secret = emqx.get("api_secret")
        if not api_key or not api_secret:
            print("⚠️ emqx API key/secret 尚未生成（可能 init_emqx.py 未成功），跳过写入 .env。")
            return
        self._update_env_file(
            {
                "EMQX_ACCOUNT": api_key,
                "EMQX_PASSWORD": api_secret,
            }
        )

    # ------------------------------------------------------------------ docker helpers
    def _run_init_deploy(self) -> None:
        if self.args.skip_docker:
            print("跳过 docker 构建/启动（--skip-docker）")
            return
        script = DEPLOY_DIR / "init_deploy_local.sh"
        if not script.exists():
            raise InstallError(f"缺少 {script}，无法继续。")
        env = {}
        influx = self.credentials.get("influxdb", {})
        token = influx.get("INFLUXDB_TOKEN")
        if token:
            env["INFLUXDB_TOKEN"] = token
        # 设置 Docker Compose 超时时间（5分钟），避免创建大量容器时超时
        env["COMPOSE_HTTP_TIMEOUT"] = "300"
        self._run(["bash", str(script)], cwd=DEPLOY_DIR, env=env or None)

    def _docker_compose_up(self) -> None:
        self._run(["docker-compose", "-p", PROJECT_NAME, "up", "-d"], cwd=DEPLOY_DIR)

    def _restart_container(self, name: str) -> None:
        self._run(["docker", "restart", name], check=False)

    # ------------------------------------------------------------------ django helpers
    def _run_manage(
        self,
        *manage_args: str,
        check: bool = True,
        capture: bool = False,
        extra_env: Optional[Dict[str, str]] = None,
    ) -> subprocess.CompletedProcess | str:
        cmd: List[str] = ["docker", "exec"]
        if extra_env:
            for key, value in extra_env.items():
                cmd.extend(["-e", f"{key}={value}"])
        cmd.extend([CONTAINER_WEB, "python", "manage.py"])
        cmd.extend(manage_args)
        return self._run(cmd, check=check, capture=capture)

    def _create_mqtt_tcp_server_records(self) -> None:
        cmd = ["createmqttbroker", self.args.ip, self.args.mqtt_port, self.args.mqtt_tls_port]
        result = self._run_manage(*cmd, capture=True, check=False)
        if isinstance(result, str) and result:
            out = result.lower()
            if "already exists" in out:
                print("MQTT Broker 记录已存在，跳过。")
            else:
                print(result)
        cmd = ["createtcpserver", self.args.ip, self.args.tcp_port]
        result = self._run_manage(*cmd, capture=True, check=False)
        if isinstance(result, str) and result:
            out = result.lower()
            if "already exists" in out:
                print("TCP Server 记录已存在，跳过。")
            else:
                print(result)

    def _wait_for_migrations(self, timeout: int = 180) -> bool:
        """等待容器内的 migrate 完成。
        
        通过轮询 `migrate --check` 的退出码来判断：
        - 返回 0：没有未应用的迁移，migrate 已完成
        - 返回非零：仍有未应用的迁移，继续等待
        
        这样可以避免安装脚本与容器启动时的 migrate 并发冲突。
        """
        print("等待容器内的 Django migrate 完成...")
        for i in range(timeout):
            # migrate --check 如果有未应用的迁移会返回非零退出码，如果没有则返回 0
            # capture=False 以获取 CompletedProcess 对象，才能检查 returncode
            result = self._run_manage("migrate", "--check", check=False, capture=False)
            if isinstance(result, subprocess.CompletedProcess):
                if result.returncode == 0:
                    print("✓ Django migrate 已完成")
                    return True
            # 每 3 秒检查一次，避免过于频繁
            if i % 3 == 0 and i > 0:
                print(f"  等待中... ({i}/{timeout}s)")
            time.sleep(1)
        print(f"⚠️ Django migrate 在 {timeout}s 内未完成。")
        return False

    def _run_init_emqx_script(self) -> None:
        if self.args.skip_emqx_init:
            print("跳过 backend/init_emqx.py（--skip-emqx-init）")
            return
        script = BACKEND_DIR / "init_emqx.py"
        if not script.exists():
            print("⚠️ 未找到 backend/init_emqx.py，跳过。")
            return
        emqx = self.credentials.get("emqx", {})
        dashboard_password = emqx.get("password")
        if not dashboard_password:
            raise InstallError("deploy_credentials.json 中缺少 emqx.password，请先执行 install_emqx.py。")
        self._run(
            ["python3", str(script), dashboard_password],
            cwd=BACKEND_DIR,
        )
        self._reload_credentials()

    # ------------------------------------------------------------------ pipeline
    def run(self) -> None:
        # 仅执行公共产品导入（阶段9），跳过其他步骤
        if getattr(self.args, "only_import_public_products", False):
            print("\n=== 仅执行公共产品导入（gitee） ===")
            self._import_public_products()
            return

        if not self.args.ip:
            raise InstallError("--ip 是必需参数，用于创建 MQTT/TCP 记录。")
        if not self.args.db_password:
            raise InstallError("--db-password 是必需参数")
        self._ensure_backend_env()
        self._ensure_admin()
        self._ensure_system_users_credentials()

        print("\n=== 阶段 1：安装 InfluxDB ===")
        self._install_influxdb()

        print("\n=== 阶段 2：安装 EMQX ===")
        self._install_emqx()

        print("\n=== 阶段 3：同步 .env（数据库 / InfluxDB / MQTT 基础配置） ===")
        # 先写入基础配置（DB / Influx / Redis / MQTT / EMQX API 等）
        self._sync_basic_env()
        # 写入系统用户环境变量
        self._sync_system_users_env()

        print("\n=== 阶段 4：初始化 EMQX 账号与 MQTT 用户（预检查） ===")
        # 确保 deploy_credentials.json 中有 internal_users（如果不存在则提前生成）
        # 这样在 docker-compose up 之前，.env 文件就包含所有必要的 MQTT 用户环境变量
        self._ensure_mqtt_internal_users()
        self._reload_credentials()  # 重新加载以获取刚生成的 internal_users
        self._sync_mqtt_credentials()
        # 如果已有 API 凭证，也先写入
        self._sync_emqx_api_credentials()
        # 复制 IAM 公钥，确保 docker-compose build 前后端可获取最新公钥
        self._copy_public_key()
        # 把已经补全的 backend/.env 同步到 deploy/.env，供 docker-compose 使用
        self._copy_env_to_deploy()

        print("\n=== 阶段 5：docker 构建 / 启动 ===")
        self._run_init_deploy()

        if self.args.skip_post:
            print("根据参数 --skip-post，跳过后续 Django 初始化步骤。")
            self._print_summary()
            return

        if not self._wait_for_container(CONTAINER_WEB, timeout=240):
            raise InstallError(f"{CONTAINER_WEB} 未就绪，无法继续。")

        print("\n=== 阶段 5.5：等待 Django migrate 完成 ===")
        # 等待容器启动命令中的 migrate 完成（容器启动时会检查并执行 migrate）
        # 这样可以避免安装脚本与容器启动时的 migrate 并发冲突
        if not self._wait_for_migrations(timeout=180):
            raise InstallError("Django migrate 未完成，无法继续。")

        print("\n=== 阶段 6：初始化 EMQX 账号与 MQTT 用户 ===")
        # 此时容器已启动，可以运行 init_emqx.py
        # 调用 backend/init_emqx.py：创建 API key、webhook、认证配置、internal_users 等
        self._run_init_emqx_script()
        # 重新同步 EMQX API 凭证（init_emqx.py 可能创建了新的）
        self._sync_emqx_api_credentials()
        # 重新同步 MQTT 用户凭证（init_emqx.py 可能创建了新的 internal_users）
        self._sync_mqtt_credentials()
        # 更新 deploy/.env（因为可能新增了 MQTT 用户环境变量）
        self._copy_env_to_deploy()

        print("\n=== 阶段 7：初始化 Django 数据 ===")
        # 准备系统用户凭证 JSON，传递给 initsysusers 命令
        system_users = self.credentials.get("system_users", {})
        credentials_json = {}
        for username, user_env_key, token_env_key in SYSTEM_USERS_CONFIG:
            user_info = system_users.get(username, {})
            user_value = user_info.get("username", username)
            password = user_info.get("password")
            if user_value and password:
                credentials_json[user_value] = password
        
        if credentials_json:
            # 将凭证作为 JSON 字符串传递给命令
            credentials_str = json.dumps(credentials_json)
            self._run_manage("initsysusers", "--credentials-json", credentials_str, check=False)
        else:
            # 如果没有凭证，仍然尝试从环境变量读取
            self._run_manage("initsysusers", check=False)
        
        print("\n=== 阶段 7.5：从 IAM 同步 admin 用户 ===")
        self._sync_admin_from_iam()
        
        self._restart_container(CONTAINER_WEB)
        if not self._wait_for_container(CONTAINER_WEB, timeout=120):
            raise InstallError(f"{CONTAINER_WEB} 重启失败。")
        self._create_mqtt_tcp_server_records()

        print("\n=== 阶段 8：最终确认 ===")
        self._restart_container(CONTAINER_WEB)
        self._print_summary()
        print("\n=== 阶段 9：导入最新公共产品（gitee） ===")
        self._import_public_products()

    def _print_summary(self) -> None:
        admin = self.credentials.get("iam_admin", {})
        emqx = self.credentials.get("emqx", {})
        influx = self.credentials.get("influxdb", {})
        print("\n部署完成。关键信息：")
        print(f"- 业务访问地址: http://{self.args.ip}:8082")
        print(f"- IAM 管理员账号: {admin.get('username', 'admin')} / {admin.get('password', '<unknown>')}")
        print(f"- EMQX 控制台: http://{self.args.ip}:58084 （admin / {emqx.get('password', '<unknown>')}）")
        print(f"- InfluxDB Token: {influx.get('INFLUXDB_TOKEN', '<unknown>')}")
        print(f"- 凭证文件: {CREDENTIALS_FILE}")
        print("如需补充钉钉/短信等配置，请编辑 backend/.env 后执行 deploy/restart.sh。")

    # ------------------------------------------------------------------ public products from gitee
    def _download_public_products_from_gitee(self) -> Path:
        """
        从公开 gitee 仓库获取最新公共产品（无需 token），并打包成 importer 可识别的 zip。
        逻辑：
          1) git clone --depth=1（优先 master，失败再尝试 main）
          2) 提取 fixed_products/latest 目录
          3) 重新打包为 public_products.zip（包含 manifest.json 与 resources/）
        """
        tmp_dir = Path(tempfile.mkdtemp())
        repo_dir = tmp_dir / "repo"
        output_zip = tmp_dir / "public_products.zip"

        def _clone(branch: str) -> None:
            print(f"克隆公共产品仓库... (branch={branch})")
            url = "https://gitee.com/children1987/eztcloud-public-product.git"
            self._run(
                ["git", "clone", "--depth=1", "--branch", branch, url, str(repo_dir)],
                timeout=120,
                check=True,
            )

        # 尝试 master，失败再尝试 main
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        try:
            _clone("master")
        except Exception as exc_master:  # pylint: disable=broad-except
            print(f"⚠️ 克隆 master 失败，尝试 main：{exc_master}")
            if repo_dir.exists():
                shutil.rmtree(repo_dir, ignore_errors=True)
            _clone("main")

        latest_dir = repo_dir / "fixed_products" / "latest"
        if not latest_dir.exists():
            raise RuntimeError("未在仓库中找到 fixed_products/latest")

        print("重新打包公共产品为 importer 可用格式...")
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(latest_dir):
                for name in files:
                    full_path = Path(root) / name
                    # 以 latest 为根，确保 manifest.json 在 zip 根目录
                    rel_path = full_path.relative_to(latest_dir)
                    zf.write(full_path, rel_path)

        return output_zip

    def _import_public_products(self) -> None:
        """
        将 gitee 最新公共产品导入本地实例。
        步骤：
          1) 下载并重打包公共产品为 zip
          2) 拷贝 zip 至容器 /tmp/public_products.zip
          3) 容器内使用 FixedProductImporter 导入，默认 force_update=True, skip_conflicts=True
        """
        try:
            zip_path = self._download_public_products_from_gitee()
        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️ 下载/打包公共产品失败，跳过导入：{exc}")
            return

        print("将公共产品包拷贝到容器...")
        container_zip = "/tmp/public_products.zip"
        self._run(["docker", "cp", str(zip_path), f"{CONTAINER_WEB}:{container_zip}"])

        print("在容器内导入公共产品...")
        # 获取 IAM admin 用户名（eztcloud 的 admin 用户应该与 IAM 一致）
        iam_admin = self.credentials.get("iam_admin", {})
        username = iam_admin.get("username", "admin")
        
        result = self._run_manage(
            "import_from_zip",
            container_zip,
            "--username", username,
            "--force-update",
            "--skip-conflicts",
            check=False,
            capture=True,
        )
        if isinstance(result, str):
            print(result.strip())
        print("公共产品导入完成。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EZtCloud (isw_v2) 自动化部署脚本")
    parser.add_argument("--ip", required=False, help="服务器 IP（用于 MQTT/TCP 记录、EMQX 配置）")
    parser.add_argument("--db-password", required=False, help="PostgreSQL 数据库密码")
    parser.add_argument(
        "--db-host",
        default=None,
        help="数据库主机（默认同 --ip，如不提供则自动使用 --ip）",
    )
    parser.add_argument("--db-port", default=DEFAULT_DB_PORT, help=f"数据库端口（默认 {DEFAULT_DB_PORT}）")
    parser.add_argument("--db-name", default=DEFAULT_DB_NAME, help=f"数据库名（默认 {DEFAULT_DB_NAME}）")
    parser.add_argument("--db-user", default=DEFAULT_DB_USER, help=f"数据库用户（默认 {DEFAULT_DB_USER}）")
    parser.add_argument("--influx-url", default=DEFAULT_INFLUX_URL, help=f"InfluxDB URL（默认 {DEFAULT_INFLUX_URL}）")
    parser.add_argument("--emqx-api-port", default=DEFAULT_EMQX_API_PORT, help=f"EMQX Dashboard 端口（默认 {DEFAULT_EMQX_API_PORT}）")
    parser.add_argument("--mqtt-port", default=DEFAULT_BROKER_PORT, help=f"MQTT 端口（默认 {DEFAULT_BROKER_PORT}）")
    parser.add_argument("--mqtt-tls-port", default=DEFAULT_BROKER_TLS_PORT, help=f"MQTT TLS 端口（默认 {DEFAULT_BROKER_TLS_PORT}）")
    parser.add_argument("--tcp-port", default=DEFAULT_TCP_PORT, help=f"TCP Server 端口（默认 {DEFAULT_TCP_PORT}）")
    parser.add_argument("--skip-influx", action="store_true", help="跳过 InfluxDB 安装")
    parser.add_argument("--skip-emqx", action="store_true", help="跳过 EMQX 安装")
    parser.add_argument("--skip-docker", action="store_true", help="跳过 init_deploy_local.sh（只生成配置）")
    parser.add_argument("--skip-post", action="store_true", help="跳过 Django/EMQX 后续初始化")
    parser.add_argument("--skip-emqx-init", action="store_true", help="跳过 backend/init_emqx.py")
    parser.add_argument(
        "--only-import-public-products",
        action="store_true",
        help="仅执行公共产品导入（gitee），跳过其余步骤。假定容器已运行。",
    )
    args = parser.parse_args()
    # 如果未显式提供 db-host，则默认使用 --ip
    if not args.db_host:
        args.db_host = args.ip
    return args


def main() -> None:
    try:
        installer = IswInstaller(parse_args())
        installer.run()
    except InstallError as exc:
        print(f"\n安装失败：{exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n安装被中断。")
        sys.exit(1)


if __name__ == "__main__":
    main()


