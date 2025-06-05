from pathlib import Path
from typing import Optional, List
import os
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv
import time

# 加载.env文件
env_path = Path('.') / '.env'
print(f"Looking for .env file at: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)
# load_dotenv()

class Settings(BaseSettings):
    # 网站监控配置
    TARGET_URL: str = Field(default="http://www.lixia.gov.cn/col/col37116/index.html")
    SCAN_INTERVAL: int = Field(default=300)  # 默认5分钟
    SEND_STARTUP_NOTIFY: bool = Field(default=True)  # 是否在启动时发送通知

    # 定时推送配置
    DAILY_PUSH_ENABLED: bool = Field(default=True)  # 是否启用每日推送
    DAILY_PUSH_TIMES: str = Field(default="09:00,21:00")  # 每日推送时间

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO")
    LOG_RETENTION: int = Field(default=30)  # 日志保留天数
    LOG_DIR: Path = Field(default=Path("logs"))

    @validator('SCAN_INTERVAL', 'LOG_RETENTION', pre=True)
    def parse_int(cls, v):
        print(f"Parsing int value: {v}, type: {type(v)}")  # 调试信息
        if isinstance(v, str):
            v = v.split('#')[0].strip()
            try:
                return int(v)
            except ValueError:
                return None
        return v

    @validator('SEND_STARTUP_NOTIFY', 'DAILY_PUSH_ENABLED', pre=True)
    def parse_bool(cls, v):
        print(f"Parsing bool value: {v}, type: {type(v)}")  # 调试信息
        if isinstance(v, str):
            v = v.split('#')[0].strip()
            return v.lower() in ('true', '1', 'yes', 'y')
        return v

    @property
    def push_times(self) -> List[str]:
        """获取推送时间列表"""
        if not self.DAILY_PUSH_TIMES:
            return ["09:00", "21:00"]
        return [time.strip() for time in self.DAILY_PUSH_TIMES.split(',') if time.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 打印当前工作目录和环境变量
print("\n=== Environment Information ===")
print(f"Current working directory: {os.getcwd()}")
print("\n=== Environment Variables ===")
all_vars = {
    'TARGET_URL': os.getenv('TARGET_URL'),
    'SCAN_INTERVAL': os.getenv('SCAN_INTERVAL'),
    'SEND_STARTUP_NOTIFY': os.getenv('SEND_STARTUP_NOTIFY'),
    'DAILY_PUSH_ENABLED': os.getenv('DAILY_PUSH_ENABLED'),
    'DAILY_PUSH_TIMES': os.getenv('DAILY_PUSH_TIMES'),
    'LOG_LEVEL': os.getenv('LOG_LEVEL'),
    'LOG_RETENTION': os.getenv('LOG_RETENTION')
}
for key, value in all_vars.items():
    print(f"{key}: {value} (type: {type(value)})")

print("\n=== Creating Settings Instance ===")
settings = Settings()
print("\n=== Final Settings Values ===")
print(f"TARGET_URL: {settings.TARGET_URL}")
print(f"SCAN_INTERVAL: {settings.SCAN_INTERVAL}")
print(f"SEND_STARTUP_NOTIFY: {settings.SEND_STARTUP_NOTIFY}")
print(f"DAILY_PUSH_ENABLED: {settings.DAILY_PUSH_ENABLED}")
print(f"DAILY_PUSH_TIMES: {settings.DAILY_PUSH_TIMES}")
print(f"Push times list: {settings.push_times}")
print(f"LOG_LEVEL: {settings.LOG_LEVEL}")
print(f"LOG_RETENTION: {settings.LOG_RETENTION}")
print(f"LOG_DIR: {settings.LOG_DIR}") 