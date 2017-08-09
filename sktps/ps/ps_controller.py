from __future__ import print_function

import json
import time

import redis
import tensorflow as tf
from rediscluster import StrictRedisCluster
from tensorflow.python.framework import graph_util

import util
from measure import Measure, MeasureHelper, SimpleMeasurement
from util.config import config
from util.log import log
from util.pony import Pony

channel = 'ps'  # change it later


class ParameterServerController(object):
    def __init__(self):
        info = config['pubsub']
        self.host = info[0]
        self.port = int(info[1])

        self.channel = channel

        self.r = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.p = self.r.pubsub()
        self.p.subscribe(self.channel)

        rc_address = util.get_redis_cluster_address_randomly()
        startup_nodes = [{'host': rc_address[0], 'port': rc_address[1]}]
        self.rc = StrictRedisCluster(
            startup_nodes=startup_nodes, decode_responses=False)
        # group_id : { train_id, total, variables, keys: [key, ] }
        self.progress_dict = {}
        self.measure_helper = MeasureHelper()

    def _handle(self, message):
        if 'key' not in message:
            return
        if message['key'] != 'set_variable':
            return
        group_id = message['group_id']
        train_id = message['train_id']
        worker_count = message['worker_count']
        variables = message['variables']
        pd = self.progress_dict
        if group_id not in pd:
            pd[group_id] = {
                'group_id': group_id,
                'total': int(worker_count),
                'train_id': train_id,
                'variables': variables,
                'keys': []
            }

        item = pd[group_id]
        item['total'] = int(worker_count)
        item['worker_num'] = int(worker_count)
        keys = item['keys']
        tid = message['transaction_id']
        if tid not in keys:
            keys.append(tid)
        else:
            log.warn('Same transaction id: %s' % tid)
        item['progress'] = len(keys)
        Pony().log({
            'key': 'UPDATE_PS',
            'value': pd[group_id],
        })

        if len(keys) >= item['total']:
            # TODO: calculate and put average into rc
            m = Measure().create_measurement(
                'controller', train_id, group_id)
            self.measure_helper.num_03_after_get_on_controller(m, len(keys))
            self._calculate_average_and_put(group_id, item, m)

            message = json.dumps({
                'key': 'average',
                'group_id': group_id,
                'train_id': item['train_id'],
            })
            self.r.publish(channel=channel, message=message)
            self.measure_helper.num_05_after_pub_on_controller(m)
            m['key'] = 'MEASUREMENT'
            Pony().log(m)
        else:
            log.debug('Wait more data')

    def _calculate_average_and_put(self, group_id, item, m):
        keys = item['keys']
        tf.reset_default_graph()
        sess = tf.Session()
        new_vars = []

        m_cal_and_put = SimpleMeasurement('cal_and_put', m)

        m_init = SimpleMeasurement('init', m)
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        m_init.end_measure()

        for v in item['variables']:
            count = 0
            name = 'average_%s' % v
            ts = []
            for key in keys:
                raw = self.rc.get(key)
                # TODO: check raw is not None
                util.restore_graph(key, raw)
                g = sess.graph
                t = g.get_tensor_by_name('%s/%s:0' % (key, v))
                ts.append(t)
                count += 1

            m_cal = SimpleMeasurement('cal', m)
            avg = tf.foldl(tf.add, ts) / count
            new_var = tf.Variable(avg, name=name)
            sess.run(new_var.initializer)
            sess.run(new_var)
            new_vars.append(name)
            m_cal.end_measure()

        g = sess.graph
        g_def = g.as_graph_def()
        constants = graph_util.convert_variables_to_constants(
            sess, g_def, new_vars)
        s = constants.SerializeToString()
        self.rc.set(group_id, s)
        sess.close()

        m_cal_and_put.end_measure()

    def run(self):
        log.warn('START PROCESS: ParameterServerController')

        while True:
            raw_message = self.p.get_message()
            message = util.extract_json(raw_message)
            if not message:
                time.sleep(0.001)
            else:
                self._handle(message)
