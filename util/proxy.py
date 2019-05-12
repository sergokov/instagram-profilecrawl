import sys
from collections import deque

from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from util.chromedriver import init_chromedriver
from util.settings import Settings
from util.time_util import sleep_actual, current_time_mills

#36.66.211.81:39775,138.204.95.189:8080,41.193.238.249:8080,203.99.116.210:8080

class Proxy:
    proxy_ip = None
    invoke_time = current_time_mills()
    browser = None

    def __init__(self, proxy_ip, invoke_time, browser):
        self.proxy_ip = proxy_ip
        self.invoke_time = invoke_time
        self.browser = browser


class ProxyRotator:
    queue = deque()

    def __init__(self, proxy_ips):
        if len(proxy_ips) == 0:
            self.queue.appendleft(Proxy("local_ip", current_time_mills(), ProxyRotator._create_proxy_browser()))
        else:
            for proxy_ip in proxy_ips:
                browser = ProxyRotator._create_proxy_browser(proxy_ip)
                if browser is not None:
                    self.queue.appendleft(Proxy(proxy_ip, current_time_mills(), browser))

    @staticmethod
    def _create_proxy_browser(proxy_ip=None):
        chrome_options = Options()
        chromeOptions = webdriver.ChromeOptions()
        prefs = {'profile.managed_default_content_settings.images': 2, 'disk-cache-size': 4096}
        chromeOptions.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})

        capabilities = DesiredCapabilities.CHROME

        try:
            return init_chromedriver(chrome_options, capabilities)
        except Exception as exc:
            print(exc)
            sys.exit()

    def next_proxy(self):
        start = current_time_mills()
        proxy = self.queue.pop()
        while proxy.invoke_time > current_time_mills():
            sleep_actual(0.5)
        usage_delay = current_time_mills() - start
        print("Proxy {} will used with delay in {} mls.".format(proxy.proxy_ip, usage_delay))
        return proxy

    def return_proxy(self, proxy):
        proxy.invoke_time = current_time_mills() + Settings.sleep_time_between_post_crawl * 1000
        self.queue.appendleft(proxy)

