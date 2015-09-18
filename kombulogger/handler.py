# -*- coding: utf-8 -*-

import logging
import socket
import datetime
import time

import kombu

from kombulogger import default_broker_url, default_queue_name


class KombuHandler(logging.Handler):

    refresh_connection_interval = datetime.timedelta(minutes=8)

    def __init__(self, url=None, queue=None):
        logging.Handler.__init__(self)
        self.level = logging.INFO
        self.hostname = socket.gethostname()

        self.url = url or default_broker_url
        self.queue_name = queue or default_queue_name

        self._connected_time = datetime.datetime.utcnow()
        self.connection = None
        self.queue = None
        self.retries = 0

        self._connect()

    def _connect(self):
        now = datetime.datetime.utcnow()
        expired = now - self._connected_time > self.refresh_connection_interval
        if self.connection is None or expired:
            self.connection = kombu.Connection(self.url)
            self.queue = self.connection.SimpleQueue(self.queue_name,
                                                     no_ack=True)
            self._connected_time = now

    def _record_to_dict(self, record):
        return {
            'message': self.format(record),
            'level': record.levelname,
            'host': self.hostname,
        }

    def emit(self, record):
        self._connect()
        try:
            content = self._record_to_dict(record)
            self.queue.put(content)
        except:
            try:
                self.close()
            except:
                pass
            self.connection = None

            if self.retries < 3:
                time.sleep(0.3)  # throttle just a bit
                self.emit(record)
                self.retries += 1
            else:
                self.retries = 0

    def close(self):
        self.queue.close()
        self.connection.close()
