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
import shutil
import logging
# from persistqueue import Queue
import queue

class DiskQueue(object):
    """
    Persistent queue for spider scheduling
    """
    def __init__(self, queue_name):
        self.name = queue_name
#         self.queue = Queue(queue_name)
        self.queue = queue.Queue()

    def __del__(self):
        if self.qsize() == 0 and os.path.exists(self.name):
            shutil.rmtree(self.name)

    def put(self, item):
        self.queue.put(item)

    def get(self):
        return self.queue.get()

    def qsize(self):
        return self.queue.qsize()

    def task_done(self):
        self.queue.task_done()

    def join(self):
        self.queue.join()
