# Python Capture Backend

该目录提供抓包后端能力，包含：

1. 抓包并写入 JSONL（原有）
2. 抓包分类入 MySQL（活跃主机、活跃 IP、高流量 IP、L4/L7 协议占比、实时告警）
3. FastAPI + Swagger 接口（给前端看板直接调用）

## 1) 安装

```bash
cd python-capture
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) 初始化数据库

```sql
-- 在 MySQL 执行
SOURCE schema_mysql.sql;
```

## 3) 启动抓包（写文件 + 入库）

```bash
python main.py --list-ifaces
python main.py --iface "YOUR_INTERFACE_NAME" --bpf "tcp or udp" --out-dir data --database-url "mysql+pymysql://root:root@127.0.0.1:3306/nettraffic_ai"
```

可选阈值参数：

```bash
--high-traffic-threshold-bytes 10485760
```

## 4) 启动 API（含 Swagger）

```bash
set DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/nettraffic_ai
python api_main.py
```

Swagger 页面：

- `http://127.0.0.1:8000/docs`

## 前端可用接口

- `GET /api/dashboard/overview`
- `GET /api/dashboard/active-hosts?limit=20`
- `GET /api/dashboard/active-ips?limit=20`
- `GET /api/dashboard/high-traffic-ips?limit=20`
- `GET /api/dashboard/protocols/transport`
- `GET /api/dashboard/protocols/application`
- `GET /api/dashboard/alerts/recent?limit=20`

## 数据分类说明（对应你图里的看板）

- 活跃主机：`active_hosts`（按 MAC）
- 活跃 IP：`active_ips`
- 高流量 IP：`active_ips` 按 `byte_count` 排序
- 应用层协议：`protocol_metrics` 中 `protocol_layer='L7'`
- 传输层协议：`protocol_metrics` 中 `protocol_layer='L4'`
- 实时警报数：`alert_records` 中 `status='ACTIVE'`

## 说明

- Windows 抓包请用管理员终端，并安装 Npcap。
- 当前 L7 是基于端口映射识别（HTTP/HTTPS/DNS/SSH/MySQL/Redis 等）。

## Chatbot (DeepSeek)

`/api/chat/ask` now uses DeepSeek directly and injects real-time dashboard context.

PowerShell startup example:

```powershell
$env:DATABASE_URL="mysql+pymysql://root:root@127.0.0.1:3306/nettraffic_ai"
$env:DEEPSEEK_API_KEY="your_deepseek_api_key"
$env:DEEPSEEK_MODEL="deepseek-chat"
python api_main.py
```

Optional env vars:

- `DEEPSEEK_API_URL` (default: `https://api.deepseek.com/chat/completions`)
- `DEEPSEEK_TIMEOUT_SEC` (default: `20`)
- `DEEPSEEK_MAX_HISTORY` (default: `8`)
