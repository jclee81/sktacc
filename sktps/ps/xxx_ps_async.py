from __future__ import print_function

import json
import time

import redis
import tensorflow as tf
from rediscluster import StrictRedisCluster
from tensorflow.core.framework import variable_pb2

import util
from util.config import config
from util.log import log

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
            'parallel_count': -1,
        }

        self._log('created')

    def _log(self, msg):
        log.debug('[%s:%s] %s' % (self.worker_id, self.iteration_id, msg))

    def _set_variable_and_publish(self, iteration_id, variable, key):
        v = variable
        s = v.to_proto().SerializeToString()
        # h = ':'.join('{:02x}'.format(ord(c)) for c in s)

        parallel_count = self.infra_info['parallel_count']

        self.rc.set(key, s)

        message = json.dumps({
            'worker_id': self.worker_id,
            'train_id': self.train_id,
            'iteration_id': iteration_id,
            'parallel_count': parallel_count
        })
        self.r.publish(channel=channel, message=message)
        self._log('pub %s' % iteration_id)

        return v, s

    def _check_message(self, message):
        my_iteration_id = self.iteration_id
        worker_id = message['worker_id']
        iteration_id = message['iteration_id']
        if self.worker_id != worker_id:
            if my_iteration_id == iteration_id:
                return 'cur'
            elif my_iteration_id < iteration_id:
                return 'next'
        return 'prev'

    def _wait_until_time_out(self, time_out_sec):
        self._log('_wait_until')
        p = self.p
        start_time = time.time()

        for message in self.future_list:
            prev_cur_next = self._check_message(message)
            if prev_cur_next == 'cur':
                return True

        while True:
            raw_message = p.get_message()
            message = util.extract_json(raw_message)
            if not message:
                time.sleep(0.001)
            else:
                prev_cur_next = self._check_message(message)
                if prev_cur_next == 'next':
                    self._log('future append %s' % message['iteration_id'])
                    self.future_list.append(message)
                elif prev_cur_next == 'cur':
                    self.future_list.append(message)
                    return True
                else:
                    time.sleep(0.001)

            diff = time.time() - start_time
            if diff > time_out_sec:
                return False

    def _collect_message(self):
        messages = []
        messages.extend(self.future_list)
        self.future_list = []
        while True:
            raw_message = self.p.get_message()
            message = util.extract_json(raw_message)
            if message:
                messages.append(message)
            else:
                break
        return messages

    def _calculate_average(self, my_v, messages):
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            for message in messages:
                prev_cur_next = self._check_message(message)
                if prev_cur_next == 'next':
                    self._log('future append %s' % message['iteration_id'])
                    self.future_list.append(message)
                elif prev_cur_next == 'cur':
                    worker_id = message['worker_id']
                    key = self.get_key(
                        self.train_id, worker_id, self.iteration_id)
                    your_v_raw = self.rc.get(key)
                    var_def = variable_pb2.VariableDef()
                    var_def.ParseFromString(your_v_raw)

                    # TODO
                    v2 = tf.Variable(variable_def=var_def)
                    result = tf.add(my_v, v2) / 2.0
                    print('!!!', sess.run(result))
                    return result

        return my_v

    def get_key(self, train_id, worker_id, iteration_id):
        return '%s_%s_%s' % (worker_id, train_id, iteration_id)

    def set_infra_info(self, infra_info):
        self.infra_info = infra_info

    def change_var_as_average(self, iteration_id, variable, time_out_sec=1):
        self.iteration_id = iteration_id

        train_id = self.train_id
        worker_id = self.worker_id

        key = self.get_key(train_id, worker_id, iteration_id)

        # 1. set variable to redis cluster
        my_v, s = self._set_variable_and_publish(iteration_id, variable, key)

        # 2. get first message until time out
        success = self._wait_until_time_out(time_out_sec)
        if not success:
            self._log('Timeout!')
            return my_v
        else:
            self._log('Have data!')

        # 3. collect messages
        messages = self._collect_message()

        # 4. calculate average
        avg_v = self._calculate_average(my_v, messages)

        return avg_v
