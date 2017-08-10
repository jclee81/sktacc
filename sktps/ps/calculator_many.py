from __future__ import print_function

import time
import json

import tensorflow as tf
from tensorflow.python.framework import graph_util

import util
from measure import Measure, MeasureHelper, SimpleMeasurement
from util.log import log
from util.pony import Pony

channel = 'ps'  # change it later


# raw_messages --> todo_tasks --> ing_tasks --> done_tasks


class Group(object):
    def __init__(self, group_id, train_id, parallel_count, variables):
        self.group_id = group_id
        self.train_id = train_id
        self.parallel_count = parallel_count
        self.variables = variables
        self.messages = []
        self.todo = []
        self.ing = []
        self.done = []

    def add_to_done(self, task):
        # TODO: use lock
        self.done.append(task)

    def update(self):
        # TODO: done --> todo --> ing
        return False


class CalculatorMany(object):
    def __init__(self):
        self.measure_helper = MeasureHelper()
        self.r = None
        self.p = None
        self.rc = None
        self.group_dict = {}  # group_id : Group object

    def set_from_controller(self, controller):
        log.info('CalculatorMany')
        c = controller
        self.r = c.r
        self.p = c.p
        self.rc = c.rc

    def handle(self, message):
        if 'key' not in message:
            return
        if message['key'] != 'set_variable':
            return

        group_id = message['group_id']
        train_id = message['train_id']
        parallel_count = message['parallel_count']
        variables = message['variables']
        tid = message['transaction_id']

        group_dict = self.group_dict
        if group_id not in group_dict:
            group = Group(group_id, train_id, parallel_count, variables)
            group_dict[group_id] = group
        group = group_dict[group_id]
        cur_sum_count = 1
        group.add_to_done((tid, cur_sum_count))

    def loop(self):
        for k in self.group_dict:
            v = self.group_dict[k]
            finished = v.update()
            if finished:
                del self.group_dict[k]
                break
