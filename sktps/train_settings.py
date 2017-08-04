import ml.code1
import ml.mnist_with_ps
import ml.mnist_no_ps
import ml.cnn_mnist

train_actions = {
    'code1': ml.code1,
    'mnist_with_ps': ml.mnist_with_ps,
    'mnist_no_ps': ml.mnist_no_ps,
    'cnn_mnist': ml.cnn_mnist
}

# train_code_names = ['mnist_no_ps', 'mnist_with_ps']
# train_code_names = ['cnn_mnist']
# train_code_names = ['code1', 'cnn_mnist', 'mnist_no_ps', 'mnist_with_ps']
train_code_names = ['code1']

