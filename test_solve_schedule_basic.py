import unittest

from solve_schedule_basic import solve_greedy


class GreedySolverTest(unittest.TestCase):
    def test_solve_greedy_schedules_highest_priority_first(self):
        tasks = {
            1: {"priority": 1, "time": 2},
            2: {"priority": 3, "time": 2},
            3: {"priority": 2, "time": 1},
        }

        self.assertEqual(solve_greedy(tasks, num_time_units=4), [2, 2, 3, 1])

    def test_solve_greedy_pads_empty_slots(self):
        tasks = {
            1: {"priority": 1, "time": 1},
        }

        self.assertEqual(solve_greedy(tasks, num_time_units=3), [1, -1, -1])


if __name__ == "__main__":
    unittest.main()
