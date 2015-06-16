# -*- coding: utf-8 -*-

import logging
import socket

import kombu

from kombulogger import default_broker_url, default_queue_name


class KombuHandler(logging.Handler):

    def __init__(self, url=None, queue=None):
        logging.Handler.__init__(self)
        self.level = logging.INFO
        self.hostname = socket.gethostname()

        url = url or default_broker_url
        queue = queue or default_queue_name

        self.connection = kombu.Connection(url)
        self.queue = self.connection.SimpleQueue(queue, no_ack=True)

    def _record_to_dict(self, record):
        return {
            'message': self.format(record),
            'level': record.levelname,
            'host': self.hostname,
        }

    def emit(self, record):
        content = self._record_to_dict(record)
        self.queue.put(content)

    def close(self):
        self.queue.close()
        self.connection.close()
