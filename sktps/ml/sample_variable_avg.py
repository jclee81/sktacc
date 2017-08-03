import tensorflow as tf


def run():
    x1 = tf.Variable([1.0, 2.0], name='x1')
    x2 = tf.Variable([8.0, 4.0], name='x2')

    init_op = tf.global_variables_initializer()

    with tf.Session() as session:
        session.run(init_op)
        print(session.run(x1))
        session.run(x1.assign((x1 + x2) / 2))
        print(session.run(x1))
        print(session.run(x2))


run()
