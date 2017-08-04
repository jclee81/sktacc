'''
Graph and Loss visualization using Tensorboard.
This example is using the MNIST database of handwritten digits
(http://yann.lecun.com/exdb/mnist/)

Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/
'''

from __future__ import print_function

import tensorflow as tf
# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data

import util
from ps import ParameterServer
from util.log import log


class MnistInput(object):
    def __init__(self, message):
        self.worker_id = message['port']
        self.train_id = message['train_id']
        self.code_name = message['code_name']
        self.worker_count = message['worker_count']
        self.mod = self.worker_id % self.worker_count
        self.logs_path = \
            '/tmp/tensorflow_logs/%s/%s/%s/%d' % (
                util.yymmdd(), self.code_name, self.worker_count, self.mod)

        self.use_ps = True
        if self.code_name == 'mnist_no_ps':
            self.use_ps = False


def run(mnist_input):
    mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
    mi = mnist_input
    code_name = mi.code_name
    log.info('Start mnist: %s' % code_name)
    worker_id = mi.worker_id
    train_id = mi.train_id
    worker_count = mi.worker_count
    logs_path = mi.logs_path
    mod = mi.mod

    ps_conn = ParameterServer(train_id, worker_id, worker_count)

    learning_rate = 0.01
    training_epochs = 25
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
        iter_id = 1
        for epoch in range(training_epochs):
            cost_sum = 0.
            batch_count = 0

            total_batch = int(mnist.train.num_examples / batch_size)
            # Loop over all batches
            for i in range(total_batch):
                batch_xs, batch_ys = mnist.train.next_batch(batch_size)
                _, c, summary = sess.run([optimizer, cost, merged_summary_op],
                                         feed_dict={x: batch_xs, y: batch_ys})
                summary_writer.add_summary(summary, epoch * total_batch + i)
                cost_sum += c
                batch_count += 1

            avg_cost = float(cost_sum) / batch_count

            # Display logs per epoch step
            if (epoch + 1) % display_step == 0:
                print("Epoch:", '%04d' % (epoch + 1), "cost=",
                      "{:.9f}".format(avg_cost))

            ########
            if mi.use_ps:
                ps_conn.change_var_as_average(
                    sess,
                    iteration_id=iter_id,
                    variables=[W, b],
                    time_out_sec=10)
                iter_id += 1
                mod = (mod + 1) % worker_count

        print("Optimization Finished!")
        print("Accuracy:",
              acc.eval({x: mnist.test.images, y: mnist.test.labels}))
        print(
            "Run the command line:\n --> tensorboard "
            "--logdir=/tmp/tensorflow_logs \nThen open http://0.0.0.0:6006/ "
            "into your web browser")


if __name__ == '__main__':
    run()
