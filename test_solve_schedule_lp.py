import unittest

try:
    import solve_schedule_lp
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f"LP solver tests require missing dependency: {exc.name}") from exc


class LinearSolverSmokeTest(unittest.TestCase):
    def test_solve_schedule_returns_task_ids_within_capacity(self):
        tasks = {
            101: {"priority": 1, "time": 1},
            202: {"priority": 2, "time": 2},
        }

        schedule = solve_schedule_lp.solve_schedule(tasks, num_time_units=3)

        self.assertEqual(len(schedule), 3)
        self.assertTrue(set(schedule).issubset({-1, 101, 202}))
        self.assertLessEqual(schedule.count(101), 1)
        self.assertLessEqual(schedule.count(202), 2)


if __name__ == "__main__":
    unittest.main()
