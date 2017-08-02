#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2017 SenseDeal AI, Inc. All Rights Reserved
#
################################################################################
"""
mini spider
Author: Tony Qin (tony@sensedeal.ai)
Date:2017/7/31
"""


import argparse
import logging

import sys
import threading

import config_load
import crawl_thread
import seedfile_load
import spider_conf

from disk_queue import DiskQueue
from storage import Storage

# reload(sys)
# sys.setdefaultencoding('utf-8')


class MiniSpider(object):
    """
    Attributes:
        url_queue:the queue consists of url
    """

    def __init__(self):
        self.url_queue = DiskQueue("./crawler_queue")

    def log_config(self):
        """log configuration"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a %d %b %Y %H:%M:%S',
            filename='spider.log',
            filemode='a+')

    def main(self):
        """main function"""
        parser = argparse.ArgumentParser()
        VERSION = '0.0.1'
        parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0')
        parser.add_argument("-c", "--conf", help="assign config file")
        args, remaining = parser.parse_known_args(sys.argv)
        conf_file = args.conf
        try:
            spider_conf_info = config_load.load_conf(conf_file)
        except Exception as e:
            logging.error("load conf failed: %s", e)
        thread_count = int(spider_conf_info['thread_count'])
        self.log_config()
        logging.info("Mini Spider activated")
        conf = spider_conf.SpiderConf(spider_conf_info)
        try:
            seedfile_load.load_seedfile(spider_conf_info['url_list_file'], self.url_queue)
        except Exception as e:
            logging.error("load load_seedfile failed: %s", e)
        if self.url_queue.qsize() <= 0:
            logging.error("FATAL: no urls loaded, exit!")
            sys.exit(1)
        db_store = Storage(conf=conf)
        history_urls = []
        threads = []
        mutex = threading.Lock()
        for i in range(thread_count):
            crawler = crawl_thread.CrawlerThread(url_queue=self.url_queue,
                    thread_name="Crawler" + '_' + str(i), conf=conf,
                    storage=db_store,
                    history_urls=history_urls, mutex=mutex)
            threads.append(crawler)
            crawler.setDaemon(True)
            crawler.start()
        self.url_queue.join()
        for thread in threads:
            if thread.isAlive():
                logging.info("%s, waiting to terminate", thread.name)
                thread.join(1)
        logging.info("Crawler exited")


if __name__ == '__main__':
    mini_spider = MiniSpider()
    mini_spider.main()
