#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2017 SenseDeal AI, Inc. All Rights Reserved
#
################################################################################
"""
Author: Tony Qin (tony@sensedeal.ai)
Date:2017/7/31
"""


import logging
import socket
import threading

import spider_conf
import webpage


class CrawlerThread(threading.Thread):
    """Crawler thread
    Attributes:
        url_queue:the queue contains url
        thread_name:name of the thread
        conf:the name of conf
        history_urls:history urls crawled
    """

    def __init__(self, url_queue, thread_name, conf, storage, history_urls=None, mutex=None):
        super(CrawlerThread, self).__init__(name = thread_name)
        self.url_queue = url_queue
        self.conf = conf
        self.storage = storage
        if type(history_urls) != list:
            self.history_urls = []
        else:
            self.history_urls = history_urls
        self.mutex = mutex

    def run(self):
        """run thread"""
        logging.info('%s started', self.name)
        socket.setdefaulttimeout(self.conf.timeout)
        try:

            self.parser = webpage.WebpageParser(self.conf.max_depth,
                    out_path=self.conf.output_directory,
                    pattern=self.conf.target_url,
                    url_queue=self.url_queue,
                    storage=self.storage,
                    crawler_name=self.name,
                    interval=self.conf.interval,
                    history_urls=self.history_urls,
                    mutex=self.mutex)
            self.parser.start()
        except:
            logging.error('%s run fail', self.name)
        logging.info('%s finished', self.name)


if __name__ == '__main__':
    config = {u'target_url': u'.*.(htm|html)$;',
            u'output_directory': u'./output;',
            u'crawl_timeout': u'1;',
            u'crawl_interval': u'1;',
            u'url_list_file': u'./urls;',
            u'max_depth': u'2;'}
    conf = spider_conf.SpiderConf(conf=config)
    import disk_queue
    q = DiskQueue('./crawl_thread_queue')
    q.put(('http://www.baidu.com/', 0))
    crawler = CrawlerThread(q, 'crawler', conf)
    crawler.run()
