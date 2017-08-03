import tensorflow as tf

from ps import ParameterServer
from util.log import log


def run(message):
    log.info('Run code1')

    worker_id = message['port']
    train_id = message['train_id']
    worker_count = message['worker_count']

    y1 = tf.Variable([float(worker_id)], name='y1')
    init_op = tf.global_variables_initializer()

    ps_conn = ParameterServer(train_id, worker_id, worker_count)

    with tf.Session() as sess:
        for i in range(0, 1):
            iteration_id = i + 1
            sess.run(init_op)

            ########
            ps_conn.change_var_as_average(
                sess,
                iteration_id=iteration_id,
                variables=[y1],
                time_out_sec=10)
            ########

            log.warn('after set_average! it works!!!')
            print(y1.eval())
