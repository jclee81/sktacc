# -*- coding: utf-8 -*-
# # 1. init
# # train_id: 사용자가 지정한 문자열인데 중복 이슈가 없도록 해결한다.
# # my_iteration_id: 현재 이터레이션 값. sync의 기준이 된다
# # worker_count: 같이 iteration을 도는 워커의 총 수.
# # persistent: True라면 iteration의 결과값을 디스크에 저장하도록 한다.
# ps.initialize(train_id, my_iteration_id, worker_count, persistent:True)
#
# # 2. build graph
# sess = tf.Session()
#
# # 3. load variable
# # sync/async방식을 둘 다 지원할 수 있으면 좋다. 당장은 sync만 지원하도록 한다.
# # load variable을 할 때에는 memcopy가 안되도록 하는 것이 중요하다.
# mode = { 'sync_mode': 'async',  'tolerance_step': 2, }
# # tolerance step: 가장 최근에 싱크된 데이터를 가져와라
# ps.load_variables(sess, target_iteration_id, mode)
#
# # 4. run train
#
# # 5. set trained weights to ps
# ps.save_variables(sess, my_iteration_id)
#
# # 따로 API제공
# # 위의 4개 함수는 트레이너가 코드 내에서 작성하는 코드인데 그 이외에 트레이너가 원할 때 따로 호출할 수 있는
# # API를 제공하도록 한다. 만약 트레이너가 중간 학습 결과를 로컬 디스크에 받아오고 싶은 경우라면
# # 아래 함수를 이용해서 받아올 수 있도록 해준다.
# # copy_to_local(train_id, iteration_id, target_path) : copy from ps storage
#  to local

import time

import tensorflow as tf

import ps
from util.log import log


def run(raw_data):
    log.debug('Run code2')
    message = raw_data[0]
    worker_id = raw_data[1]
    iteration_id = raw_data[2]

    train_id = message['train_id']
    worker_count = message['worker_count']

    y1 = tf.Variable([float(iteration_id)], name='y1')
    init_op = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init_op)

        ps_conn = ps.ParameterServer(
            sess,
            train_id,
            worker_id,
            iteration_id,
            [y1],
            ps.DefaultAgingPolicy(),
            worker_count)

        while True:
            ########
            if ps_conn.load_variables(None):
                break
            time.sleep(0.1)

        sess.run(y1.assign_add([2.]))

        ########
        ps_conn.save_variables()
        log.warn('after set_average! it works!!!')
        print(y1.eval())

    return True
