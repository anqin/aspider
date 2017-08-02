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
import unittest

import config_load


class TestConfigLoad(unittest.TestCase):
    """testcases
    Attributes:
        craw_interval : craw interval
        crawl_timeout : crawl timeout
        max_depth : max depth
        output_directory : output directory
        target_url : target url
        thread_count : thread num
        url_list_file : url file
    """

    def setUp(self):
        self.default_keys = [
            'crawl_interval',
            'crawl_timeout',
            'max_depth',
            'output_directory',
            'target_url',
            'thread_count',
            'url_list_file'
            ]

    def testLoadConfNotExist(self):
        """test load_conf when file doesnot exist"""
        config = config_load.load_conf('not_exist')
        self.assertEqual(type(config), dict)
        sorted_keys = sorted(config.keys())
        self.assertEqual(sorted_keys, self.default_keys)

    def testLoadConfNone(self):
        """test load_conf when file not given"""
        config = config_load.load_conf()
        self.assertEqual(type(config), dict)
        sorted_keys = sorted(config.keys())
        self.assertEqual(sorted_keys, self.default_keys)

    def testLoadConfDefault(self):
        """test load_conf:default conf"""
        config_file = os.path.join('..', 'spider.conf')
        config = config_load.load_conf(config_file)
        self.assertEqual(type(config), dict)
        sorted_keys = sorted(config.keys())
        self.assertEqual(sorted_keys, self.default_keys)

    def tearDown(self):
        pass


def suite():
    """return test suite"""
    tests = [
            'testLoadConfNotExist',
            'testLoadConfNone',
            'testLoadConfDefault',
            ]
    return unittest.TestSuite(map(TestConfigLoad, tests))


if __name__ == '__main__':
    unittest.main()
