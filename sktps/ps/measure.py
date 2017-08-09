from __future__ import print_function

import util
from util.singleton import SingletonMixin


class SimpleMeasurement:
    def __init__(self, key, measurement):
        self.key = key
        self.measurement = measurement
        self.start = util.now_milli_sec()
        self.end = None

    def end_measure(self):
        self.end = util.now_milli_sec()
        diff = int(self.end) - int(self.start)
        self.measurement[self.key] += int(diff)


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
            # ml worker case
            return {
                'node_type': node_type,
                'train_id': train_id,
                'group_id': group_id,
                'worker_id': worker_id,
            }
        else:
            # controller case
            return {
                'node_type': node_type,
                'train_id': train_id,
                'group_id': group_id,
                'cal_and_put': 0,
                'init': 0,
                'cal': 0,
            }

    def append(self, measurement):
        self.measurements.append(measurement)


class MeasureHelper(object):
    def __init__(self):
        pass

    def num_00_init(self, m):
        m['num_00_init'] = util.now_milli_sec()

    def num_01_before_load_variables(self, m):
        m['num_01_before_load_variables'] = util.now_milli_sec()
        # m['data_size'] = data_size

    def num_01_after_load_variables(self, m):
        m['num_01_after_load_variables'] = util.now_milli_sec()
        # m['data_size'] = data_size

    def num_02_before_save_variables(self, m):
        m['num_02_before_save_variables'] = util.now_milli_sec()
        # m['data_size'] = data_size

    def num_02_after_save_variables(self, m, data_size):
        m['num_02_after_save_variables'] = util.now_milli_sec()
        m['data_size'] = data_size

    def num_03_after_get_on_controller(self, m, parallel_count):
        m['num_03_after_get_on_controller'] = util.now_milli_sec()
        m['parallel_count'] = parallel_count

    def num_05_after_pub_on_controller(self, m):
        m['num_05_after_pub_on_controller'] = util.now_milli_sec()
