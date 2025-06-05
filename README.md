# 网站监控程序

这是一个用于监控指定网站更新并发送通知的Python程序。

## 功能特点

- 定期检查目标网站的内容更新
- 发现更新时自动发送通知
- 支持启动时发送通知
- 支持每日定时推送最新消息
- 完整的日志记录
- 可配置的扫描间隔和通知选项

## 环境要求

- Python 3.8+
- 虚拟环境（推荐）

## 安装步骤

1. 克隆仓库：
```bash
git clone [仓库地址]
cd [项目目录]
```

2. 创建并激活虚拟环境：
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置说明

在项目根目录创建 `.env` 文件，配置以下参数：

```ini
# 网站监控配置
TARGET_URL=http://www.lixia.gov.cn/col/col37116/index.html
SCAN_INTERVAL=300  # 扫描间隔（秒）
SEND_STARTUP_NOTIFY=true  # 是否在启动时发送通知

# 定时推送配置
DAILY_PUSH_ENABLED=true  # 是否启用每日推送
DAILY_PUSH_TIMES=09:00,21:00  # 每日推送时间，多个时间用逗号分隔

# 日志配置
LOG_LEVEL=INFO  # 日志级别
LOG_RETENTION=30  # 日志保留天数
```

## 运行程序

```bash
python main.py
```

## 功能说明

### 1. 网站监控
- 程序会按照设定的时间间隔（默认5分钟）检查目标网站
- 发现新内容时自动发送通知

### 2. 启动通知
- 程序启动时会发送一条通知消息
- 可通过 `SEND_STARTUP_NOTIFY` 配置是否启用

### 3. 每日定时推送
- 支持在指定时间（默认早9点和晚9点）推送当日最新消息
- 可通过 `DAILY_PUSH_ENABLED` 开启/关闭此功能
- 可通过 `DAILY_PUSH_TIMES` 配置推送时间

### 4. 日志记录
- 所有操作都会记录到日志文件
- 日志文件保存在 `logs` 目录
- 可通过 `LOG_LEVEL` 配置日志级别
- 可通过 `LOG_RETENTION` 配置日志保留天数

## 目录结构

```
.
├── config/             # 配置文件目录
│   └── settings.py    # 配置管理
├── utils/             # 工具函数目录
│   ├── logger.py     # 日志工具
│   ├── monitor.py    # 网站监控
│   └── notifier.py   # 通知工具
├── logs/              # 日志文件目录
├── .env              # 环境变量配置
├── .env.example      # 环境变量示例
├── requirements.txt  # 项目依赖
└── main.py          # 主程序
```

## 注意事项

1. 确保 `.env` 文件中的配置正确
2. 确保网络连接正常
3. 建议使用虚拟环境运行程序
4. 定期检查日志文件大小

## 错误处理

- 程序会自动记录所有错误到日志文件
- 网络错误会自动重试
- 配置错误会在启动时提示

## 开发计划

- [ ] 添加更多通知方式
- [ ] 支持多个目标网站
- [ ] 添加Web管理界面
- [ ] 支持自定义消息模板

## 扩展功能

项目预留了以下扩展接口：
- OpenAI 集成
- Kafka 消息队列
- Elasticsearch 存储

## 注意事项

- 请确保正确配置通知相关的环境变量
- 建议定期检查日志文件
- 如遇到问题，请查看日志文件获取详细信息

## 许可证

MIT License 