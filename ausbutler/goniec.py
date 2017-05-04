import socket

from .tour_config import Constants


class Goniec(object):
    def __init__(self, config):
        self.config = config

    def send(self, files):
        if self.config['enabled']:
            try:
                content_lines = [Constants.path] + files + ['bye', '']
                goniec = socket.socket()
                goniec.connect((self.config['host'], self.config['port']))
                goniec.sendall('\n'.join(content_lines))
                goniec.close()
            except socket.error:
                print 'WARNING: unable to send files via Goniec'
