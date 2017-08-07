import util
from util.log import log


class DefaultAgingPolicy(object):
    def __init__(self):
        self.try_count = 0
        self.target_iteration_id = -1

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
        raw = ps.rc.get(group_id)
        if raw is None:
            log.info('Aging: target iteration id will be decreased')
            success = False
        else:
            success = True
        return first, success, group_id, raw

