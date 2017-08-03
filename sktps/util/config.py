# -*- coding: utf-8 -*-
import json

import os

from singleton import SingletonMixin


class Config(SingletonMixin):
    def __init__(self):
        super(Config, self).__init__()
        self.config = None
        cur = os.path.dirname(os.path.realpath(__file__))
        self.filename = cur + '/../config/config.base.json'
        self.local_filename = cur + '/../config/config.local.json'
        self.base = None
        self.local = '{}'
        self.reset()

    def reset(self):

        with open(self.filename, 'r') as fd:
            self.base = fd.read()

        if os.path.isfile(self.local_filename):
            with open(self.local_filename, 'r') as fd:
                self.local = fd.read()
        else:
            self.local = '{}'
        b = json.loads(self.base)
        l = json.loads(self.local)
        self.config = {
            key: value for (key, value) in (b.items() + l.items())
        }


config = Config().config
