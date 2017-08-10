import unittest

from ps.calculator_many import Group


class FakeTask:
    def __init__(self):
        self.return_value = None


class FakeRqq:
    def __init__(self):
        pass

    def enqueue(self, a, b):
        return FakeTask()


class CalculatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_group_basic(self):
        group_id = 'g001'
        train_id = 't001'
        parallel_count = 3
        variables = []
        group = Group(group_id, train_id, parallel_count, variables, FakeRqq())
        group.add_message(('key1', 1))
        group.add_message(('key2', 1))
        group.add_message(('key3', 1))
        self.assertEqual(group.messages.size(), 3)
        group._message_to_done()
        self.assertEqual(group.messages.size(), 0)
        self.assertEqual(len(group.done), 3)

    def test_group_final_task(self):
        group_id = 'g001'
        train_id = 't001'
        parallel_count = 3
        variables = []
        group = Group(group_id, train_id, parallel_count, variables, FakeRqq())
        group.add_message(('key2', 1))
        group.add_message(('key3', 1))
        group.add_message(('key1', 3))
        group._message_to_done()
        final_task = group._get_final_task()
        self.assertEqual(final_task[0], 'key1')

    def test_task(self):
        # create
        group_id = 'g001'
        train_id = 't001'
        parallel_count = 5
        variables = []
        group = Group(group_id, train_id, parallel_count, variables, FakeRqq())
        group.add_message(('key1', 1))
        group.add_message(('key2', 1))
        group.add_message(('key3', 1))
        group.add_message(('key4', 1))
        group.add_message(('key5', 1))
        group._message_to_done()
        group._create_new_task()
        self.assertEqual(len(group.ing), 2)
        self.assertEqual(len(group.done), 1)

        group._ing_to_done()
        self.assertEqual(len(group.ing), 2)
        self.assertEqual(len(group.done), 1)
        group.ing['0key1'].return_value = ('0key1', 2)
        group.ing['0key3'].return_value = ('0key3', 2)

        group._ing_to_done()
        self.assertEqual(len(group.ing), 0)
        self.assertEqual(len(group.done), 3)

        group._create_new_task()
        self.assertEqual(len(group.ing), 1)
        self.assertEqual(len(group.done), 1)

        group.ing['0key5'].return_value = ('0key5', 3)
        group._ing_to_done()
        final_task = group._get_final_task()
        self.assertEqual(len(group.ing), 0)
        self.assertEqual(len(group.done), 2)
        self.assertEqual(final_task, None)

        group._create_new_task()
        self.assertEqual(len(group.ing), 1)
        self.assertEqual(len(group.done), 0)

        group.ing['g001'].return_value = ('g001', 5)
        group._ing_to_done()
        final_task = group._get_final_task()
        self.assertEqual(len(group.ing), 0)
        self.assertEqual(len(group.done), 1)
        self.assertEqual(final_task[0], 'g001')


if __name__ == '__main__':
    unittest.main()
