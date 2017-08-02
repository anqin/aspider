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

import os
import sys
sys.path.append("..")
import threading
import unittest

from disk_queue import DiskQueue
import webpage


class TestWebPageParser(unittest.TestCase):
    """testcases
    Attributes:
        q : url queue
    """

    def setUp(self):
        self.q = DiskQueue('./test_webpage_queue')
        self.q.put(('http://www.baidu.com/', 0))
        self.mutex = threading.Lock()
        self.history_urls = []

    def testWebpageParser(self):
        """test WebpageParser"""
        parser = webpage.WebpageParser(2, out_path='./out',
            pattern='.*\.(htm|html)$', url_queue=self.q,
            crawler_name='test', mutex=self.mutex,
            history_urls=[])
        self.assertIsInstance(parser, webpage.WebpageParser)
        self.assertEqual(parser.crawler_name, 'test')
        parser.start(auto_terminate=True)
        self.assertTrue(os.path.isdir('./out'))

    def tearDown(self):
        for f in os.listdir('./out'):
            os.remove(os.path.join('./out', f))
        os.rmdir('./out')


def suite():
    """return test suite"""
    tests = ['testWebpageParser']
    return unittest.TestSuite(map(TestWebPageParser, tests))


if __name__ == '__main__':
    unittest.main()
