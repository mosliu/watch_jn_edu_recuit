import sys
import signal
from utils.logger import logger
from utils.monitor import WebMonitor
from utils.notify import send

def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("接收到退出信号，正在关闭程序...")
    send("监控程序退出", "程序正常退出")
    sys.exit(0)

def main():
    """主程序入口"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 创建并运行监控器
        monitor = WebMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main() 