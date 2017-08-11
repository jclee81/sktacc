from __future__ import print_function

import threading

import redis
from rq import Connection, Queue

from measure import MeasureHelper
from task import tf_average
from util.config import config
from util.log import log

channel = 'ps'  # change it later


class ThreadSafeQueue:
    def __init__(self):
        self.lock = threading.Lock()
        self.items = []

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        with self.lock:
            self.items.insert(0, item)

    def dequeue(self):
        v = None
        with self.lock:
            v = self.items.pop()
        return v

    def size(self):
        s = 0
        with self.lock:
            s = len(self.items)
        return s


class Group(object):
    def __init__(self, group_id, train_id, parallel_count, variables, rqq):
        self.group_id = group_id
        self.train_id = train_id
        self.parallel_count = parallel_count
        self.variables = variables
        self.rqq = rqq
        self.messages = ThreadSafeQueue()
        # self.todo = []
        self.ing = {}
        self.done = []

    def add_message(self, task):
        self.messages.enqueue(task)

    def _message_to_done(self):
        while self.messages.size() > 0:
            t = self.messages.dequeue()
            self.done.append(t)

    def _get_final_task(self):
        for task in self.done:
            total_sum = task[1]
            if total_sum == self.parallel_count:
                return task
        return None

    def _create_new_task(self):
        while len(self.done) >= 2:
            data1 = self.done.pop(0)
            data2 = self.done.pop(0)
            result_key = '0' + data1[0]
            result_count = int(data1[1]) + int(data2[1])
            if result_count == self.parallel_count:
                result_key = self.group_id
            task_input = {
                'data1': {'key': data1[0], 'count': int(data1[1]), },
                'data2': {'key': data2[0], 'count': int(data2[1]), },
                'result_key': result_key,
                'result_count': int(data1[1]) + int(data2[1])
            }
            task = self.rqq.enqueue(tf_average, task_input)
            self.ing[result_key] = task

    def _ing_to_done(self):
        done_key_list = []
        for key, task in self.ing.iteritems():
            if task.return_value is not None:
                done_key_list.append(key)
                self.done.append(task.return_value)
        for key in done_key_list:
            del self.ing[key]

    def update(self):
        self._message_to_done()
        final_task = self._get_final_task()
        if final_task:
            return True
        self._create_new_task()
        self._ing_to_done()
        return False


class CalculatorMany(object):
    def __init__(self):
        self.measure_helper = MeasureHelper()
        self.r = None
        self.p = None
        self.rc = None
        self.group_dict = {}  # group_id : Group object

        info = config['pubsub']
        host = info[0]
        port = int(info[1])
        self.raw_conn = redis.StrictRedis(host=host, port=port, db=0)
        self.conn = Connection(self.raw_conn)

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
            rqq = Queue(connection=self.raw_conn)
            group = Group(group_id, train_id, parallel_count, variables, rqq)
            group_dict[group_id] = group
        group = group_dict[group_id]
        cur_sum_count = 1
        group.add_message((tid, cur_sum_count))

    def loop(self):
        finish_key_list = []
        for key in self.group_dict:
            v = self.group_dict[key]
            finished = v.update()
            if finished:
                finish_key_list.append(key)
        for key in finish_key_list:
            del self.group_dict[key]
