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
            [2, 2, 1, 1, 1, 1, -1], self._tasks))

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
        schedule = make_random_genes(self._tasks, 10)
        self.assertTrue(is_schedule_possible(schedule, self._tasks))

    def test_empty_tasks(self):
        schedule = make_random_genes({}, 5)
        self.assertEqual([-1, -1, -1, -1, -1], schedule,
                         "This array should be filled with -1")

    def test_schedule_with_alot_of_tasks(self):
        tasks = self._tasks * 3
        schedule = make_random_genes(tasks, 10)
        self.assertTrue(is_schedule_possible(schedule, tasks))


class TestFitnessFunction(unittest.TestCase):
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
            DictToTask({
                'priority': 4,
                'time_required': 5,
            }),
        ]

    def test_empty_schedule(self):
        schedule = [-1, -1, -1, -1]
        self.assertEqual(fitness_impl(schedule, self._tasks),
            [0.0, 1.0, 0.0, 0.0])

    def test_filled_schedule(self):
        schedule = [0, 0, 3, 3]
        self.assertEqual(fitness_impl(schedule, self._tasks),
            [0.0, 0.9330329915368074, 1.0, 0.375])

    def test_low_priority(self):
        schedule = [3, 3, 3, 3]
        self.assertEqual(fitness_impl(schedule, self._tasks),
            [0.0, 1.0, 1.0, 0.0])

    def test_high_priority(self):
        schedule = [0, 0, 0, 2]
        self.assertEqual(fitness_impl(schedule, self._tasks),
            [1.0, 0.9330329915368074, 1.0, 0.625])

    def test_context_switched(self):
        schedule = [0, 1, 2, 3]
        self.assertEqual(fitness_impl(schedule, self._tasks),
            [0.25, 0.8122523963562356, 1.0, 0.375])

if __name__ == '__main__':
    unittest.main()
