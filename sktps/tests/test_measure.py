import unittest

from ps.measure import Measure, MeasureHelper


class MeasureTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_measurement(self):
        node_type = 'n'
        train_id = 't'
        group_id = 'g'
        worker_id = 'w'

        m = Measure().create_measurement(
            node_type, train_id, group_id, worker_id)

        self.assertEqual(m['node_type'], node_type)
        self.assertEqual(m['group_id'], group_id)
        self.assertEqual(m['worker_id'], worker_id)

        mh = MeasureHelper()

        mh.num_00_start_call_func(m)
        mh.num_01_after_pub_on_worker(m, 99)
        mh.num_02_before_get_on_controller(m)
        mh.num_03_after_get_on_controller(m, 2)
        mh.num_04_after_cal_avg_on_controller(m)
        mh.num_05_after_pub_on_controller(m)
        mh.num_06_after_sub_on_worker(m)
        mh.num_07_after_get_on_worker(m)
        mh.num_08_after_assign_on_worker(m)
        mh.num_09_finish_call_func(m, True)

        t = type(1)  # integer

        self.assertEqual(m['data_size'], 99)
        self.assertEqual(type(m['num_00_start_call_func']), t)
        self.assertEqual(type(m['num_01_after_pub_on_worker']), t)
        self.assertEqual(type(m['num_02_before_get_on_controller']), t)
        self.assertEqual(type(m['num_03_after_get_on_controller']), t)
        self.assertEqual(type(m['num_04_after_cal_avg_on_controller']), t)
        self.assertEqual(type(m['num_05_after_pub_on_controller']), t)
        self.assertEqual(type(m['num_06_after_sub_on_worker']), t)
        self.assertEqual(type(m['num_07_after_get_on_worker']), t)
        self.assertEqual(type(m['num_08_after_assign_on_worker']), t)
        self.assertEqual(type(m['num_09_finish_call_func']), t)
        self.assertEqual(m['success'], True)

        mh.num_09_finish_call_func(m, False)
        self.assertEqual(m['success'], False)


if __name__ == '__main__':
    unittest.main()
