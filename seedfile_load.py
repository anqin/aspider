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
import disk_queue


def load_seedfile(seed, url_queue):
    """ load seedfile to queue"""
    if not os.path.isfile(seed):
        seed = './urls'
    try:
        with open(seed) as s:
            urls = s.readlines()
    except IOError:
        urls = []
    for url in urls:
        url_queue.put((url.strip(), 0))


if __name__ == '__main__':
    url_queue = DiskQueue('./seedfile_load_queue')
    load_seedfile('./urls', url_queue)
    print(url_queue.qsize())
