import argparse
import threading

from flask import Flask
from flask_socketio import SocketIO

import ml.code1 as code1
import ml.mnist_mod_run
import ml.mnist_wo_mod_run
import ml.mnist_single

import ml.mnist_deep as mnist_deep
from util.log import log
from util.pony import Pony
from util.util import get_worker_id

parser = argparse.ArgumentParser(description="fake ml node")
parser.add_argument('host')
parser.add_argument('port')
args = parser.parse_args()
host = args.host
port = int(args.port)
wid = get_worker_id(host, port)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    # Pony().log({ 'key': 'connect', 'type': 'worker', 'value': wid, })
    return 'Hello this is fake ml node %d' % port


@socketio.on('connect')
def on_connect():
    log.debug('on_connect')


@socketio.on('disconnect')
def on_disconnect():
    log.debug('on_disconnect')


@socketio.on('ping')
def ping(message):
    log.info('on ping: %s', message)
    # emit('my_event', {'data': 'pong'})
    return 'pong'


#######################
def start_train(message):
    code_name = message['code_name']
    train_id = message['train_id']

    Pony().log({
        'key': 'START_ML_TRAIN',
        'code_name': code_name,
        'worker_id': wid,
        'train_id': train_id,
    })

    if code_name == 'code1':
        code1.run(message)
    elif code_name == 'mnist_mod_run':
        ml.mnist_mod_run.run(message)
    elif code_name == 'mnist_wo_mod_run':
        ml.mnist_wo_mod_run.run(message)
    elif code_name == 'mnist_single':
        ml.mnist_single.run(message)
    else:
        log.error('Invalid code name: %s' % code_name)

    Pony().log({
        'key': 'FINISH_ML_TRAIN',
        'code_name': code_name,
        'worker_id': wid,
        'train_id': train_id,
    })


#######################


@socketio.on('train_now')
def train_now(message):
    log.info('on train_now message: %s' % message['port'])
    t = threading.Thread(target=start_train, args=(message,))
    t.start()
    return 'ok'


if __name__ == '__main__':
    log.warn('START PROCESS: ml worker (listen port: %d)', port)
    Pony().log({'key': 'START_ML_WORKER', 'worker_id': wid})
    socketio.run(app, host=host, port=port)
