import os
import random
import time
import threading

from queue import Queue

from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from autoCommet.cook import cookies, comments
from autoCommet.logger import Logger

BaseDir = os.path.abspath(os.path.dirname(__file__))
print(BaseDir)
log = Logger("scrawl", "log.txt")

q = Queue()


def get_bosh():
    try:
        with open(BaseDir + "/config/bosh.txt", 'r', encoding='utf-8') as fp:
            content = fp.read().split(',')
        return content
    except:
        print("未找到评论语句文件")
        exit(0)


def init_driver():
    chrome = "D:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
    options.add_experimental_option('excludeSwitches',
                                    ['enable-automation'])

    driver = webdriver.Chrome(executable_path=chrome, options=options)
    return driver


class URL(threading.Thread):
    def __init__(self, url, q, name, cookies=None):
        super().__init__()
        self.name = name
        self.url = url
        self.driver = init_driver()
        self.cookies = cookies
        self.video_url_list = {}
        self.q = q

    def get_url_by_cookie(self):
        self.driver.get(self.url)
        for item in self.cookies:
            try:
                item.pop('sameSite')
                # item.pop('secure')
            except:
                pass
            self.driver.add_cookie(item)
        self.driver.get(self.url)

    def run(self, nums=20, pages=1, fans=False, fans_gt=0) -> None:
        print("run %s" % self.name)
        self.get_url_by_cookie()
        while True:
            time.sleep(1)
            self.parser_pages(nums, pages, fans, fans_gt)
            self.driver.get(self.url)


    def parser_pages(self, nums, pages, fans, fans_gt):
        if len(self.video_url_list.keys()) > 9999:
            self.video_url_list.clear()
        page = 0
        _driver = self.driver
        while page < pages:
            _list = WebDriverWait(_driver, 50).until(lambda _driver: _driver.find_elements_by_class_name('r'))

            for l in _list[0:nums]:
                if fans:
                    nickname, fan_nums = self.get_up_info(l, _driver)
                    if int(fan_nums.replace(",", "")) >= fans_gt:
                        t = l.find_element_by_class_name('title')
                        title = t.get_attribute('title')
                        attr = t.get_attribute('href')
                        if self.video_url_list.get(attr):
                            self.video_url_list[attr] += 1
                        else:
                            self.video_url_list[attr] = 0
                        # self.q.put_nowait(t.get_attribute('href'))
                else:
                    t = l.find_element_by_class_name('title')
                    attr = t.get_attribute('href')
                    # title = t.get_attribute('title')

                    if self.video_url_list.get(attr) is not None:

                        self.video_url_list[attr] += 1
                    else:
                        self.video_url_list[attr] = 0

                        self.q.put_nowait(t.get_attribute('href'))
            # print(self.video_url_list)
            # print(len(self.video_url_list.keys()),'----',len(set(self.video_url_list.keys())))

            next = _driver.find_element_by_class_name('nav-btn')
            next.click()
            page += 1

    def get_up_info(self, ele, driver):
        up_info = ele.find_element_by_class_name('v-author')
        nickname = up_info.get_attribute('title')
        up_info.click()
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        try:
            fans = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name('n-fs'))
            fans = fans.get_attribute('title')
        except TimeoutException:
            log.get().info('fans time out')
            fans = 0

        print(nickname, fans)
        driver.close()
        driver.switch_to.window(windows[0])

        return nickname, fans

    # def run(self) -> None:


class Survive(threading.Thread):
    def __init__(self, url, q, name, cookies=None):
        super().__init__()
        self.name = name
        self.url = url
        self.driver = init_driver()
        self.cookies = cookies
        self.video_url_list = []
        self.q = q
        print("--init")

    def run(self) -> None:
        print("--run")
        self.get_url_by_cookie()
        # print("q", self.q.empty())
        while True:
            print("q", self.q.empty())
            if self.q.empty():
                break
            time.sleep(0.5)
            self.send_message()

    def get_url_by_cookie(self):
        self.driver.get(self.url)
        for item in self.cookies:
            try:
                item.pop('sameSite')
                # item.pop('secure')
            except:
                pass
            self.driver.add_cookie(item)
        self.driver.get(self.url)

    # WebDriverWait(self.driver, 50).until(lambda driver: driver.get(self.url))

    def send_message(self):
        textarea = None
        _driver = self.driver
        reply = random.choice(comments)

        url = self.q.get()
        count = 0
        _driver.get(url)

        while count < 10:
            _driver.execute_script('window.scrollTo(0,800)')
            try:
                textarea = _driver.find_element_by_class_name('textarea-container').find_element_by_tag_name(
                    'textarea')
                break
            except NoSuchElementException:

                time.sleep(2)
                count += 1
                # print("%s try time %s" % (self.name, count))

        if self.__no_more_reply(_driver) and textarea:
            count = 1
            while count < 5:
                try:
                    textarea.send_keys(reply)
                    break
                except ElementClickInterceptedException:
                    act = 'window.scrollTo(0,%s)' % (count * 100)
                    _driver.execute_script(act)
                    count += 1

            button = _driver.find_element_by_class_name('comment-submit')
            try:
                button.click()
                text = self.name + url + ":" + reply
                log.get().info(text)
            except Exception as e:
                text = "%s:发生错误%s" % (self.name, e)
                log.get().info(text)
        else:
            text = self.name + url + ":已被抢一楼"
            log.get().info(text)

    def __no_more_reply(self, driver):
        try:
            driver.find_element_by_class_name('no-more-reply')
            return True
        except NoSuchElementException:
            return False


if __name__ == '__main__':
    base_url = "https://www.bilibili.com/"
    url_pool = ["https://www.bilibili.com/v/game/esports/"]
    # url_pool=["https://www.bilibili.com/v/anime/serial#/"]
    # url = "https://www.bilibili.com/video/BV1uz411z7L1"

    for i, url in enumerate(url_pool):
        u = URL(url, q, "url_thread-%s" % i, cookies=cookies)
        t = threading.Thread(target=u.run, args=(), daemon=True)
        t.start()
        # t.join()
    time.sleep(1)
    for i in range(1, 3):
        s = Survive(base_url, q, "parse_thread-%s" % i, cookies=cookies)
        t = threading.Thread(target=s.run, args=())
        t.start()

    # get_bosh()
