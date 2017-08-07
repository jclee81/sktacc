import ast
import json
import pprint
import random
from datetime import datetime

from tensorflow.core.framework import graph_pb2
from tensorflow.python.framework import importer

from config import config

epoch = datetime.utcfromtimestamp(0)


def get_redis_cluster_address_randomly():
    candidates = config["ps"]
    return random.choice(candidates)


def get_worker_id(host, port):
    wid = '%s-%s' % (host, port)
    return wid


def get_transaction_id(train_id, worker_id, iteration_id):
    return '%s-%s-%09d' % (worker_id, train_id, iteration_id)


def get_group_id(train_id, iteration_id):
    return '%s-%09d' % (train_id, int(iteration_id))


def extract_json(message):
    if message is None:
        return None
    msg_type = message['type']
    if msg_type == 'message' or msg_type == 'pmessage':
        data_str = message['data']
        # print (data_str, type(data_str))
        data = json.loads(data_str)
        return data
    return None


def extract_json2(message):
    try:
        if message is None:
            return None
        msg_type = message['type']
        if msg_type == 'message' or msg_type == 'pmessage':
            data_str = message['data']
            return ast.literal_eval(data_str)
    except:
        print (message)
    return None


def hhmmss():
    now = datetime.now()
    now_str = now.strftime('%H%M%S')
    return now_str


def yymmdd():
    now = datetime.now()
    now_str = now.strftime('%y-%m-%d')
    return now_str


def restore_graph(name, s):
    graph_def = graph_pb2.GraphDef()
    graph_def.ParseFromString(s)
    importer.import_graph_def(graph_def, name=name)
    return graph_def


def now_milli_sec():
    dt = datetime.now()
    return int((dt - epoch).total_seconds() * 1000.0)


def print_nodes(sess):
    g = sess.graph
    g_def = g.as_graph_def()
    print([n.name for n in g_def.node])


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def print_out(stuff):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(stuff)
