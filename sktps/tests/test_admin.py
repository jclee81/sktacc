import unittest

import util
from admin import MeasureContainer


def get_sample_measurement_data(node_type):
    if node_type == 'controller':
        return {
            'key': 'MEASUREMENT',
            'node_type': 'controller',
            'train_id': 't095618',
            'group_id': u't095618-000000001',
            'parallel_count': 2,

            'num_03_after_get_on_controller': 1501754183101,
            'num_04_after_cal_avg_on_controller': 1501754183201,
            'num_05_after_pub_on_controller': 1501754183201,
        }
    else:
        return [{
            'key': 'MEASUREMENT',
            'node_type': 'ps',
            'train_id': 't095618',
            'worker_id': 'w11111',
            'group_id': u't095618-000000001',
            'data_size': 55,

            'num_00_start_call_func': 1501754183004,
            'num_01_after_pub_on_worker': 1501754183007,
            'num_06_after_sub_on_worker': 1501754183201,
            'num_07_after_get_on_worker': 1501754183201,
            'num_08_after_assign_on_worker': 1501754183206,
            'num_09_finish_call_func': 1501754183206,

            'success': True,
        }, {
            'key': 'MEASUREMENT',
            'node_type': 'ps',
            'train_id': 't095618',
            'worker_id': 'w22222',
            'group_id': u't095618-000000001',
            'data_size': 55,

            'num_00_start_call_func': 1501754183004,
            'num_01_after_pub_on_worker': 1501754183007,
            'num_06_after_sub_on_worker': 1501754183201,
            'num_07_after_get_on_worker': 1501754183201,
            'num_08_after_assign_on_worker': 1501754183206,
            'num_09_finish_call_func': 1501754183206,

            'success': True,
        }]


class AdminTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handle_measurement(self):
        mc = MeasureContainer()
        controller_data = get_sample_measurement_data('controller')
        ps_data = get_sample_measurement_data('ps')
        group_id = controller_data['group_id']

        # merged_data = mc._merge(ps_data[0], controller_data)
        # l = mc._to_list(merged_data)
        # mc._append(merged_data)
        # util.print_out(mc.df)

        # 1. ps
        mc.update(ps_data[0])
        self.assertEqual(0, len(mc.df))
        self.assertEqual(1, len(mc.ps_dict))

        # 2. controller
        mc.update(controller_data)
        self.assertEqual(1, len(mc.df))
        self.assertEqual(0, len(mc.ps_dict))

        # 3. ps
        mc.update(ps_data[1])
        self.assertEqual(2, len(mc.df))
        self.assertEqual(0, len(mc.ps_dict))
        self.assertEqual(group_id in mc.controller_dict, True)

        # util.print_out(mc.get_group_stat_json())
        # util.print_out(mc.get_train_stat_json())


if __name__ == '__main__':
    unittest.main()
