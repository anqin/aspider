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

from disk_queue import DiskQueue
import seedfile_load


class TestSeedFileLoad(unittest.TestCase):
    """testcases
    Attributes:
        default_seed_file : default seed file
        q : url queue
    """

    def setUp(self):
        RootDir = os.path.dirname(seedfile_load.__file__)
        self.default_seed_file = os.path.join(RootDir, 'urls')
        self.q = DiskQueue('./test_seedfile_load_queue')

    def testLoadSeedfile(self):
        """test load_seedfile"""
        seedfile_load.load_seedfile(self.default_seed_file, self.q)
        self.assertTrue(self.q.qsize() > 0)
        url_tuple = self.q.get()
        self.assertEqual(type(url_tuple), tuple)
        self.assertTrue(url_tuple[0].startswith('http'))
        self.assertEqual(type(url_tuple[1]), int)


def suite():
    """return test suites"""
    tests = ['testLoadSeedfile']
    return unittest.TestSuite(map(TestSeedFileLoad, tests))


if __name__ == '__main__':
    unittest.main()
