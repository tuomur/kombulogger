# -*- coding: utf-8 -*-

import os

default_broker_url = os.environ.get('KOMBULOG_BROKER_URL', 'amqp://')
default_queue_name = os.environ.get('KOMBULOG_QUEUE', 'kombulog')

from .handler import KombuHandler
