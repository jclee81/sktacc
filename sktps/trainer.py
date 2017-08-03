import argparse
import sys

from socketIO_client import SocketIO

from util.log import log

parser = argparse.ArgumentParser(description="fake trainer")
parser.add_argument('host')
parser.add_argument('port')
parser.add_argument('worker_count')
parser.add_argument('train_id')
parser.add_argument('code_name')
args = parser.parse_args()
host = args.host
port = int(args.port)
worker_count = int(args.worker_count)
code_name = args.code_name
train_id = args.train_id


class Trainer(object):
    def __init__(self):
        pass

    def send_train_signal(self):
        log.info('Send signal from trainer %s:%d (worker#: %d, %s)' % (
            host, port, worker_count, code_name))

        with SocketIO(host, port) as socketIO:
            log.info('send train_now')
            socketIO.emit('train_now', {
                'host': host,
                'port': port,
                'train_id': train_id,
                'worker_count': worker_count,
                'code_name': code_name,
            }, self.cb)
            socketIO.wait_for_callbacks(seconds=1)

    def cb(self, *args):
        log.info('finish trainer')
        sys.exit(1)


if __name__ == '__main__':
    log.warn('START PROCESS: trainer (connect port: %d)', port)
    Trainer().send_train_signal()
