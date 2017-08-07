#!/usr/bin/env python
import json
import threading
import time
from datetime import datetime

import pandas as pd
import redis
from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource

import util
from train import TrainCenter
from util.config import config
from util.log import log
from util.singleton import SingletonMixin

app = Flask(__name__)
CORS(app)
api = Api(app)

LOOP_INTERVAL_SEC = 2


class LogCollector(SingletonMixin):
    def __init__(self):
        super(LogCollector, self).__init__()
        info = config['pubsub']
        self.host = info[0]
        self.port = int(info[1])
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.p = self.r.pubsub()
        self.p.psubscribe('*')

    def collect(self):
        # TODO: get message from pub/sub server
        while True:
            raw_message = self.p.get_message()
            if not raw_message:
                break
            # log.warn('raw_message: %s' % raw_message)
            self._handle(raw_message)

    def _handle(self, raw_message):
        data = util.extract_json2(raw_message)
        if data is None or 'key' not in data:
            return

        key = data['key']
        # if key == 'START_ML_WORKER':
        #     worker_id = data['worker_id']
        #     Center().connect_ml_worker(worker_id)
        # elif key == 'START_ML_TRAIN':
        #     worker_id = data['worker_id']
        #     code_name = data['code_name']
        #     train_id = data['train_id']
        #     Center().start_train(worker_id, code_name, train_id)
        # elif key == 'FINISH_ML_TRAIN':
        #     worker_id = data['worker_id']
        #     code_name = data['code_name']
        #     train_id = data['train_id']
        #     Center().finish_train(worker_id, code_name, train_id)
        # elif key == 'REGISTER_TRAIN':
        #     Center().register_train(data)
        if key == 'UPDATE_PS':
            Center().update_ps(data)
        elif key == 'UPDATE_PS_DETAIL':
            Center().update_ps_detail(data)
        elif key == 'MEASUREMENT':
            Center().update_measurement(data)
        elif key == 'TRAIN_NOW':
            TrainCenter().train_now(data)
        elif key == 'set_variable':
            pass
        elif key == 'average':
            pass
        else:
            log.error('IMPME: %s' % key)


def start_sub_log_and_command():
    log.warn('START THREAD: admin / subscribe log and command')
    while True:
        LogCollector().collect()
        # time.sleep(0.001)
        Center().loop_count += 1
        time.sleep(LOOP_INTERVAL_SEC)


def start_train_center():
    log.warn('START THREAD: admin / train-center')
    while True:
        TrainCenter().update()
        time.sleep(LOOP_INTERVAL_SEC)


class MeasureContainer(object):
    def __init__(self):
        self.train_ids = set([])
        self.group_ids = set([])
        self.ps_dict = {}  # group_id: { worker_id: data }
        self.controller_dict = {}  # group_id: data

        self.df = pd.DataFrame(
            columns=[
                'train_id', 'group_id', 'worker_id', 'worker_count',
                'load_rtt', 'save_rtt', 'controller_rtt',
                'data_size', 'success'
            ],
            dtype='float')

    def _to_list(self, data):
        load_end = int(data['num_01_after_load_variables'])
        load_start = int(data['num_01_before_load_variables'])
        load_rtt = load_end - load_start

        save_end = int(data['num_02_after_save_variables'])
        save_start = int(data['num_02_before_save_variables'])
        save_rtt = save_end - save_start
        controller_rtt = int(data['num_05_after_pub_on_controller']) - int(
            data['num_03_after_get_on_controller'])
        success = 1
        return [
            data['train_id'],
            data['group_id'],
            data['worker_id'],
            data['worker_count'],
            load_rtt,
            save_rtt,
            controller_rtt,
            data['data_size'],
            success,
        ]

    def update(self, data):
        node_type = data['node_type']
        group_id = data['group_id']
        if node_type == 'ps':
            self._update_ps(group_id, data)
        else:
            self._update_controller(group_id, data)

    def get_stat_of_train(self):
        d = json.loads(self.get_train_stat_json())
        d2 = json.loads(
            self.df.groupby(['train_id'])['group_id'].count().to_json(
                orient='index'))
        for k, v in d.iteritems():
            v['count'] = d2[k]
        return d

    def get_train_stat_json(self):
        df = self.df
        return df.groupby(['train_id']).mean().to_json(orient='index')

    def get_group_stat_json(self):
        df = self.df
        return df.groupby(['group_id']).mean().to_json(orient='index')

    def _update_ps(self, group_id, raw):
        worker_id = raw['worker_id']
        raw['merged'] = False

        if group_id in self.controller_dict:
            controller_data = self.controller_dict[group_id]
            merged_data = self._merge(raw, controller_data)
            self._append(merged_data)
        else:
            d = self.ps_dict
            if group_id not in d:
                d[group_id] = {}
            group = d[group_id]
            group[worker_id] = raw

    def _merge(self, ps_data, controller_data):
        return util.merge_two_dicts(ps_data, controller_data)

    def _append(self, merged_data):
        l = self._to_list(merged_data)
        df = self.df
        df.loc[len(df)] = l

    def _update_controller(self, group_id, data):
        self.controller_dict[group_id] = data

        psd = self.ps_dict
        if group_id in psd:
            group_dict = psd[group_id]
            for ps in group_dict.itervalues():
                merged_data = self._merge(ps, data)
                self._append(merged_data)
            del psd[group_id]


class Center(SingletonMixin):
    def __init__(self):
        super(Center, self).__init__()
        self.loop_count = 0
        self.ml_worker = {}
        self.ps = {}
        self.ps_detail = []
        self.measure_container = MeasureContainer()

    # def start_train(self, worker_id, code_name, train_id):
    #     msg = 'Start (%s:%s)' % (code_name, train_id)
    #     w = self.ml_worker[worker_id]
    #     w['description'] = msg

    # def finish_train(self, worker_id, code_name, train_id):
    #     msg = 'Finish (%s:%s)' % (code_name, train_id)
    #     w = self.ml_worker[worker_id]
    #     w['description'] = msg

    # def connect_ml_worker(self, worker_id):
    #     self.ml_worker[worker_id] = {
    #         'worker_id': worker_id,
    #         'description': 'connected',
    #     }

    def update_ps_detail(self, data):
        group_id = data['group_id']
        msg = data['msg']
        worker_id = data['worker_id']
        now = datetime.now()
        now_str = now.strftime('%H:%M:%S.%f')
        self.ps_detail.append({
            'group_id': group_id,
            'worker_id': worker_id,
            'msg': msg,
            'time': now_str})

    def update_ps(self, data):
        v = data['value']
        group_id = v['group_id']
        self.ps[group_id] = v

    def update_measurement(self, data):
        self.measure_container.update(data)

    def get_data(self):
        return {
            'loop_count': self.loop_count,
            'train': TrainCenter().get_info(),
            'worker': [v for k, v in self.ml_worker.iteritems()],
            'ps': [v for k, v in self.ps.iteritems()],
            'ps_detail': self.ps_detail,
            'stat_of_group': json.loads(
                self.measure_container.get_group_stat_json()),
            'stat_of_train': self.measure_container.get_stat_of_train(),
        }


class DefaultRoute(Resource):
    def get(self):
        return Center().get_data()


api.add_resource(DefaultRoute, '/')


def run():
    t1 = threading.Thread(target=start_sub_log_and_command)
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=start_train_center)
    t2.daemon = True
    t2.start()

    admin_config = config['admin']
    app.run(port=int(admin_config['port']), debug=False)
    # app.run(port=int(admin_config['port']), debug=True)


if __name__ == '__main__':
    run()
