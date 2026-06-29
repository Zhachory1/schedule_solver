import unittest
from collections import Counter

from solve_schedule_basic import solve_priority_first, solve_random


class BasicSolverTest(unittest.TestCase):
    def test_solve_random_is_seedable_and_capacity_safe(self):
        tasks = {
            1: {"priority": 1, "time": 2},
            2: {"priority": 3, "time": 1},
        }

        schedule = solve_random(tasks, num_time_units=4, seed=7)
        counts = Counter(schedule)

        self.assertEqual(schedule, solve_random(tasks, num_time_units=4, seed=7))
        self.assertLessEqual(counts[1], 2)
        self.assertLessEqual(counts[2], 1)
        self.assertEqual(counts[-1], 1)

    def test_solve_priority_first_packs_highest_priority_first(self):
        tasks = {
            1: {"priority": 1, "time": 2},
            2: {"priority": 3, "time": 2},
            3: {"priority": 2, "time": 1},
        }

        self.assertEqual(solve_priority_first(tasks, num_time_units=4), [2, 2, 3, 1])


if __name__ == "__main__":
    unittest.main()
