from __future__ import print_function

import json

import tensorflow as tf
from tensorflow.python.framework import graph_util

import util
from measure import Measure, MeasureHelper, SimpleMeasurement
from util.log import log
from util.pony import Pony

channel = 'ps'  # change it later


class CalculatorMany(object):
    def __init__(self):
        self.progress_dict = {}
        self.measure_helper = MeasureHelper()
        self.r = None
        self.p = None
        self.rc = None

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
        # group_id = message['group_id']
        # train_id = message['train_id']
        # parallel_count = message['parallel_count']
        # variables = message['variables']
        # pd = self.progress_dict
