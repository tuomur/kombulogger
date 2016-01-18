# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import codecs

import kombu

from kombulogger import default_broker_url, default_queue_name


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

        self.output_file = codecs.open(path, mode='ab',
                                       encoding='UTF-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.queue.close()
        self.connection.close()
        self.output_file.close()
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
        kwargs = dict(file=self.output_file)
        if sys.version_info >= (3, 3):
            kwargs['flush'] = True
        while True:
            try:
                message = self.queue.get(block=True, timeout=1)
                payload = message.payload
                print(self._format_dict(payload), **kwargs)
                message.ack()
            except self.queue.Empty:
                pass
