from __future__ import print_function

import time

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

import util
import ps
from util.log import log


class MnistInput(object):
    def __init__(self, raw_data):
        message = raw_data[0]
        worker_id = raw_data[1]
        iteration_id = raw_data[2]
        self.worker_id = worker_id
        self.train_id = message['train_id']
        self.code_name = message['code_name']
        self.worker_count = message['worker_count']
        self.iteration_id = int(iteration_id)
        self.logs_path = \
            '/tmp/tensorflow_logs/%s/%s/%s/%s' % (
                util.yymmdd(), self.code_name, self.worker_count,
                self.worker_id)


def run(raw_data):
    mnist_input = MnistInput(raw_data)
    return _run(mnist_input)


def _run(mnist_input):
    log.info('Start mnist')
    mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
    mi = mnist_input
    code_name = mi.code_name
    log.info('Start mnist: %s' % code_name)
    worker_id = mi.worker_id
    train_id = mi.train_id
    worker_count = mi.worker_count
    iteration_id = mi.iteration_id
    logs_path = mi.logs_path
    learning_rate = 0.01
    batch_size = 100
    display_step = 1
    x = tf.placeholder(tf.float32, [None, 784], name='InputData')
    y = tf.placeholder(tf.float32, [None, 10], name='LabelData')
    W = tf.Variable(tf.zeros([784, 10]), name='Weights')
    b = tf.Variable(tf.zeros([10]), name='Bias')
    with tf.name_scope('Model'):
        pred = tf.nn.softmax(tf.matmul(x, W) + b)  # Softmax
    with tf.name_scope('Loss'):
        cost = tf.reduce_mean(
            -tf.reduce_sum(y * tf.log(pred), reduction_indices=1))
    with tf.name_scope('SGD'):
        optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(
            cost)
    with tf.name_scope('Accuracy'):
        acc = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
        acc = tf.reduce_mean(tf.cast(acc, tf.float32))

    init = tf.global_variables_initializer()
    tf.summary.scalar("loss", cost)
    tf.summary.scalar("accuracy", acc)
    merged_summary_op = tf.summary.merge_all()
    with tf.Session() as sess:
        sess.run(init)
        summary_writer = tf.summary.FileWriter(logs_path,
                                               graph=tf.get_default_graph())

        ps_conn = ps.ParameterServer(
            sess,
            train_id,
            worker_id,
            iteration_id,
            [W, b],
            ps.DefaultAgingPolicy(),
            worker_count)

        while True:
            ########
            if ps_conn.load_variables():
                break
            time.sleep(0.1)

        cost_sum = 0.
        batch_count = 0

        total_batch = int(mnist.train.num_examples / batch_size)

        # Loop over all batches
        for i in range(total_batch):
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            _, c, summary = sess.run([optimizer, cost, merged_summary_op],
                                     feed_dict={x: batch_xs, y: batch_ys})
            summary_writer.add_summary(summary, total_batch + i)
            cost_sum += c
            batch_count += 1

        avg_cost = float(cost_sum) / batch_count

        ps_conn.save_variables()

        # print(
        #     "Run the command line:\n --> tensorboard "
        #     "--logdir=/tmp/tensorflow_logs \nThen open http://0.0.0.0:6006/ "
        #     "into your web browser")

    log.info('Finish mnist')
    return True


if __name__ == '__main__':
    run()
