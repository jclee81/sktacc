# -*- coding: utf-8 -*-

import redis

from config import config
from singleton import SingletonMixin


class Pony(SingletonMixin):
    def __init__(self):
        super(Pony, self).__init__()
        info = config["pubsub"]
        self.host = info[0]
        self.port = int(info[1])
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=0)

    def log(self, message):
        self.r.publish(channel='log', message=message)
