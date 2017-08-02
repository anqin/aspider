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


class SpiderConf(object):
    """
    Attributions:
        max_depth:max depth
        output_directory:directory of the result
        target_url: target url
        timeout:timeout
        interval:interval
    """

    def __init__(self, conf=None):
        if not conf:
            conf = {}
        self.max_depth = 2
        self.output_directory = '.'
        self.target_url = ''
        self.timeout = 10
        self.interval = 1

        self.linkbase_db_name = 'linkbase.db'
        self.linkbase_db_dir = '.'
        self.pagebase_db_name = 'pagebase.db'
        self.pagebase_db_dir = '.'
        self.pdfbase_db_name = 'pdfbase.db'
        self. pdfbase_db_dir = '.'

        try:
            self.max_depth = int(conf.get('max_depth', '2'))
            self.output_directory = conf.get('output_directory', '.')
            self.target_url = conf.get('target_url')
            self.timeout = float(conf.get('crawl_timeout', '10'))
            self.interval = float(conf.get('crawl_interval', '1'))

            self.linkbase_db_name = conf.get('linkbase_db_name', 'linkbase.db')
            self.linkbase_db_dir = conf.get('linkbase_db_dir', './output')
            self.pagebase_db_name = conf.get('pagebase_db_name', 'pagebase.db')
            self.pagebase_db_dir = conf.get('pagebase_db_dir', './output')
            self.pdfbase_db_name = conf.get('pdfbase_db_name', 'pdfbase.db')
            self.pdfbase_db_dir = conf.get('pdfbase_db_dir', './output')
            logging.info("config loaded successfully")
        except AttributeError:
            logging.error("loading config failed: %s, using default values", conf)


# def load_config_info(c_conf, s_conf):
#     crawler_conf = {}
#     storage_conf = {}

#     if c_conf:
#         try:
#             crawler_conf.max_depth = int(c_conf.get('max_depth', '2'))
#             crawler_conf.output_directory = c_conf.get('output_directory', '.')
#             crawler_conf.target_url = c_conf.get('target_url')
#             crawler_conf.timeout = float(c_conf.get('crawl_timeout', '10'))
#             crawler_conf.interval = float(c_conf.get('crawl_interval', '1'))
#         except AttributeError:
#             logging.error("loading config failed: %s, using default values", c_conf)

#     if s_conf:
#         try:
#             storage_conf.linkbase_db_name = s_conf.get('linkbase_db_name', 'linkbase.db')
#             storage_conf.linkbase_db_dir = s_conf.get('linkbase_db_dir', './output')
#             storage_conf.pagebase_db_name = s_conf.get('pagebase_db_name', 'pagebase.db')
#             storage_conf.pagebase_db_dir = s_conf.get('pagebase_db_dir', './output')
#             storage_conf.pdfbase_db_name = s_conf.get('pdfbase_db_name', 'pdfbase.db')
#             storage_conf.pdfbase_db_dir = s_conf.get('pdfbase_db_dir', './output')
#         except AttributeError:
#             logging.error("loading config failed: %s, using default values", s_conf)

#     return crawler_conf, storage_conf


if __name__ == '__main__':
    import config_load
    conf = config_load.load_conf('./spider.conf');
    info = SpiderConf(conf)
    print(info)
