import unittest
import numpy as np
from google.protobuf.json_format import ParseDict

from solve_schedule_ga import *
import tasks_pb2


def DictToTask(in_dict):
    return_task = tasks_pb2.Task()
    ParseDict(in_dict, return_task)
    return return_task


class TestIsValidSchedule(unittest.TestCase):
    def setUp(self):
        self._tasks = [
            DictToTask({
                'priority': 1,
                'time_required': 3,
            }),
            DictToTask({
                'priority': 3,
                'time_required': 3,
            }),
            DictToTask({
                'priority': 2,
                'time_required': 1,
            }),
            DictToTask({
                'priority': 4,
                'time_required': 8,
            }),
        ]

    def test_valid_filled_schedule(self):
        self.assertTrue(is_schedule_possible(
            [0, 0, 0, 1, 1, 1, 2], self._tasks))

    def test_empty_schedule(self):
        self.assertTrue(is_schedule_possible(
            [-1, -1, -1, -1, -1, -1, -1], self._tasks))

    def test_1_task_overbooked(self):
        self.assertFalse(is_schedule_possible(
            [2, 1, 1, 1, 1, 0, 0], self._tasks))

    def test_2_tasks_overbooked(self):
        self.assertFalse(is_schedule_possible(
            [2, 2, 1, 1, 1, 1, 0], self._tasks))

    def test_with_invalid_task(self):
        self.assertFalse(is_schedule_possible(
            [2, 1, 1, 1, 1, 0, 0], self._tasks))

    def test_with_empty_slots(self):
        self.assertTrue(is_schedule_possible(
            [2, 1, 1, 1, 0, 0, -1, -1], self._tasks))


class TestMutateSchedule(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self._tasks = [
            DictToTask({
                'priority': 1,
                'time_required': 3,
            }),
            DictToTask({
                'priority': 3,
                'time_required': 3,
            }),
            DictToTask({
                'priority': 2,
                'time_required': 1,
            }),
        ]

    def test_empty_schedule_and_tasks(self):
        self.assertEqual(mutate([], []), [], "Should be empty")

    def test_empty_schedule(self):
        self.assertEqual(mutate([], self._tasks), [], "Should be empty")

    def test_add_time_unit(self):
        schedule = [0, 0, 0, 1, 1, -1]
        self.assertEqual(mutate(schedule, self._tasks, True),
                         [0, 0, 0, 1, 1, 1],
                         "Should add 1 to the last time unit")

    def test_remove_time_unit(self):
        schedule = [0, 0, 0, 1, 1, -1]
        self.assertEqual(mutate(schedule, self._tasks, False),
                         [0, 0, -1, 1, 1, -1],
                         "Should change the 2-index to -1")


class TestMakeRandomGenes(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self._tasks = [
            DictToTask({
                'priority': 1,
                'time_required': 3,
            }),
            DictToTask({
                'priority': 3,
                'time_required': 3,
            }),
            DictToTask({
                'priority': 2,
                'time_required': 1,
            }),
        ]

    def test_random_genes(self):
        # Make random tasks with random time and priority
        # Will assert that the given schedule will still be
        # a valid schedule
        pass


if __name__ == '__main__':
    unittest.main()
