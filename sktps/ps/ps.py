from __future__ import print_function

import json

import redis
from rediscluster import StrictRedisCluster
from tensorflow.python.framework import graph_util

import util
from measure import MeasureHelper
from util.config import config
from util.log import log
from util.pony import Pony

channel = 'ps'  # change it later


class ParameterServer(object):
    def __init__(self, sess, train_id, worker_id, iteration_id, variables,
                 worker_count=-1):
        log.debug('ParameterServer v0.0.2')
        self.sess = sess
        self.train_id = train_id
        self.worker_id = worker_id
        self.iteration_id = int(iteration_id)
        self.prev_iteration_id = iteration_id - 1
        self.variables = variables

        info = config["pubsub"]
        self.host = info[0]
        self.port = int(info[1])

        self.channel = channel
        # self.channel = train_id  # later

        self.r = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.p = self.r.pubsub()
        self.p.subscribe(self.channel)

        rc_address = util.get_redis_cluster_address_randomly()
        startup_nodes = [{'host': rc_address[0], 'port': rc_address[1]}]
        self.rc = StrictRedisCluster(
            startup_nodes=startup_nodes, decode_responses=False)

        self.future_list = []
        self.infra_info = {'worker_count': worker_count}
        self.measure_helper = MeasureHelper()

    def load_variables(self, mode=None):
        sess = self.sess
        if self.prev_iteration_id < 0:
            return True
        group_id = util.get_group_id(self.train_id, self.prev_iteration_id)
        g = sess.graph
        raw = self.rc.get(group_id)
        if raw is None:
            return False
        ####
        util.restore_graph(group_id, raw)
        ####
        for v in self.variables:
            src_key = '%s/average_%s:0' % (group_id, v.op.name)
            src = g.get_tensor_by_name(src_key)
            sess.run(v.assign(src))
        return True

    def save_variables(self):
        sess = self.sess
        group_id = util.get_group_id(self.train_id, self.iteration_id)
        transaction_id = util.get_transaction_id(
            self.train_id, self.worker_id, self.iteration_id)
        data_size = self._set_variable_and_publish(
            sess,
            self.iteration_id,
            transaction_id,
            group_id)

    def _set_variable_and_publish(self, sess, iteration_id, transaction_id,
                                  group_id):
        # v = variable
        # s = v.to_proto().SerializeToString()
        # h = ":".join("{:02x}".format(ord(c)) for c in s)

        variable_names = [var.op.name for var in self.variables]

        g = sess.graph
        g_def = g.as_graph_def()
        constants = graph_util.convert_variables_to_constants(
            sess, g_def, variable_names)
        s = constants.SerializeToString()

        worker_count = self.infra_info['worker_count']
        self.rc.set(transaction_id, s)
        message = json.dumps({
            'key': 'set_variable',
            'transaction_id': transaction_id,
            'group_id': group_id,
            'variables': variable_names,
            'worker_id': self.worker_id,
            'train_id': self.train_id,
            'iteration_id': iteration_id,
            'worker_count': worker_count
        })
        self.r.publish(channel=channel, message=message)
        log.debug('pub %s' % iteration_id)
        return len(s)

    def pony(self, msg):
        group_id = util.get_group_id(self.train_id, self.iteration_id)
        worker_id = self.worker_id
        Pony().log({
            'key': 'UPDATE_PS_DETAIL',
            'group_id': group_id,
            'worker_id': worker_id,
            'msg': msg,
        })

    def pony_measurement(self, measurement):
        measurement['key'] = 'MEASUREMENT'
        Pony().log(measurement)
