# -*- coding: utf-8 -*-

from __future__ import print_function

from .server import KombuLogServer


print('Starting server. Ctrl-C to stop.')

try:
    with KombuLogServer() as server:
        server.run()
except (KeyboardInterrupt, SystemExit):
    pass
