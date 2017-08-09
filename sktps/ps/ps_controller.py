from __future__ import print_function

import time

import redis
from rediscluster import StrictRedisCluster

import util
from util.config import config
from util.log import log

channel = 'ps'  # change it later


class ParameterServerController(object):
    def __init__(self, calculator):
        self.calculator = calculator
        info = config['pubsub']
        self.host = info[0]
        self.port = int(info[1])
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.p = self.r.pubsub()
        self.p.subscribe(channel)
        rc_address = util.get_redis_cluster_address_randomly()
        startup_nodes = [{'host': rc_address[0], 'port': rc_address[1]}]
        self.rc = StrictRedisCluster(
            startup_nodes=startup_nodes, decode_responses=False)
        calculator.set_from_controller(self)

    def run(self):
        log.warn('START PROCESS: ParameterServerController')

        while True:
            raw_message = self.p.get_message()
            message = util.extract_json(raw_message)
            if not message:
                time.sleep(0.001)
            else:
                self.calculator.handle(message)
