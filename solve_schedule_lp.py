# Lint as: python3
"""Linear/integer programming schedule solver."""

from ortools.linear_solver import pywraplp


def solve_schedule(tasks_d, num_time_units=16):
    solver = pywraplp.Solver.CreateSolver('SCIP') or pywraplp.Solver.CreateSolver('CBC')
    if solver is None:
        return []

    task_ids = list(tasks_d.keys())
    x = {}
    for task_id in task_ids:
        for unit in range(num_time_units):
            x[task_id, unit] = solver.BoolVar(f'x[{task_id},{unit}]')

    for task_id in task_ids:
        solver.Add(sum(x[task_id, unit] for unit in range(num_time_units)) <= tasks_d[task_id]['time'])

    for unit in range(num_time_units):
        solver.Add(sum(x[task_id, unit] for task_id in task_ids) <= 1)

    objective = solver.Objective()
    for task_id in task_ids:
        for unit in range(num_time_units):
            objective.SetCoefficient(x[task_id, unit], tasks_d[task_id]['priority'])
    objective.SetMaximization()

    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return []

    schedule = [-1] * num_time_units
    for unit in range(num_time_units):
        for task_id in task_ids:
            if x[task_id, unit].solution_value() > 0.5:
                schedule[unit] = task_id
                break
    return schedule
