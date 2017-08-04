from __future__ import print_function

import mnist_common


def run(message=None):
    mnist_input = mnist_common.MnistInput(message)
    mnist_common.run(mnist_input)
