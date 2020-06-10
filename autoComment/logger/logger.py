# -*- coding:utf-8 -*-
import datetime
import logging
import time
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from logging import FileHandler
import os

BaseDir = os.path.abspath(os.path.dirname(__file__))
print(BaseDir)


class Logger:
    def __init__(self, loggername: str, filename):
        self.loggername = loggername
        self.cache_day = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
        self.logger = logging.getLogger(self.loggername)

        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件

        self.fh = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=300)  # 指定utf-8格式编码，避免输出的日志文本乱码

        # self.fh = FileHandler('config/{}.log'.format(self.cache_day))

        self.fh.setLevel(logging.DEBUG)

        # 创建一个handler，用于将日志输出到控制台
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        self.fh.setFormatter(formatter)
        self.ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)

    def reset_log(self):
        pass

    def get(self):
        """定义一个函数，回调logger实例"""
        return self.logger



if __name__ == '__main__':
    pass
