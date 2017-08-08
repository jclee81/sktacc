"""A deep MNIST classifier using convolutional layers.
See extensive documentation at
https://www.tensorflow.org/get_started/mnist/pros
"""
# Disable linter warnings to maintain consistency with tutorial.
# pylint: disable=invalid-name
# pylint: disable=g-bad-import-order

from __future__ import absolute_import, division, print_function

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

import util
from ps import ParameterServer
from util.log import log

FLAGS = None


def deepnn(x):
    """deepnn builds the graph for a deep net for classifying digits.

    Args:
      x: an input tensor with the dimensions (N_examples, 784), where 784 is the
      number of pixels in a standard MNIST image.

    Returns:
      A tuple (y, keep_prob). y is a tensor of shape (N_examples, 10),
      with values
      equal to the logits of classifying the digit into one of 10 classes (the
      digits 0-9). keep_prob is a scalar placeholder for the probability of
      dropout.
    """
    vs = []
    # Reshape to use within a convolutional neural net.
    # Last dimension is for "features" - there is only one here, since images
    #  are grayscale -- it would be 3 for an RGB image, 4 for RGBA, etc.
    x_image = tf.reshape(x, [-1, 28, 28, 1])

    # First convolutional layer - maps one grayscale image to 32 feature maps.
    W_conv1 = weight_variable([5, 5, 1, 32], vs)
    b_conv1 = bias_variable([32], vs)
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)

    # Pooling layer - downsamples by 2X.
    h_pool1 = max_pool_2x2(h_conv1)

    # Second convolutional layer -- maps 32 feature maps to 64.
    W_conv2 = weight_variable([5, 5, 32, 64], vs)
    b_conv2 = bias_variable([64], vs)
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

    # Second pooling layer.
    h_pool2 = max_pool_2x2(h_conv2)

    # Fully connected layer 1 -- after 2 round of downsampling, our 28x28 image
    # is down to 7x7x64 feature maps -- maps this to 1024 features.
    W_fc1 = weight_variable([7 * 7 * 64, 1024], vs)
    b_fc1 = bias_variable([1024], vs)

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    # Dropout - controls the complexity of the model, prevents co-adaptation of
    # features.
    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    # Map the 1024 features to 10 classes, one for each digit
    W_fc2 = weight_variable([1024, 10], vs)
    b_fc2 = bias_variable([10], vs)

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
    return y_conv, keep_prob, vs


def conv2d(x, W):
    """conv2d returns a 2d convolution layer with full stride."""
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    """max_pool_2x2 downsamples a feature map by 2X."""
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')


def weight_variable(shape, vs):
    """weight_variable generates a weight variable of a given shape."""
    initial = tf.truncated_normal(shape, stddev=0.1)
    v = tf.Variable(initial)
    vs.append(v)
    return v


def bias_variable(shape, vs):
    """bias_variable generates a bias variable of a given shape."""
    initial = tf.constant(0.1, shape=shape)
    v = tf.Variable(initial)
    vs.append(v)
    return v


def run(raw_data):
    message = raw_data[0]
    worker_id = raw_data[1]
    iteration_id = raw_data[2]
    train_id = message['train_id']
    worker_count = message['worker_count']

    logs_path = '/tmp/tensorflow_logs/%s/%s' % (util.yymmdd(), 'cnn_mnist')

    log.warn('Run cnn_mnist(%s, %s)' % (train_id, worker_id))

    mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
    x = tf.placeholder(tf.float32, [None, 784])
    y_ = tf.placeholder(tf.float32, [None, 10])

    y_conv, keep_prob, variables = deepnn(x)

    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    tf.summary.scalar("accuracy", accuracy)
    tf.summary.scalar('cross_entropy', cross_entropy)
    merged = tf.summary.merge_all()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        summary_writer = tf.summary.FileWriter(
            logs_path, graph=tf.get_default_graph())

        ps_conn = ParameterServer(
            sess, train_id, worker_id, iteration_id, variables, None,
            worker_count)
        batch = mnist.train.next_batch(200)

        ps_conn.load_variables()
        sess.run(
            [train_step],
            feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
        ps_conn.save_variables()

        summary, acc = sess.run(
            [merged, accuracy],
            feed_dict={
                x: mnist.test.images,
                y_: mnist.test.labels,
                keep_prob: 1.0})
        print('acc: %s' % acc)

        # summary_writer.add_summary(summary, iteration_id)

    return True
