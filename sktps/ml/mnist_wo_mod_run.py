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

from ps import ParameterServer
from util.log import log


model_name = 'mnist_wo_mod_run'


def run(message=None):
    log.warn('Start mnist2 - W/O mod run in iteration')
    mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

    worker_id = 'w1'
    train_id = 't1'
    worker_count = 1
    if message:
        worker_id = message['port']
        train_id = message['train_id']
        worker_count = message['worker_count']

    ps_conn = ParameterServer(train_id, worker_id, worker_count)

    mod = worker_id % worker_count
    log.error('%s mod: %d' % (worker_id, mod))

    # Parameters
    learning_rate = 0.01
    training_epochs = 25
    batch_size = 100
    display_step = 1
    logs_path = '/tmp/tensorflow_logs/example/%s/%d/%d' % (
        model_name, worker_count, mod)

    # tf Graph Input
    # mnist data image of shape 28*28=784
    x = tf.placeholder(tf.float32, [None, 784], name='InputData')
    # 0-9 digits recognition => 10 classes
    y = tf.placeholder(tf.float32, [None, 10], name='LabelData')

    # Set model weights
    W = tf.Variable(tf.zeros([784, 10]), name='Weights')
    b = tf.Variable(tf.zeros([10]), name='Bias')

    # Construct model and encapsulating all ops into scopes, making
    # Tensorboard's Graph visualization more convenient
    with tf.name_scope('Model'):
        # Model
        pred = tf.nn.softmax(tf.matmul(x, W) + b)  # Softmax
    with tf.name_scope('Loss'):
        # Minimize error using cross entropy
        cost = tf.reduce_mean(
            -tf.reduce_sum(y * tf.log(pred), reduction_indices=1))
    with tf.name_scope('SGD'):
        # Gradient Descent
        optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(
            cost)
    with tf.name_scope('Accuracy'):
        # Accuracy
        acc = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
        acc = tf.reduce_mean(tf.cast(acc, tf.float32))

    # Initializing the variables
    init = tf.global_variables_initializer()

    # Create a summary to monitor cost tensor
    tf.summary.scalar("loss", cost)
    # Create a summary to monitor accuracy tensor
    tf.summary.scalar("accuracy", acc)
    # Merge all summaries into a single op
    merged_summary_op = tf.summary.merge_all()

    # Launch the graph
    with tf.Session() as sess:
        sess.run(init)

        # op to write logs to Tensorboard
        summary_writer = tf.summary.FileWriter(
            logs_path, graph=tf.get_default_graph())
        # Training cycle
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
                # Write logs at every iteration
                summary_writer.add_summary(summary, epoch * total_batch + i)
                # Compute average loss
                cost_sum += c
                batch_count += 1

            avg_cost = float(cost_sum) / batch_count

            ps_conn.change_var_as_average(
                sess,
                iteration_id=iter_id,
                variables=[W, b],
                time_out_sec=10)
            iter_id += 1
            mod = (mod + 1) % worker_count

            # Display logs per epoch step
            if (epoch + 1) % display_step == 0:
                print("Epoch:", '%04d' % (epoch + 1), "cost=",
                      "{:.9f}".format(avg_cost))

        print("Optimization Finished!")

        # Test model
        # Calculate accuracy
        print("Accuracy:",
              acc.eval({x: mnist.test.images, y: mnist.test.labels}))

        print(
            "Run the command line:\n --> tensorboard "
            "--logdir=/tmp/tensorflow_logs \nThen open http://0.0.0.0:6006/ "
            "into your web browser")


if __name__ == '__main__':
    run()
