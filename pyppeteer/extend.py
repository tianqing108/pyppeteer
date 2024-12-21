import logging
import re
import socket
from urllib.parse import urlparse

import requests

from pyppeteer.browser import Browser
from pyppeteer.page import Page

logger = logging.getLogger(__name__)



async def active_page(browser: Browser) -> Page | None:
    pages = await browser.pages()
    match = re.search(r":(\d+)/", browser._connection._url)
    port = None
    if match:
        port = match.group(1)
    else:
        return None
    browserUrl = f"http://127.0.0.1:{port}/json"
    res = requests.get(browserUrl)
    data = res.json()
    if len(data) == 0:
        return None
    filtered_data = [item for item in data if item.get('type') == "page"]
    if len(filtered_data) == 0:
        return None
    target_id = filtered_data[0]['id']
    page = next((p for p in pages if p.target._targetId == target_id), None)
    return page


def is_browser_alive(wsurl):
    # 使用正则表达式提取端口号
    match = re.search(r":(\d+)/", wsurl)
    if match:
        port = match.group(1)
        logger.info("提取到的端口号:%s", port)
        return is_port_in_use(int(port))
    else:
        logger.info("未找到端口号")
        return False


# 比较host是否一致
def compare_host(url1, url2):
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)

    # 获取主机部分
    host1 = parsed_url1.hostname
    host2 = parsed_url2.hostname

    # 比较主机部分是否相同
    if host1 == host2:
        return True
    else:
        return False


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)  # 设置连接超时时间为1秒
            s.connect(("127.0.0.1", port))
            return True  # 端口已被占用
        except (socket.timeout, ConnectionRefusedError):
            return False  # 端口未被占用


async def open(exec_path: str, remote_port: int, proxy_port: int, user_data_dir: str) -> str:
    if is_port_in_use(remote_port):
        logger.info("chrome已启动，跳过")
        return True
    args = [
        f"--remote-debugging-port={remote_port}",
        f"--proxy-server=127.0.0.1:{proxy_port}",
        f"--user-data-dir={user_data_dir}",
        '--disable-background-networking', '--disable-background-timer-throttling', '--disable-breakpad',
        '--disable-browser-side-navigation', '--disable-client-side-phishing-detection', '--disable-default-apps',
        '--disable-dev-shm-usage', '--disable-extensions', '--disable-features=site-per-process',
        '--disable-hang-monitor',
        '--disable-popup-blocking', '--disable-prompt-on-repost', '--disable-sync', '--disable-translate',
        '--metrics-recording-only', '--no-first-run', '--safebrowsing-disable-auto-update', '--password-store=basic','--use-mock-keychain'
    ]
    process = await asyncio.to_thread(subprocess.Popen, [exec_path] + args, creationflags=subprocess.DETACHED_PROCESS)
    if process:
        logger.info("chrome已启动，pid：%s", process.pid)
        return True
    return False

if __name__ == '__main__':
    asyncio.run(open(r"C:\Program Files\Google\Chrome\Application\chrome.exe", 9090, 9091, "./user"))
    time.sleep(5)
