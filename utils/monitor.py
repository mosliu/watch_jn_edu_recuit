import time
import schedule
from datetime import datetime
from typing import Optional, List, Dict
import requests
from bs4 import BeautifulSoup
from utils.logger import logger
from utils.notify import send
from config.settings import settings

class WebMonitor:
    def __init__(self):
        self.url = settings.TARGET_URL
        self.last_content: Optional[str] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.start_time = datetime.now()
        logger.info(f"监控器初始化完成，目标URL: {self.url}")
        logger.info(f"扫描间隔: {settings.SCAN_INTERVAL}秒")
        logger.info(f"每日推送: {'启用' if settings.DAILY_PUSH_ENABLED else '禁用'}")
        if settings.DAILY_PUSH_ENABLED:
            logger.info(f"推送时间: {', '.join(settings.push_times)}")

    def fetch_content(self) -> Optional[str]:
        """获取网页内容"""
        start_time = time.time()
        try:
            logger.info(f"开始获取网页内容: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            elapsed = time.time() - start_time
            logger.info(f"网页获取成功，耗时: {elapsed:.2f}秒，状态码: {response.status_code}")
            return response.text
        except requests.RequestException as e:
            elapsed = time.time() - start_time
            logger.error(f"获取网页内容失败，耗时: {elapsed:.2f}秒，错误: {str(e)}")
            return None

    def parse_content(self, html: str) -> List[Dict[str, str]]:
        """解析网页内容，提取新闻列表"""
        start_time = time.time()
        try:
            logger.info("开始解析网页内容")
            soup = BeautifulSoup(html, 'html.parser')
            news_list = []
            
            # 查找包含新闻列表的script标签
            script_tag = soup.find('script', {'type': 'text/xml'})
            if not script_tag:
                logger.warning("未找到新闻列表数据")
                return []

            # 解析CDATA中的内容
            cdata_content = script_tag.string
            if not cdata_content:
                logger.warning("未找到新闻列表内容")
                return []

            # 创建新的BeautifulSoup对象来解析CDATA内容
            cdata_soup = BeautifulSoup(cdata_content, 'html.parser')
            
            # 查找所有record标签
            records = cdata_soup.find_all('record')
            logger.info(f"找到 {len(records)} 条记录")
            
            for record in records:
                try:
                    # 解析每个record中的内容
                    record_soup = BeautifulSoup(record.string, 'html.parser')
                    link = record_soup.find('a')
                    date_span = record_soup.find('span', class_='font14')
                    
                    if link and date_span:
                        title = link.get('title', '').strip()
                        url = link.get('href', '')
                        if url and not url.startswith('http'):
                            url = f"http://www.lixia.gov.cn{url}"
                        
                        date = date_span.text.strip('[]')
                        
                        news_list.append({
                            'title': title,
                            'url': url,
                            'date': date
                        })
                        logger.debug(f"解析成功: {title} ({date})")
                except Exception as e:
                    logger.error(f"解析单条新闻失败: {str(e)}")
                    continue
            
            elapsed = time.time() - start_time
            logger.info(f"网页解析完成，耗时: {elapsed:.2f}秒，成功解析 {len(news_list)} 条信息")
            return news_list
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"解析网页内容失败，耗时: {elapsed:.2f}秒，错误: {str(e)}")
            return []

    def check_updates(self) -> bool:
        """检查是否有更新"""
        start_time = time.time()
        logger.info("开始检查更新")
        
        current_content = self.fetch_content()
        if not current_content:
            logger.warning("获取当前内容失败，跳过更新检查")
            return False

        if self.last_content is None:
            logger.info("首次运行，记录当前内容")
            self.last_content = current_content
            # 打印最新一条消息
            news_list = self.parse_content(current_content)
            if news_list:
                latest = news_list[0]
                logger.info("当前最新消息:")
                logger.info(f"标题: {latest['title']}")
                logger.info(f"日期: {latest['date']}")
                logger.info(f"链接: {latest['url']}")
            return False

        has_update = current_content != self.last_content
        elapsed = time.time() - start_time
        
        if has_update:
            logger.info(f"检测到更新，耗时: {elapsed:.2f}秒")
            self.last_content = current_content
            # 打印更新后的最新消息
            news_list = self.parse_content(current_content)
            if news_list:
                latest = news_list[0]
                logger.info("更新后的最新消息:")
                logger.info(f"标题: {latest['title']}")
                logger.info(f"日期: {latest['date']}")
                logger.info(f"链接: {latest['url']}")
        else:
            logger.info(f"未检测到更新，耗时: {elapsed:.2f}秒")

        return has_update

    def get_latest_message(self) -> Optional[str]:
        """获取最新的一条消息"""
        start_time = time.time()
        logger.info("开始获取最新消息")
        
        news = self.get_latest_news()
        if news:
            message = f"标题：{news['title']}\n日期：{news['date']}\n链接：{news['url']}"
            elapsed = time.time() - start_time
            logger.info(f"获取最新消息成功，耗时: {elapsed:.2f}秒")
            logger.info(f"最新消息: {news['title']} ({news['date']})")
            return message
        
        elapsed = time.time() - start_time
        logger.warning(f"获取最新消息失败，耗时: {elapsed:.2f}秒")
        return None

    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """获取最新的一条新闻"""
        start_time = time.time()
        logger.info("开始获取最新新闻")
        
        content = self.fetch_content()
        if not content:
            logger.error("获取网页内容失败")
            return None
        
        news_list = self.parse_content(content)
        elapsed = time.time() - start_time
        
        if news_list:
            logger.info(f"获取最新新闻成功，耗时: {elapsed:.2f}秒")
            return news_list[0]
        
        logger.warning(f"未找到任何新闻，耗时: {elapsed:.2f}秒")
        return None

    def send_daily_summary(self):
        """发送每日汇总消息"""
        start_time = time.time()
        logger.info("开始发送每日汇总")
        
        try:
            latest_message = self.get_latest_message()
            if latest_message:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"每日汇总 ({current_time}):\n最新消息：\n{latest_message}"
                send(message)
                elapsed = time.time() - start_time
                logger.info(f"每日汇总消息发送成功，耗时: {elapsed:.2f}秒")
            else:
                elapsed = time.time() - start_time
                logger.warning(f"没有找到最新消息，跳过每日汇总，耗时: {elapsed:.2f}秒")
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"发送每日汇总消息失败，耗时: {elapsed:.2f}秒，错误: {str(e)}")

    def run(self):
        """运行监控"""
        logger.info(f"开始监控网页更新... 启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 启动时发送最新消息
        if settings.SEND_STARTUP_NOTIFY:
            logger.info("发送启动通知")
            latest_news = self.get_latest_news()
            if latest_news:
                message = "监控程序启动，当前最新信息：\n\n"
                message += f"标题：{latest_news['title']}\n"
                message += f"日期：{latest_news['date']}\n"
                message += f"链接：{latest_news['url']}\n"
                send("监控程序启动通知", message)
                logger.info("启动通知发送成功")
            else:
                logger.warning("未找到最新消息，跳过启动通知")

        # 设置定时推送任务
        if settings.DAILY_PUSH_ENABLED:
            logger.info("设置定时推送任务")
            for push_time in settings.push_times:
                schedule.every().day.at(push_time).do(self.send_daily_summary)
                logger.info(f"已设置每日推送时间: {push_time}")
        
        check_count = 0
        while True:
            try:
                check_count += 1
                current_time = datetime.now()
                logger.info(f"第 {check_count} 次检查 - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 运行定时任务
                schedule.run_pending()
                
                # 检查网站更新
                if self.check_updates():
                    latest_message = self.get_latest_message()
                    if latest_message:
                        send(latest_message)
                        logger.info("更新通知发送成功")
                
                # 等待下一次检查
                logger.info(f"等待 {settings.SCAN_INTERVAL} 秒后进行下一次检查")
                time.sleep(settings.SCAN_INTERVAL)
                
            except Exception as e:
                error_msg = f"监控过程发生错误: {str(e)}"
                logger.error(error_msg)
                send("监控程序异常", error_msg)
                logger.info("等待60秒后重试")
                time.sleep(60)  # 发生错误时等待1分钟后继续 