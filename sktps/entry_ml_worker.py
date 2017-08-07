from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import redis
from rq import Connection, Queue, Worker

from util.config import config

if __name__ == '__main__':
    info = config['pubsub']
    host = info[0]
    port = int(info[1])
    conn = redis.StrictRedis(host=host, port=port, db=0)
    with Connection(conn):
        q = Queue(connection=conn)
        Worker(q).work()
