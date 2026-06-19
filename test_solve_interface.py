import unittest
from types import SimpleNamespace

from solve_interface import SolverInterface


class DemoSolver(SolverInterface):
    def _solve_impl(self):
        return [1, 1, -1]


class SolveInterfaceTest(unittest.TestCase):
    def test_solve_schedule_returns_and_stores_schedule(self):
        solver = DemoSolver()

        self.assertEqual(solver.solve_schedule(), [1, 1, -1])
        self.assertEqual(solver.get_schedule(), [1, 1, -1])

    def test_update_tasks_subtracts_scheduled_units(self):
        task = SimpleNamespace(id=1, time_required=3)
        solver = SolverInterface(tasks=[task], num_of_increments=3)
        solver.schedule = [1, 1, -1]

        solver.update_tasks()

        self.assertEqual(task.time_required, 1)

    def test_find_random_units_handles_empty_and_full_cases(self):
        self.assertEqual(SolverInterface._find_random_empty_unit([]), -1)
        self.assertEqual(SolverInterface._find_random_empty_unit([1, 2]), -1)
        self.assertEqual(SolverInterface._find_random_filled_unit([-1, -1]), -1)


if __name__ == "__main__":
    unittest.main()
