import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

def setup_logger():
    """配置日志系统"""
    # 确保日志目录存在
    settings.LOG_DIR.mkdir(exist_ok=True)
    
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        settings.LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天零点创建新文件
        retention=f"{settings.LOG_RETENTION} days",  # 保留指定天数
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        encoding="utf-8"
    )
    
    return logger

# 创建全局logger实例
logger = setup_logger() 