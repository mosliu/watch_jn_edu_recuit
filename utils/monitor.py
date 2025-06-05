import time
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

    def fetch_content(self) -> Optional[str]:
        """获取网页内容"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"获取网页内容失败: {str(e)}")
            return None

    def parse_content(self, html: str) -> List[Dict[str, str]]:
        """解析网页内容，提取新闻列表"""
        try:
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
                except Exception as e:
                    logger.error(f"解析单条新闻失败: {str(e)}")
                    continue
            
            logger.info(f"当前页面共有 {len(news_list)} 条信息")
            return news_list
        except Exception as e:
            logger.error(f"解析网页内容失败: {str(e)}")
            return []

    def check_updates(self) -> bool:
        """检查是否有更新"""
        current_content = self.fetch_content()
        if not current_content:
            return False

        if self.last_content is None:
            self.last_content = current_content
            return False

        if current_content != self.last_content:
            self.last_content = current_content
            return True

        return False

    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """获取最新的一条新闻"""
        content = self.fetch_content()
        if not content:
            return None
        
        news_list = self.parse_content(content)
        return news_list[0] if news_list else None

    def run(self):
        """运行监控"""
        logger.info("开始监控网页更新...")
        
        # 启动时发送最新消息
        if settings.SEND_STARTUP_NOTIFY:
            latest_news = self.get_latest_news()
            if latest_news:
                message = "监控程序启动，当前最新信息：\n\n"
                message += f"标题：{latest_news['title']}\n"
                message += f"日期：{latest_news['date']}\n"
                message += f"链接：{latest_news['url']}\n"
                send("监控程序启动通知", message)
        
        while True:
            try:
                if self.check_updates():
                    logger.info("检测到网页更新")
                    current_news = self.parse_content(self.last_content)
                    if current_news:
                        message = "检测到新的教育信息：\n\n"
                        for news in current_news[:5]:  # 只显示最新的5条
                            message += f"标题：{news['title']}\n"
                            message += f"日期：{news['date']}\n"
                            message += f"链接：{news['url']}\n\n"
                        
                        send("历下区教育信息更新提醒", message)
                
                time.sleep(settings.SCAN_INTERVAL)
                
            except Exception as e:
                error_msg = f"监控过程发生错误: {str(e)}"
                logger.error(error_msg)
                send("监控程序异常", error_msg)
                time.sleep(60)  # 发生错误时等待1分钟后继续 