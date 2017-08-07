#!/usr/bin/env python

import argparse
import json
import subprocess
import time

import redis

import ps.sample_freeze_restore as sfr
import util
from train_settings import train_code_name, train_worker_count
from util.config import config
from util.log import log
from util.singleton import SingletonMixin


class CmdHandler(SingletonMixin):
    def __init__(self):
        super(CmdHandler, self).__init__()

    def kill(self):
        # kill $(ps aux | grep ml_worker | grep - v grep | awk '{print $2}')
        # subprocess.Popen(['pkill', '-f', 'python'])
        subprocess.Popen(['pkill', '-f', 'train'])
        subprocess.Popen(['pkill', '-f', 'ml_worker'])
        # subprocess.Popen(['pkill', '-f', 'admin'])
        subprocess.Popen(['pkill', '-f', 'ps_controller'])

    def admin(self):
        subprocess.Popen(['pkill', '-f', 'admin'])
        time.sleep(0.3)
        subprocess.Popen(['python', 'admin.py'])

    def ps_controller(self):
        subprocess.Popen(['pkill', '-f', 'ps_controller'])
        time.sleep(0.5)
        subprocess.Popen(['python', 'ps_controller.py'])

    def ml_worker(self):
        subprocess.Popen(['pkill', '-f', 'ml_worker'])
        time.sleep(0.5)
        for i in range(0, train_worker_count):
            log.info('ml_worker: %d start' % i)
            subprocess.Popen(['python', 'ml_worker.py'])

    def train(self):
        info = config['pubsub']
        host = info[0]
        port = int(info[1])
        r = redis.StrictRedis(host=host, port=port, db=0)

        key = 'TRAIN_NOW'
        train_id = 't%s' % util.hhmmss()
        code_name = train_code_name

        message = json.dumps({
            'key': key,
            'train_id': train_id,
            'worker_count': train_worker_count,
            'code_name': code_name})
        r.publish('admin_command', message)

    def pub(self):
        info = config['pubsub']
        host = info[0]
        port = int(info[1])
        r = redis.StrictRedis(host=host, port=port, db=0)
        message = json.dumps(
            {'worker_id': 'console', 'train_id': '1', 'iteration_id': '1'})
        r.publish('ps', message)


parser = argparse.ArgumentParser(description='skt parameter server')
parser.add_argument('command', choices=[
    'k', 'kill',
    'a', 'admin',
    'p', 'ps_controller',
    'm', 'ml_worker',
    't', 'train',
    'b', 'bang',
    'pub',
    'sample_freeze_restore',
])
args = parser.parse_args()
c = args.command

if c == 'k' or c == 'kill':
    CmdHandler().kill()
elif c == 'a' or c == 'admin':
    CmdHandler().admin()
elif c == 'p' or c == 'ps_controller':
    CmdHandler().ps_controller()
elif c == 'm' or c == 'ml_worker':
    # CmdHandler().kill()
    # time.sleep(0.5)
    CmdHandler().ml_worker()
elif c == 't' or c == 'train':
    CmdHandler().train()
elif c == 'b' or c == 'bang':
    CmdHandler().kill()
    time.sleep(0.5)
    # CmdHandler().admin()
    CmdHandler().ps_controller()
    CmdHandler().ml_worker()
    CmdHandler().train()
elif c == 'pub':
    CmdHandler().pub()
elif c == 'sample_freeze_restore':
    sfr.run()
else:
    log.warn('%s is not valid command' % c)
