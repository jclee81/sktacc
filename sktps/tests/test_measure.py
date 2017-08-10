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

        mh.num_00_init(m)
        mh.num_01_before_load_variables(m)
        mh.num_01_after_load_variables(m)

        mh.num_02_before_save_variables(m)
        mh.num_02_after_save_variables(m, 99)

        mh.num_03_after_get_on_controller(m, 2)
        mh.num_05_after_pub_on_controller(m)

        t = type(1)  # integer

        self.assertEqual(m['data_size'], 99)
        self.assertEqual(m['parallel_count'], 2)
        self.assertEqual(type(m['num_00_init']), t)
        self.assertEqual(type(m['num_01_before_load_variables']), t)
        self.assertEqual(type(m['num_01_after_load_variables']), t)

        self.assertEqual(type(m['num_02_before_save_variables']), t)
        self.assertEqual(type(m['num_02_after_save_variables']), t)

        self.assertEqual(type(m['num_03_after_get_on_controller']), t)
        self.assertEqual(type(m['num_05_after_pub_on_controller']), t)


if __name__ == '__main__':
    unittest.main()
