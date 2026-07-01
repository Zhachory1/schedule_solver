import unittest

try:
    import solve_schedule_ortools as ortools_solver
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(f"OR-Tools smoke tests require missing dependency: {exc.name}") from exc


class OrToolsSmokeTest(unittest.TestCase):
    def test_parse_input_reads_repo_tasks_csv(self):
        max_priority, tasks = ortools_solver.parse_input("tasks.csv")

        self.assertEqual(max_priority, 3.0)
        self.assertEqual(tasks[1], {"priority": 3, "time": 1})
        self.assertEqual(tasks[2], {"priority": 2, "time": 6})
        self.assertEqual(tasks[3], {"priority": 1, "time": 1})

    def test_solve_schedule_returns_task_ids_within_capacity(self):
        tasks = {
            101: {"priority": 1, "time": 1},
            202: {"priority": 2, "time": 2},
        }

        schedule = ortools_solver.solve_schedule(tasks, num_time_units=3)

        self.assertEqual(len(schedule), 3)
        self.assertTrue(set(schedule).issubset({-1, 101, 202}))
        self.assertLessEqual(schedule.count(101), 1)
        self.assertLessEqual(schedule.count(202), 2)


if __name__ == "__main__":
    unittest.main()
