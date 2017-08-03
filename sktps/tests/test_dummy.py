import unittest

import tensorflow as tf


class Dummy(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy1(self):
        self.assertEqual(30, 30)
        #
        # y1 = tf.Variable([float(1.0)], name='y1')
        # y2 = tf.Variable([float(3.0)], name='y2')
        # init_op = tf.global_variables_initializer()
        # with tf.Session() as sess:
        #     sess.run(init_op)
        #     dest = [var for var in tf.global_variables()
        #             if var.op.name == 'y1'][0]
        #     print(sess.run(dest.assign(y2)))
        #     sess.run(init_op)
        #     print(y1.eval())


if __name__ == '__main__':
    unittest.main()
