import base64
import http.client
import json
import os
import secrets
import string
from pathlib import Path
from sys import argv


BASE_URL = "/api/v5"

# 统一凭证文件（与 install_emqx.py / install_influxdb.py 一致）
CREDENTIAL_FILE = Path("/workspace/isw-helper/output/deploy_credentials.json")

# 内置 MQTT 用户模板（用户名固定，密码运行时随机生成）
INTERNAL_USER_TEMPLATES = [
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


def create_connector(emqx_server_ip, emqx_server_port, api_key, api_secret):
    # 创建connector的数据
    connector_data = {
        "type": "http",
        "name": "connection_event_WH_D",
        "enable": True,
        "tags": [],
        # todo: "http://127.0.0.1" 应取自变量 SITE_BASE_URL
        "url": "http://127.0.0.1/api/emqx_webhook/connection_event/",
        "headers": {},
        "connect_timeout": "15s",
        "pool_type": "random",
        "pool_size": 8,
        "enable_pipelining": 100,
        "ssl": {
            "verify": "verify_none",
            "reuse_sessions": True,
            "depth": 10,
            "versions": ["tlsv1.3", "tlsv1.2"],
            "ciphers": [],
            "secure_renegotiate": True,
            "log_level": "notice",
            "hibernate_after": "5s",
            "enable": False
        },
        "resource_opts": {
            "health_check_interval": "15s",
            "start_after_created": True,
            "start_timeout": "5s"
        }
    }
    connector_url = f"{BASE_URL}/connectors"

    # 创建HTTP连接
    conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()}'
    }

    # 发送POST请求
    conn.request("POST", connector_url, body=json.dumps(connector_data), headers=headers)
    response = conn.getresponse()
    print(f"Create connector response: {response.status} {response.reason}")
    print(response.read().decode())

    # 关闭连接
    conn.close()


def create_action(emqx_server_ip, emqx_server_port, api_key, api_secret):
    # 创建action的数据
    action_data = {
        "type": "http",
        "name": "connection_event_WH_D",
        "enable": True,
        "connector": "connection_event_WH_D",
        "tags": [],
        "parameters": {
            "method": "post",
            "headers": {
                "keep-alive": "timeout=5",
                "content-type": "application/json",
                "connection": "keep-alive",
                "cache-control": "no-cache",
                "accept": "application/json"
            },
            "max_retries": 2
        },
        "resource_opts": {
            "worker_pool_size": 16,
            "health_check_interval": "15s",
            "query_mode": "async",
            "request_ttl": "45s",
            "inflight_window": 100,
            "max_buffer_bytes": "256MB"
        }
    }
    action_url = f"{BASE_URL}/actions"

    # 创建HTTP连接
    conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()}'
    }

    # 发送POST请求
    conn.request("POST", action_url, body=json.dumps(action_data), headers=headers)
    response = conn.getresponse()
    print(f"Create action response: {response.status} {response.reason}")
    print(response.read().decode())

    # 关闭连接
    conn.close()


def create_rule(emqx_server_ip, emqx_server_port, api_key, api_secret):
    # 创建rule的数据
    rule_data = {
        "id": "connection_event_WH_D",
        "sql": "SELECT\n  *\nFROM\n  \"$events/client_connected\",\n  \"$events/client_disconnected\"",
        "actions": [
            "http:connection_event_WH_D"
        ]
    }
    rule_url = f"{BASE_URL}/rules"

    # 创建HTTP连接
    conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()}'
    }

    # 发送POST请求
    conn.request("POST", rule_url, body=json.dumps(rule_data), headers=headers)
    response = conn.getresponse()
    print(f"Create rule response: {response.status} {response.reason}")
    print(response.read().decode())

    # 关闭连接
    conn.close()


def load_env(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            # 去除行首尾的空白字符
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            # 分割键值对
            key, value = line.split('=', 1)
            os.environ[key] = value


# 第一步：获取 token
def get_token(password, emqx_server_ip, emqx_server_port):
    conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)
    headers = {'Content-Type': 'application/json'}
    payload = {
        "username": "admin",
        "password": password
    }
    conn.request("POST", f"{BASE_URL}/login", body=json.dumps(payload), headers=headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    conn.close()
    if response.status == 200:
        return data['token']
    else:
        raise Exception(f"Failed to get token: {response.status} {data}")


# 第二步：创建 API 密钥
def create_api_key(emqx_server_ip, emqx_server_port, token):
    conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        "name": "for_webserver",
        "desc": "",
        "enable": True
    }
    conn.request("POST", f"{BASE_URL}/api_key", body=json.dumps(payload), headers=headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    conn.close()
    if response.status == 200:
        print(f"API Key: {data['api_key']}")
        print(f"API Secret: {data['api_secret']}")
    else:
        raise Exception(f"Failed to create API key: {response.status} {data}")
    return data


def rewrite_env_value(file_path, key, value):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f"{key}={value}\n"
                key_found = True
                break
        
        if not key_found:
            print(f"{key} not found in .env file")
            return
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
    
    except Exception as e:
        print(f"写入文件时发生错误: {e}")
        exit()


# 初始化 API 秘钥（通过 admin 密码登录获取 token，再创建 API key）
def init_api_key(password, emqx_server_ip, emqx_server_port):
    try:
        # 获取 token
        token = get_token(password, emqx_server_ip, emqx_server_port)
        print(f"Token: {token}")

        # 创建 API 密钥
        data = create_api_key(emqx_server_ip, emqx_server_port, token)
        return data
    except Exception as e:
        print(f"Error: {e}")
        exit()


# 从 deploy_credentials.json 中读取/写入 EMQX 相关凭证
def load_deploy_credentials():
    if CREDENTIAL_FILE.exists():
        try:
            return json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("Warning: deploy_credentials.json 解析失败，将覆盖重写。")
            return {}
    return {}


def save_deploy_credentials(data):
    CREDENTIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_or_create_api_credentials(password, emqx_server_ip, emqx_server_port):
    """
    获取或创建 EMQX 的 API key/secret。
    - 优先从 deploy_credentials.json 的 emqx 节点读取
    - 若不存在，则调用 EMQX 接口创建，并写回 deploy_credentials.json
    """
    payload = load_deploy_credentials()
    emqx_section = payload.get("emqx", {})

    api_key = emqx_section.get("api_key") or ""
    api_secret = emqx_section.get("api_secret") or ""

    if api_key and api_secret:
        print("在 deploy_credentials.json 中找到已有 EMQX API key/secret。")
        return api_key, api_secret

    print("deploy_credentials.json 中未找到 EMQX API key/secret，将调用 EMQX 创建。")
    data = init_api_key(password, emqx_server_ip, emqx_server_port)

    emqx_section["api_key"] = data["api_key"]
    emqx_section["api_secret"] = data["api_secret"]
    payload["emqx"] = emqx_section
    save_deploy_credentials(payload)

    print(f"API key/secret 已写入 {CREDENTIAL_FILE}（emqx.api_key / emqx.api_secret）。")
    print("后续可由其他脚本统一写入 .env。")
    return data["api_key"], data["api_secret"]


def generate_password(length: int = 24) -> str:
    """生成适合作为 MQTT 用户密码的随机字符串。"""
    alphabet = string.ascii_letters + string.digits + "_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def get_or_create_internal_users():
    """
    获取或创建 EMQX 内置 MQTT 用户列表。
    - 优先从 deploy_credentials.json 的 emqx.internal_users 读取
    - 如不存在，则根据 INTERNAL_USER_TEMPLATES 生成随机密码并写回
    """
    payload = load_deploy_credentials()
    emqx_section = payload.get("emqx", {})

    internal_users = emqx_section.get("internal_users")
    if internal_users:
        print(f"在 {CREDENTIAL_FILE} 中找到 {len(internal_users)} 个 internal_users。")
        return internal_users

    users = []
    for tmpl in INTERNAL_USER_TEMPLATES:
        username = tmpl["username"]
        pwd = generate_password()
        users.append(
            {
                "username": username,
                "password": pwd,
                "is_superuser": tmpl.get("is_superuser", False),
            }
        )

    emqx_section["internal_users"] = users
    payload["emqx"] = emqx_section
    save_deploy_credentials(payload)

    print(f"已根据模板初始化 {len(users)} 个 internal_users，密码已随机生成并写入 {CREDENTIAL_FILE}。")
    return users


def get_or_create_password_auth(emqx_server_ip, emqx_server_port, api_key, api_secret):
    """
    自动化创建 Password-Based + 内置数据库 的认证配置。
    - 若已存在相同机制/后端的认证，则复用其 id
    - 否则创建一个新的
    """
    conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {base64.b64encode(f'{api_key}:{api_secret}'.encode()).decode()}",
    }

    # 先查询已有认证配置
    conn.request("GET", f"{BASE_URL}/authentication", headers=headers)
    response = conn.getresponse()
    body = response.read().decode() or "[]"
    try:
        configs = json.loads(body)
    except json.JSONDecodeError:
        configs = []

    if response.status == 200:
        for item in configs:
            if (
                item.get("mechanism") == "password_based"
                and item.get("backend") == "built_in_database"
            ):
                auth_id = item.get("id")
                print(f"找到已有 Password-Based 内置数据库认证配置，id={auth_id}")
                conn.close()
                return auth_id
    else:
        print(f"查询认证配置失败: {response.status} {body}")

    # 未找到则创建新的
    payload = {
        "mechanism": "password_based",
        "backend": "built_in_database",
        # EMQX v5 需要指定哈希算法对象，使用明文以便与脚本生成的密码一致
        "password_hash_algorithm": {"name": "plain"},
        "user_id_type": "username",
    }

    conn.request(
        "POST",
        f"{BASE_URL}/authentication",
        body=json.dumps(payload),
        headers=headers,
    )
    response = conn.getresponse()
    body = response.read().decode() or "{}"
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = {}

    if response.status in (200, 201):
        auth_id = data.get("id")
        print(f"已创建 Password-Based 内置数据库认证配置，id={auth_id}")
        conn.close()
        return auth_id

    print(f"创建认证配置失败: {response.status} {body}")
    conn.close()
    return None


def import_users_from_internal_users(
    emqx_server_ip: str,
    emqx_server_port: str,
    api_key: str,
    api_secret: str,
    auth_id: str,
    internal_users,
):
    """
    从 CSV 导入用户到指定的认证配置中。
    约定：CSV 的前两列为 username,password（可带表头，表头行会自动跳过）。
    """
    if not auth_id:
        print("未获取到认证配置 id，跳过导入用户。")
        return

    if not internal_users:
        print("未提供 internal_users 列表，跳过导入用户。")
        return

    print(f"开始根据 internal_users 导入 EMQX 用户，共 {len(internal_users)} 个。")

    for item in internal_users:
        username = (item.get("username") or "").strip()
        password = item.get("password") or ""
        if not username or not password:
            continue

        conn = http.client.HTTPConnection(emqx_server_ip, emqx_server_port)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{api_key}:{api_secret}'.encode()).decode()}",
        }
        payload = {
            "user_id": username,
            "password": password,
        }
        url = f"{BASE_URL}/authentication/{auth_id}/users"
        conn.request("POST", url, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        body = response.read().decode()
        if response.status not in (200, 201):
            print(f"导入用户 {username} 失败: {response.status} {body}")
        else:
            print(f"已导入用户 {username}")
        conn.close()


def main(password):
    env = ".env"

    # 从 .env 中仅读取 EMQX_API_HOST / EMQX_API_PORT 等配置
    load_env(env)

    # 设置 EMQX 服务器的 IP 和端口
    emqx_server_ip = os.getenv('EMQX_API_HOST', '127.0.0.1')
    print(f"EMQX Server IP: {emqx_server_ip}")
    emqx_server_port = os.getenv('EMQX_API_PORT', '58084')
    print(f"EMQX Server Port: {emqx_server_port}")

    # 从 deploy_credentials.json 获取或创建 API key/secret
    api_key, api_secret = get_or_create_api_credentials(password, emqx_server_ip, emqx_server_port)

    # 设置Basic Auth认证信息
    print(f"EMQX api_key: {api_key}")
    print(f"EMQX api_secret: {api_secret[0]}*{api_secret[-1]}")

    # 调用函数创建 connector / action / rule
    create_connector(emqx_server_ip, emqx_server_port, api_key, api_secret)
    create_action(emqx_server_ip, emqx_server_port, api_key, api_secret)
    create_rule(emqx_server_ip, emqx_server_port, api_key, api_secret)

    # 自动化创建 Password-Based + 内置数据库 认证，并从 CSV 导入用户
    auth_id = get_or_create_password_auth(emqx_server_ip, emqx_server_port, api_key, api_secret)
    # internal_users 直接来源于脚本内置模板（首次运行会随机生成密码并写入 deploy_credentials.json）
    internal_users = get_or_create_internal_users()
    import_users_from_internal_users(emqx_server_ip, emqx_server_port, api_key, api_secret, auth_id, internal_users)


if __name__ == "__main__":
    # 接收一个参数，该参数为EMQX管理页面的admin密码
    if len(argv) != 2:
        print("Usage: python init_emqx.py <password>")
        exit()

    password = argv[1]
    main(password)
