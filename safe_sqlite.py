#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2017 SenseDeal AI, Inc. All Rights Reserved
#
################################################################################
"""
Author: Tony Qin (tony@sensedeal.ai)
Date:2017/8/2
"""

import logging
try:
    import queue as Queue # module re-named in Python 3
except ImportError:
    import Queue
import sqlite3
import threading
import time
import uuid


class SafeSqlite(threading.Thread):
    """Sqlite thread safe object.

    Example:
        from SafeSqlite import SafeSqlite
        sql_worker = SafeSqlite("/tmp/test.sqlite")
        sql_worker.execute(
            "CREATE TABLE tester (timestamp DATETIME, uuid TEXT)")
        sql_worker.execute(
            "INSERT into tester values (?, ?)", ("2010-01-01 13:00:00", "bow"))
        sql_worker.execute(
            "INSERT into tester values (?, ?)", ("2011-02-02 14:14:14", "dog"))
        sql_worker.execute("SELECT * from tester")
        sql_worker.close()
    """
    def __init__(self, file_name, max_queue_size=100):
        """Automatically starts the thread.

        Args:
            file_name: The name of the file.
            max_queue_size: The max queries that will be queued.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.sqlite3_conn = sqlite3.connect(
            file_name, check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES)
        self.sqlite3_cursor = self.sqlite3_conn.cursor()
        self.sql_queue = Queue.Queue(maxsize=max_queue_size)
        self.results = {}
        self.max_queue_size = max_queue_size
        self.exit_set = False
        # Token that is put into queue when close() is called.
        self.exit_token = str(uuid.uuid4())
        self.start()
        self.thread_running = True

    def run(self):
        """Thread loop.

        This is an infinite loop.  The iter method calls self.sql_queue.get()
        which blocks if there are not values in the queue.  As soon as values
        are placed into the queue the process will continue.

        If many executes happen at once it will churn through them all before
        calling commit() to speed things up by reducing the number of times
        commit is called.
        """
        logging.debug("run: Thread started")
        execute_count = 0
        for token, query, values in iter(self.sql_queue.get, None):
#             logging.debug("sql_queue: %s", self.sql_queue.qsize())
            if token != self.exit_token:
#                 logging.debug("run: %s", query)
                self.run_query(token, query, values)
                execute_count += 1
                # Let the executes build up a little before committing to disk
                # to speed things up.
                if (
                        self.sql_queue.empty() or
                        execute_count == self.max_queue_size):
#                     logging.debug("run: commit")
                    self.sqlite3_conn.commit()
                    execute_count = 0
            # Only exit if the queue is empty. Otherwise keep getting
            # through the queue until it's empty.
            if self.exit_set and self.sql_queue.empty():
                self.sqlite3_conn.commit()
                self.sqlite3_conn.close()
                self.thread_running = False
                return

    def run_query(self, token, query, values):
        """Run a query.

        Args:
            token: A uuid object of the query you want returned.
            query: A sql query with ? placeholders for values.
            values: A tuple of values to replace "?" in query.
        """
        if query.lower().strip().startswith("select"):
            try:
                self.sqlite3_cursor.execute(query, values)
                self.results[token] = self.sqlite3_cursor.fetchall()
            except sqlite3.Error as err:
                # Put the error into the output queue since a response
                # is required.
                self.results[token] = (
                    "Query returned error: %s: %s: %s" % (query, values, err))
                logging.error(
                    "Query returned error: %s: %s: %s", query, values, err)
        else:
            try:
                self.sqlite3_cursor.execute(query, values)
            except sqlite3.Error as err:
                logging.error(
                    "Query returned error: %s: %s: %s", query, values, err)

    def close(self):
        """Close down the thread and close the sqlite3 database file."""
        self.exit_set = True
        self.sql_queue.put((self.exit_token, "", ""), timeout=5)
        # Sleep and check that the thread is done before returning.
        while self.thread_running:
            time.sleep(.01)  # Don't kill the CPU waiting.

    @property
    def queue_size(self):
        """Return the queue size."""
        return self.sql_queue.qsize()

    def query_results(self, token):
        """Get the query results for a specific token.

        Args:
            token: A uuid object of the query you want returned.

        Returns:
            Return the results of the query when it's executed by the thread.
        """
        delay = .001
        while True:
            if token in self.results:
                return_val = self.results[token]
                del self.results[token]
                return return_val
            # Double back on the delay to a max of 8 seconds.  This prevents
            # a long lived select statement from trashing the CPU with this
            # infinite loop as it's waiting for the query results.
            logging.debug("Sleeping: %s %s", delay, token)
            time.sleep(delay)
            if delay < 8:
                delay += delay

    def execute(self, query, values=None):
        """Execute a query.

        Args:
            query: The sql string using ? for placeholders of dynamic values.
            values: A tuple of values to be replaced into the ? of the query.

        Returns:
            If it's a select query it will return the results of the query.
        """
        if self.exit_set:
            logging.debug("Exit set, not running: %s", query)
            return "Exit Called"
#         logging.debug("execute: %s", query)
        values = values or []
        # A token to track this query with.
        token = str(uuid.uuid4())
        # If it's a select we queue it up with a token to mark the results
        # into the output queue so we know what results are ours.
        if query.lower().strip().startswith("select"):
            self.sql_queue.put((token, query, values), timeout=5)
            return self.query_results(token)
        else:
            self.sql_queue.put((token, query, values), timeout=5)
