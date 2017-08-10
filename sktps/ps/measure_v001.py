from __future__ import print_function

import util
from util.singleton import SingletonMixin


class Measure(SingletonMixin):
    def __init__(self):
        super(Measure, self).__init__()
        self.groups = []
        self.measurements = []

    def register_group(self, group_id, data_size):
        group = {
            'group_id': group_id,
            'data_size': data_size,
            'avg': -1,
        }
        self.groups.append(group)

    def create_measurement(self, node_type, train_id, group_id, worker_id=None):
        if worker_id:
            return {
                'node_type': node_type,
                'train_id': train_id,
                'group_id': group_id,
                'worker_id': worker_id,
            }
        else:
            return {
                'node_type': node_type,
                'train_id': train_id,
                'group_id': group_id,
            }

    def append(self, measurement):
        self.measurements.append(measurement)


class MeasureHelper(object):
    def __init__(self):
        pass

    def num_00_start_call_func(self, m):
        m['num_00_start_call_func'] = util.now_milli_sec()

    def num_01_after_pub_on_worker(self, m, data_size):
        m['num_01_after_pub_on_worker'] = util.now_milli_sec()
        m['data_size'] = data_size

    def num_02_before_get_on_controller(self, m):
        m['num_02_before_get_on_controller'] = util.now_milli_sec()

    def num_03_after_get_on_controller(self, m, parallel_count):
        m['num_03_after_get_on_controller'] = util.now_milli_sec()
        m['parallel_count'] = parallel_count

    def num_04_after_cal_avg_on_controller(self, m):
        m['num_04_after_cal_avg_on_controller'] = util.now_milli_sec()

    def num_05_after_pub_on_controller(self, m):
        m['num_05_after_pub_on_controller'] = util.now_milli_sec()

    def num_06_after_sub_on_worker(self, m):
        m['num_06_after_sub_on_worker'] = util.now_milli_sec()

    def num_07_after_get_on_worker(self, m):
        m['num_07_after_get_on_worker'] = util.now_milli_sec()

    def num_08_after_assign_on_worker(self, m):
        m['num_08_after_assign_on_worker'] = util.now_milli_sec()

    def num_09_finish_call_func(self, m, success):
        m['num_09_finish_call_func'] = util.now_milli_sec()
        m['success'] = success
