import tensorflow as tf

from ps import ParameterServer
from util.log import log


def run(raw_data):
    log.info('Run code1')
    message = raw_data[0]
    worker_id = raw_data[1]
    iteration_id = raw_data[2]

    train_id = message['train_id']
    parallel_count = message['parallel_count']

    y1 = tf.Variable([float(iteration_id)], name='y1')
    init_op = tf.global_variables_initializer()

    ps_conn = ParameterServer(train_id, worker_id, parallel_count)

    with tf.Session() as sess:
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
    return True
