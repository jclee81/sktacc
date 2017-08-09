from __future__ import print_function

import json
import time

import redis
from rediscluster import StrictRedisCluster
from tensorflow.python.framework import graph_util

import util
from measure import Measure, MeasureHelper
from util.config import config
from util.log import log
from util.pony import Pony

channel = 'ps'  # change it later


class ParameterServer(object):
    def __init__(self, train_id, worker_id, parallel_count=-1):
        self.train_id = train_id
        self.worker_id = worker_id
        self.iteration_id = -1

        info = config['pubsub']
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
        self.infra_info = {
            'parallel_count': parallel_count
        }
        self.measure_helper = MeasureHelper()

    def change_var_as_average(self, sess, iteration_id, variables,
                              time_out_sec=1):

        self.iteration_id = iteration_id
        train_id = self.train_id
        worker_id = self.worker_id

        group_id = self.get_group_id(train_id, iteration_id)

        m = Measure().create_measurement('ps', train_id, group_id, worker_id)

        self.measure_helper.num_00_start_call_func(m)

        transaction_id = self.get_transaction_id(
            train_id, worker_id, iteration_id)

        # 1. set variable to redis cluster
        data_size = self._set_variable_and_publish(
            sess, iteration_id, variables, transaction_id, group_id)

        self.measure_helper.num_01_after_pub_on_worker(m, data_size)

        # 2. wait my group_id average
        success = self._wait_average(sess, group_id, variables, time_out_sec, m)

        self.measure_helper.num_09_finish_call_func(m, success)
        self.pony_measurement(m)

    def _log(self, msg):
        log.debug('[%s:%s] %s' % (self.worker_id, self.iteration_id, msg))

    def pony(self, msg):
        group_id = self.get_group_id(self.train_id, self.iteration_id)
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

    def _set_variable_and_publish(self, sess, iteration_id, variables,
                                  transaction_id, group_id):
        # v = variable
        # s = v.to_proto().SerializeToString()
        # h = ':'.join('{:02x}'.format(ord(c)) for c in s)

        variable_names = [var.op.name for var in variables]

        g = sess.graph
        g_def = g.as_graph_def()
        constants = graph_util.convert_variables_to_constants(
            sess, g_def, variable_names)
        s = constants.SerializeToString()

        parallel_count = self.infra_info['parallel_count']
        self.rc.set(transaction_id, s)
        message = json.dumps({
            'key': 'set_variable',
            'transaction_id': transaction_id,
            'group_id': group_id,
            'variables': variable_names,
            'worker_id': self.worker_id,
            'train_id': self.train_id,
            'iteration_id': iteration_id,
            'parallel_count': parallel_count
        })
        self.r.publish(channel=channel, message=message)
        self._log('pub %s' % iteration_id)
        return len(s)

    def get_transaction_id(self, train_id, worker_id, iteration_id):
        return '%s-%s-%09d' % (worker_id, train_id, iteration_id)

    def get_group_id(self, train_id, iteration_id):
        return '%s-%09d' % (train_id, int(iteration_id))

    def set_infra_info(self, infra_info):
        self.infra_info = infra_info

    def _check_message(self, message, group_id):
        key = message['key']
        if key != 'average':
            return 'prev'
        if 'train_id' not in message:
            return 'prev'
        if message['train_id'] != self.train_id:
            return 'prev'
        if group_id == message['group_id']:
            return 'cur'
        my_iteration_id = self.iteration_id
        if int(message['iteration_id']) > int(my_iteration_id):
            return 'next'
        return 'prev'

    def _restore_variable_from_rc(self, sess, group_id, variables, m):
        self.measure_helper.num_06_after_sub_on_worker(m)

        g = sess.graph
        raw = self.rc.get(group_id)

        self.measure_helper.num_07_after_get_on_worker(m)

        ####
        util.restore_graph(group_id, raw)
        ####

        for v in variables:
            src_key = '%s/average_%s:0' % (group_id, v.op.name)
            src = g.get_tensor_by_name(src_key)
            sess.run(v.assign(src))

        self.measure_helper.num_08_after_assign_on_worker(m)

    def _wait_average(self, sess, group_id, variables, time_out_sec, m):
        p = self.p
        start_time = time.time()

        for message in self.future_list:
            prev_cur_next = self._check_message(message, group_id)
            if prev_cur_next == 'cur':
                self._restore_variable_from_rc(sess, group_id, variables, m)
                return True

        while True:
            raw_message = p.get_message()
            message = util.extract_json(raw_message)
            if not message:
                time.sleep(0.001)
            else:
                prev_cur_next = self._check_message(message, group_id)
                if prev_cur_next == 'next':
                    self._log('future append %s' % message['iteration_id'])
                    self.future_list.append(message)
                elif prev_cur_next == 'cur':
                    self._restore_variable_from_rc(sess, group_id, variables, m)
                    return True
                else:
                    time.sleep(0.001)

            diff = time.time() - start_time
            if diff > time_out_sec:
                log.error('Timeout!')
                return False


