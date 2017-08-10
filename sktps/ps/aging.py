import util
import time
from util.log import log


class DefaultAgingPolicy(object):
    def __init__(self, time_out_sec=30):
        self.target_iteration_id = -1
        self.time_out_sec = time_out_sec

    def init(self, parameter_server):
        self.target_iteration_id = parameter_server.iteration_id

    def get_data(self, parameter_server):
        self.target_iteration_id -= 1
        iid = self.target_iteration_id
        success = True
        first = True
        if iid < 0:
            return first, success, '', None
        first = False

        ps = parameter_server
        group_id = util.get_group_id(ps.train_id, iid)

        max_try_count = self.time_out_sec / 0.1
        try_count = 0
        while True:
            raw = ps.rc.get(group_id)
            try_count += 1
            if raw is None:
                if max_try_count > try_count:
                    time.sleep(0.1)
                    continue
                else:
                    log.info('Aging: target iteration id will be decreased')
                    success = False
            else:
                success = True
            return first, success, group_id, raw

