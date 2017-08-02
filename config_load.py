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


import configparser
import os


def load_conf(conf=None):
    """load configuration"""
    BaseDir = os.path.dirname(__file__)
    if not conf or not os.path.isfile(conf):
        conf = os.path.join(BaseDir, 'spider.conf')
    conf_parser = configparser.ConfigParser()
    config = {}
    try:
        conf_parser.read(conf)
        for sec in conf_parser.sections():
            config[sec] = dict(conf_parser.items(sec))
    except configparser.ParsingError:
        config['spider'] = {}
    return config['spider']


if __name__ == '__main__':
    config = load_conf()
    print(config)
