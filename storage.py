#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2017 SenseDeal AI, Inc. All Rights Reserved
#
################################################################################

"""
Author: Tony Qin (tony@sensedeal.ai)
Date:2017/8/1
"""
import os
import sqlite3
import logging
import subprocess

from datetime import datetime, date
from urllib.parse import urlparse

from safe_sqlite import SafeSqlite


def get_storage_key_from_url(url):
    url_obj = urlparse(url)
    domain = url_obj.hostname
    key = ''
    for i in reversed(domain.split('.')):
        if i != 'www':
            if key == '':
                key = i
            else:
                key = key + '.' + i
    return (key + url_obj.path).replace('/', '__')


class LinkBaseNotSafe(object):
    """
    Crawler data caching per relative URL and domain.
    Non-thread-safe implementation
    """
    def __init__(self, crawler_name='Crawler', db_name='linkbase.db', db_dir='.'):
        self.crawler_name = crawler_name
        self.db_name = db_name
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            try:
                os.mkdir(self.db_dir)
            except OSError as e:
                logging.warning("%s mkdir %s failed: %s, use current dir by default",
                                self.crawler_name, self.db_dir, e)


        self.conn = sqlite3.connect(os.sep.join([db_dir, db_name]))
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sites
                        (key text not null, url text not null, content text,
                         in_time timestamp, crawled_time timestamp,
                         weight real, unique(key, url))''')
        self.conn.commit()
        self.cursor = self.conn.cursor()

    def set(self, url):
        """
        store the content for a given domain and relative url
        """
        try:
            self.cursor.execute(
                "INSERT INTO sites(key, url, in_time, crawled_time, weight) VALUES (?,?,?,?,?)",
                (get_storage_key_from_url(url), url,
                  datetime.now(), datetime.now(), 0))
            self.conn.commit()
        except Exception as err:
            logging.warning('insert database fail, %s', err)

    def get(self, key):
        """
        return the content for a given domain and relative url
        """
        self.cursor.execute("SELECT url FROM sites WHERE key=?",
            (key,))
        row = self.cursor.fetchone()
        if row:
            return row[0]

    def get_urls(self, domain):
        """
        return all the URLS within a domain
        """
        self.cursor.execute("SELECT url FROM sites WHERE domain=?", (domain,))
        return [row[0] for row in self.cursor.fetchall()]


class LinkBase(object):
    """
    Crawler data caching per relative URL and domain.
    Thread-safe implementation
    """
    def __init__(self, crawler_name='Crawler', db_name='linkbase.db', db_dir='.'):
        self.crawler_name = crawler_name
        self.db_name = db_name
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            try:
                os.mkdir(self.db_dir)
            except OSError as e:
                logging.warning("%s mkdir %s failed: %s, use current dir by default",
                                self.crawler_name, self.db_dir, e)


        self.safe_sqlite = SafeSqlite(os.sep.join([db_dir, db_name]))
        self.safe_sqlite.execute('''CREATE TABLE IF NOT EXISTS sites
                        (key text not null, url text not null, content text,
                         in_time timestamp, crawled_time timestamp,
                         weight real, unique(key, url))''')

    def __del__(self):
        self.safe_sqlite.close()

    def set(self, url):
        """
        store the content for a given domain and relative url
        """
        try:
            self.safe_sqlite.execute(
                "INSERT INTO sites(key, url, in_time, crawled_time, weight) VALUES (?,?,?,?,?)",
                (get_storage_key_from_url(url), url,
                  datetime.now(), datetime.now(), 0))
        except Exception as err:
            logging.warning('insert database fail, %s', err)

    def get(self, key):
        """
        return the content for a given domain and relative url
        """
        row = self.safe_sqlite.execute("SELECT url FROM sites WHERE key=?", (key,))
        if row:
            return row[0]

    def get_urls(self, domain):
        """
        return all the URLS within a domain
        """
        self.cursor.execute("SELECT url FROM sites WHERE domain=?", (domain,))
        return [row[0] for row in self.cursor.fetchall()]


class PageBase(object):
    """
    Crawler webpage caching per URL and domain
    """
    def __init__(self, crawler_name='Crawler', db_name='pagebase.db', db_dir='.'):
        self.crawler_name = crawler_name
        self.db_name = db_name
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            try:
                os.mkdir(self.db_dir)
            except OSError as e:
                logging.warning("%s mkdir %s failed: %s, use current dir by default",
                                self.crawler_name, self.db_dir, e)

    def save_to_disk(self, url, html, path=None):
        if path == None:
            path = self.db_dir
#         out_file_name = os.sep.join([path, url.replace('://', '_').replace('/', '_')])
        out_file_name = os.sep.join([path, get_storage_key_from_url(url)])
        logging.info('%s, saving %s,to: %s', self.crawler_name, url, out_file_name)
        try:
            with open(out_file_name, 'w') as f:
                f.write(html)
        except Exception as e:
            logging.error("save html: %s ,to file error %s ", html, e)


    def save_to_global(self, url, html):
        """
        save to global distributed storage
        """
        return


class PdfBase(object):
    """
    Crawler webpage caching per URL and domain
    """
    def __init__(self, crawler_name='Crawler', db_name='pdfbase.db', db_dir='.'):
        self.crawler_name = crawler_name
        self.db_name = db_name
        self.db_dir = db_dir
        if not os.path.exists(self.db_dir):
            try:
                os.mkdir(self.db_dir)
            except OSError as e:
                logging.warning("%s mkdir %s failed: %s, use current dir by default",
                                self.crawler_name, self.db_dir, e)

    def save_to_disk(self, url, path=None):
        if path == None:
            path = self.db_dir
        out_file_name = os.sep.join([path, get_storage_key_from_url(url)])
        logging.info('%s, saving %s,to: %s', self.crawler_name, url, out_file_name)
        try:
            cmd = 'wget %s -O %s' %(url, out_file_name)
            print (cmd)
            out_bytes = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error("save pdf: %s ,to file error %s ", url, e)
            print (out_bytes.decode('utf-8'))


    def save_to_global(self, url, pdf):
        """
        save to global distributed storage
        """
        return


class Storage(object):
    """
    the level for storage interface, including links and webpage
    """
    def __init__(self, crawler_name='Crawler', conf=None):
        self.conf = conf
        self.crawler_name = crawler_name
        self.linkbase = LinkBase(crawler_name, conf.linkbase_db_name, conf.linkbase_db_dir)
        self.pagebase = PageBase(crawler_name, conf.pagebase_db_name, conf.pagebase_db_dir)
        self.pdfbase = PdfBase(crawler_name, conf.pdfbase_db_name, conf.pdfbase_db_dir)


if __name__ == '__main__':
    url = 'http://www.neeq.com.cn/uploads/1/file/public/201707/20170731184707_wf92rrp3uj.pdf'
#     pdfbase = PdfBase('1', '2', './test_out')
#     pdfbase.save_to_disk(url)
    linkbase = LinkBase()
    linkbase.set(url)
    print (linkbase.get((get_storage_key_from_url(url))))
