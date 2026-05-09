# NetTraffic-AI

一个面向网络流量监测与可视化分析的项目，包含前端大屏、后端抓包入库与 API 服务，支持活跃主机/IP、协议占比、高流量 IP、告警信息等核心指标展示，并提供基于大模型的问答入口。

## 项目能做什么

- 实时抓取网络流量数据（Python 抓包）
- 将流量统计结果写入数据库（MySQL）
- 提供看板所需 API（FastAPI）
- 展示网络态势大屏（Vue2 + ECharts/DataV）
- 支持自然语言问答（ChatBot 接口）

## 主要功能模块

- 活跃主机统计
- 活跃 IP 统计
- 高流量 IP 排行
- L4/L7 协议占比分析
- 实时告警展示
- 流量趋势展示/预测视图

## 技术栈

- 前端：`Vue2`、`ECharts`、`@jiaminghi/data-view`、`Three.js`
- 后端：`Python`、`FastAPI`
- 数据库：`MySQL`
- 其他：`Axios`（前后端通信）

## 项目结构

```text
nettraffic-ai/
├─ src/                    # 前端源码（大屏组件、图表、页面）
├─ public/                 # 前端静态资源
├─ python-capture/         # 后端抓包与 API 服务
│  ├─ main.py              # 抓包主程序
│  ├─ api_main.py          # FastAPI 入口
│  ├─ schema_mysql.sql     # 数据库表结构
│  └─ requirements.txt     # Python 依赖
├─ package.json            # 前端依赖与脚本
└─ README.md
```

## 快速开始

### 1. 启动前端

```bash
npm install
npm run serve
```

默认开发地址：`http://localhost:8080`

### 2. 启动后端（抓包 + API）

```bash
cd python-capture
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

初始化数据库：

```sql
SOURCE schema_mysql.sql;
```

启动抓包：

```bash
python main.py --list-ifaces
python main.py --iface "YOUR_INTERFACE_NAME" --bpf "tcp or udp" --out-dir data --database-url "mysql+pymysql://root:root@127.0.0.1:3306/nettraffic_ai"
```

启动 API：

```bash
set DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/nettraffic_ai
python api_main.py
```

Swagger 文档：`http://127.0.0.1:8000/docs`

## 说明

- Windows 抓包建议以管理员权限运行，并安装 Npcap
- 仓库已配置忽略本地虚拟环境、缓存和日志文件

## 适用场景

- 校园网/实验室网络态势演示
- 网络安全课程与毕业设计
- 流量监控可视化原型开发
