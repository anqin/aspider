#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2017 SenseDeal AI, Inc. All Rights Reserved
#
################################################################################
"""
craw_thread 单测
Author: Tony Qin (tony@sensedeal.ai)
Date:2017/7/31
"""


import os
import sys
sys.path.append("..")
import threading
import unittest

from disk_queue import DiskQueue
import crawl_thread


class TestCrawlThread(unittest.TestCase):
    """testcases
    Attributes:
        config : config file
        q : url_queue
        name : crawler name
    """

    def setUp(self):
        self.config = {}
        self.q = DiskQueue('./test_crawl_thread_queue')
        self.name = 'crawler'

    def testInitThread(self):
        """test init thread"""
        self.crawler = crawl_thread.CrawlerThread(self.q, self.name, self.config)
        self.assertIsInstance(self.crawler, threading.Thread)
        self.assertEqual(self.crawler.name, self.name)

    def tearDown(self):
        pass


def suite():
    """return test suite"""
    tests = [
            'testInitThread'
            ]
    return unittest.TestSuite(map(TestCrawlThread, tests))


if __name__ == '__main__':
    unittest.main()
