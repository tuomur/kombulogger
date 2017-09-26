# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import gzip
import logging
from logging.handlers import TimedRotatingFileHandler
import shutil

import kombu

from kombulogger import default_broker_url, default_queue_name


def namer(name):
    return name + ".gz"


def rotator(source, dest):
    with open(source, 'rb') as sourcef:
        with gzip.open(dest, 'wb') as destf:
            shutil.copyfileobj(sourcef, destf)
    os.remove(source)


class KombuLogServer(object):

    log_format = u'{host}\t{level}\t{message}'

    def __init__(self, url=None, queue=None):
        url = url or default_broker_url
        queue = queue or default_queue_name

        self.connection = kombu.Connection(url)
        self.queue = self.connection.SimpleQueue(queue, no_ack=True)

        path = os.path.join(os.getcwd(), queue)

        if not path.endswith('.log'):
            path += '.log'

        handler = TimedRotatingFileHandler(path, when='W0', backupCount=8)
        handler.rotator = rotator
        handler.namer = namer
        handler.setFormatter(logging.Formatter())

        self.output = logging.getLogger()
        self.output.setLevel(logging.INFO)
        self.output.addHandler(handler)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.queue.close()
        self.connection.close()
        return False

    def _format_dict(self, log_dict):
        try:
            return self.log_format.format(**log_dict)
        except UnicodeEncodeError:
            try:
                return u'kombulogger: Cannot format payload: {0!r}'.format(log_dict)
            except UnicodeEncodeError:
                return u'kombulogger: Cannot format payload'

    def run(self):
        while True:
            try:
                message = self.queue.get(block=True, timeout=1)
                payload = message.payload
                self.output.info(self._format_dict(payload))
                message.ack()
            except self.queue.Empty:
                pass
