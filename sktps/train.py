import uuid

import redis
from rq import Connection, Queue

import ml.cnn_mnist
import ml.code1 as code1
import ml.code2 as code2
import ml.mnist_softmax as mnist_softmax
import sandbox.fib
from util.config import config
from util.log import log
from util.singleton import SingletonMixin

train_actions = {
    'fib': sandbox.fib,
    'code1': code1,
    'code2': code2,
    'mnist_softmax': mnist_softmax,
    'cnn_mnist': ml.cnn_mnist
}


class TrainSession(object):
    def __init__(self, data, conn):
        self.data = data
        self.worker_count = int(data['worker_count'])
        self.code_name = self.data['code_name']
        self.train_id = self.data['train_id']
        self.cur_iter_id = 0
        self.q = Queue(connection=conn)
        self.tasks = []
        self.enqueue_task()

    def enqueue_task(self):
        if len(self.tasks) > 0:
            log.error('tasks not empty')
            return
        code_name = self.code_name
        self.data['iteration_id'] = self.cur_iter_id
        index = 0
        while index < self.worker_count:
            worker_id = str(uuid.uuid4())[:8]
            index += 1
            task = self.q.enqueue(
                train_actions[code_name].run, (
                    self.data, worker_id, self.cur_iter_id))
            self.tasks.append(task)

    def check(self):
        for task in self.tasks:
            if task.return_value is None:
                log.info('%s %d ing' % (self.code_name, self.cur_iter_id))
                return False
        log.info('Train(%s, %s) %d complete' % (
            self.train_id, self.code_name, self.cur_iter_id))
        self.tasks = []
        self.cur_iter_id += 1
        self.enqueue_task()
        return True


class TrainCenter(SingletonMixin):
    def __init__(self):
        super(TrainCenter, self).__init__()

        info = config['pubsub']
        self.host = info[0]
        self.port = int(info[1])
        self.raw_conn = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.conn = Connection(self.raw_conn)

        self.train_sessions = []

    def get_info(self):
        ret = []
        for session in self.train_sessions:
            ret.append({
                'train_id': session.train_id,
                'code_name': session.code_name,
                'worker_num': session.worker_count,
                'status': ''
            })
        return ret

    def update(self):
        for session in self.train_sessions:
            session.check()

    def train_now(self, data):
        log.info('train_now: %s', data)
        item = TrainSession(data, self.raw_conn)
        self.train_sessions.append(item)
