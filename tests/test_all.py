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
import unittest

import test_config_load
import test_crawl_thread
import test_seedfile_load
import test_spider_conf
import test_webpage
sys.path.append("..")


def main():
    suites = []
    suites.append(test_config_load.suite())
    suites.append(test_seedfile_load.suite())
    suites.append(test_crawl_thread.suite())
    suites.append(test_spider_conf.suite())
    suites.append(test_webpage.suite())
    test_suites = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(test_suites)


if __name__ == '__main__':
    main()
