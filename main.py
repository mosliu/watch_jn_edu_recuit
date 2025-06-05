import sys
import signal
import time
import schedule
from datetime import datetime
from utils.logger import logger
from utils.monitor import WebsiteMonitor
from utils.notifier import Notifier
from config.settings import settings

def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("接收到退出信号，正在关闭程序...")
    send("监控程序退出", "程序正常退出")
    sys.exit(0)

def send_daily_summary():
    """发送每日汇总消息"""
    try:
        monitor = WebsiteMonitor()
        latest_message = monitor.get_latest_message()
        if latest_message:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"每日汇总 ({current_time}):\n最新消息：\n{latest_message}"
            notifier = Notifier()
            notifier.send_notification(message)
            logger.info("每日汇总消息发送成功")
        else:
            logger.warning("没有找到最新消息，跳过每日汇总")
    except Exception as e:
        logger.error(f"发送每日汇总消息失败: {str(e)}")

def main():
    """主程序入口"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 初始化监控器和通知器
        monitor = WebsiteMonitor()
        notifier = Notifier()

        # 如果配置了启动通知，发送启动消息
        if settings.SEND_STARTUP_NOTIFY:
            notifier.send_notification("网站监控服务已启动")

        # 设置定时推送任务
        if settings.DAILY_PUSH_ENABLED:
            for push_time in settings.DAILY_PUSH_TIMES:
                schedule.every().day.at(push_time).do(send_daily_summary)
                logger.info(f"已设置每日推送时间: {push_time}")

        # 主循环
        while True:
            try:
                # 运行定时任务
                schedule.run_pending()
                
                # 检查网站更新
                if monitor.check_updates():
                    latest_message = monitor.get_latest_message()
                    if latest_message:
                        notifier.send_notification(latest_message)
                
                # 等待下一次检查
                time.sleep(settings.SCAN_INTERVAL)
            except Exception as e:
                logger.error(f"监控过程中发生错误: {str(e)}")
                time.sleep(settings.SCAN_INTERVAL)  # 发生错误时也等待一段时间再重试

    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main() 