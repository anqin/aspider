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


from html.parser import HTMLParser
from urllib import parse as urlparse
from retrying import retry

import logging
import multiprocessing
import os
import random
import re
import time
import urllib
import urllib.request


class HrefParser(HTMLParser):
    """HTML parser
    Attributes:
        links:list of urls
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            if len(attrs) == 0:
                pass
            else:
                for k, v in attrs:
                    if k == 'href':
                        self.links.append(v)

    def clear(self):
        """clear links"""
        self.links = []


class WebpageParser(object):
    """Webpage Parser
    Attributes:
        max_depth : max depth
        url_sets : sets of url
        out_path : output directory
        base_url : base url
        crawler_name : crawler name
    """

    def __init__(self, max_depth, out_path='.', pattern='',
            url_queue=None, storage=None,
            crawler_name='Crawler', interval=0.5,
            history_urls=None, mutex=None):
        self.max_depth = max_depth
        self.url_sets = []
        self.html = ''
        self.parser = HrefParser()
        self.out_path = out_path
        self.base_url = ''
        self.fetched_urls = []
        self.url_queue = url_queue
        self.storage = storage
        self.pattern = pattern
        self.crawler_name = crawler_name
        self.interval = interval
        self.history_urls = history_urls
        self.mutex = mutex
        if not os.path.exists(self.out_path):
            try:
                os.mkdir(self.out_path)
            except OSError as e:
                logging.warning("%s mkdir %s failed: %s, use current dir by default",
                                self.crawler_name, self.out_path, e)
                self.out_path = '.'

#     @retry(RuntimeError, tries=3, delay=1)
    @retry(stop_max_attempt_number=3, wait_fixed=1)
    def start(self, auto_terminate=False):
        """start parse"""
        logging.info("%s called start(), queue len:%s ",
                self.crawler_name, self.url_queue.qsize())
        count = 0
        while True:
            if auto_terminate:
                if count > 10:
                    return
                if self.url_queue.qsize() <= 0:
                    time.sleep(0.1)
                    count += 1
                    continue
            url, depth = self.url_queue.get()
            if url not in self.history_urls:
                try:
                    self.mutex.acquire()
                    logging.debug('%s, acquired lock', self.crawler_name)
                    self.history_urls.append(url)
                except RuntimeError as e:
                    logging.error('%s, acquire lock failed, %s', self.crawler_name, e)
                try:
                    self.mutex.release()
                    logging.debug('%s, release lock', self.crawler_name)
                except threading.ThreadError as e:
                    logging.error('%s, try release unacquired lock', self.crawler_name)
                    return
            self.base_url = url
            self.parse(url, depth)
            self.url_queue.task_done()
            time.sleep(self.interval)
        logging.info('%s job finished', self.crawler_name)

    def parse(self, url, depth):
        """Parse url"""
        if depth > self.max_depth:
            return
        if url[-4:] == '.pdf':
            self.save(url)
            return
        try:
            url = urlparse.quote(url.encode('utf-8'), ':/')
            self.html = urllib.request.urlopen(url).read().decode('utf-8')
        except IOError as err:
            logging.error('err: %s, %s', err, url)
            return
        except UnicodeError as err:
            logging.error('err: %s, %s', err, url)
            # need to deal with pdf file
            logging.debug('unicode error, ext: %s', url[-4:])
            return
        except Exception as err:
            logging.error('err: %s, %s', err, url)
            return
        self.decode(url)
        try:
            self.html = self.parser.unescape(self.html)
            self.parser.feed(self.html)
#         except UnicodeDecodeError as err:
        except Exception as err:
            logging.warning("parse url: %s failed, %s", url, err)
            return
        self.parser.close()
        self.url_sets += [urlparse.urljoin(self.base_url, suffix) for suffix in self.parser.links]
        self.parser.clear()
        for u in self.url_sets:
            if depth + 1 <= self.max_depth:
                self.url_queue.put((u, depth + 1))
        self.save(url)

    def save(self, url):
        """save page to file"""
        if re.match(self.pattern, url) and url not in self.fetched_urls:
            self.fetched_urls.append(url)
            if self.storage != None:
                self.storage.pagebase.save_to_disk(url, self.html)
                self.storage.linkbase.set(url)
        elif url[-4:] == '.pdf' and url not in self.fetched_urls:
            self.fetched_urls.append(url)
            if self.storage != None:
                self.storage.pdfbase.save_to_disk(url)
                self.storage.linkbase.set(url)

    def decode(self, url):
        """decode webpage"""
        charset_pattern = r'charset=\"?(.*?)\"'
        default_charset = 'utf-8'
        try:
            charset = re.findall(charset_pattern, self.html)[0].lower()
        except IndexError:
            logging.warning("no charset found for url: %s, use utf-8 by default", url)
            charset = default_charset
        except Exception as err:
            logging.error('err: %s, %s', err, url)
#             return
        if charset != 'utf-8':
            try:
                self.html = str(self.html).decode(charset)
            except Exception as err:
                logging.error("decoding html failed: %s, with charset: %s, err: %s",
                    url, charset, err)


if __name__ == '__main__':
    import disk_queue

    q = DiskQueue('./webpage_queue')
    q.push(('http://www.neeq.com.cn/', 0))
    parser = WebpageParser(2, out_path='./output',
            pattern='.*\.(htm|html)$', url_queue=q, crawler_name='test')
    parser.start()
    print('done')
