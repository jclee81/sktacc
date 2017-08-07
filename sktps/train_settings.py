import ml.code1
import ml.mnist_with_ps
import ml.mnist_no_ps
import ml.cnn_mnist
import sandbox.fib

train_actions = {
    'fib': sandbox.fib,
    'code1': ml.code1,
    'mnist_with_ps': ml.mnist_with_ps,
    'mnist_no_ps': ml.mnist_no_ps,
    'cnn_mnist': ml.cnn_mnist
}

train_worker_count = 2
train_code_name = 'code1'

