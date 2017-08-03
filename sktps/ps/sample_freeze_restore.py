from __future__ import print_function

import tensorflow as tf
from tensorflow.core.framework import graph_pb2
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import importer
from tensorflow.python.framework import ops

# from tensorflow.python.tools import freeze_graph
from util.log import log


def print_nodes(graph_def, msg=''):
    print('nodes in graph', msg, [n.name for n in graph_def.node])


def restore_graph(s):
    log.info('restore_graph')
    g = ops.get_default_graph()
    graph_def = graph_pb2.GraphDef()
    graph_def.ParseFromString(s)
    # print_nodes(graph_def)
    # print ('before', len(g.as_graph_def().node))
    importer.import_graph_def(graph_def, name='restore')
    # print ('after', len(g.as_graph_def().node))
    # print_nodes(g.as_graph_def())
    # t = g.get_tensor_by_name('restore/y1:0')
    return graph_def


def _get_node(restored, name):
    for n in restored.node:
        if n.name == name:
            return n
    return None


def run():
    log.info('Run freeze restore')

    y = tf.Variable([float(88.8), float(5)], name='y1')
    # print(y.op.node_def)
    init_op = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init_op)
        # sess.run(y)
        g = sess.graph
        g_def = g.as_graph_def()

        # print node names
        # print([n.name for n in g_def.node])

        # constants
        constants = graph_util.convert_variables_to_constants(
            sess, g_def, ['y1'])

        # serialize
        s = constants.SerializeToString()
        # print(len(g_def.node))
        print_nodes(g.as_graph_def(), 'before restore:')
        _ = restore_graph(s)
        print_nodes(g.as_graph_def(), 'after restore:')
        t = g.get_tensor_by_name('restore/y1:0')

        sess.run(y.assign(y + t))
        print(sess.run(y))
        # print(len(g_def.node))
        # print(sess.run(y.assign([float(99.9)])))
        # print(n)
        # print(sess.run(y.assign(n)))
        # g2 = tf.Graph()
        # g2_def = g2.as_graph_def()
        # print([n.name for n in g2_def.node])

# run()
