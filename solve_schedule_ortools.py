# Lint as: python3
"""Simple schedule creator with Google's OrTools.

Run with:

python3 solve_schedule_ortools.py --input=tasks.csv --output=schedule.csv
"""

from absl import app
from absl import flags

import pandas as pd
from ortools.sat.python import cp_model
import pprint

from schedule_output import write_schedule_csv

FLAGS = flags.FLAGS
flags.DEFINE_string('input', 'tasks.csv', 'CSV file with tasks, priority and'
                    ' time they take in 15-minute blocks')
flags.DEFINE_string('output', 'schedule.csv', 'CSV file with schedule with the'
                    ' task, the start index, and the end index.')


def parse_input(file_name):
    tasks = pd.read_csv(file_name)
    tasks_d = {}
    max_priority = 0.0
    for index, task in tasks.iterrows():
        tasks_d[task['Index']] = {
            'priority': task['Priority'],
            'time': task['Time (15min)'],
        }
        max_priority = max(max_priority, float(task['Priority']))
    return max_priority, tasks_d


def print_schedule(solver, X, task_ids=None):
    if len(X) == 0:
        raise Exception("Empty variable set")
    num_tasks = len(X)
    num_time_units = len(X[0])
    task_ids = task_ids or list(range(1, num_tasks + 1))

    schedule = [-1] * num_time_units
    for task in range(num_tasks):
        for unit in range(num_time_units):
            value = solver.Value(X[task][unit])
            if value != 0:
                if schedule[unit] != -1:
                    raise Exception("This unit is already scheduled")
                schedule[unit] = task_ids[task]
    return schedule


def solve_schedule(tasks_d, num_time_units=16):
    num_tasks = len(tasks_d)
    task_ids = list(tasks_d.keys())

    model = cp_model.CpModel()

    X = []
    for task in range(num_tasks):
        t = []
        for time_unit in range(num_time_units):
            t.append(model.NewIntVar(0, 1, "X[{},{}]".format(task, time_unit)))
        X.append(t)

    for idx, task_id in enumerate(task_ids):
        model.Add(sum(X[idx][unit] for unit in
                      range(num_time_units)) <= tasks_d[task_id]['time'])

    for unit in range(num_time_units):
        model.Add(sum(X[task][unit] for task in range(num_tasks)) <= 1)

    objective_terms = []
    for idx, task_id in enumerate(task_ids):
        slots_for_task = sum(X[idx][unit] for unit in range(num_time_units))
        objective_terms.append(3 * (tasks_d[task_id]['time'] - slots_for_task))
        objective_terms.append(slots_for_task * tasks_d[task_id]['priority'])

    pprint.pprint(objective_terms)
    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Total cost = %i' % solver.ObjectiveValue())
        print(solver.ResponseStats())
        schedule = print_schedule(solver, X, task_ids)
        print(schedule)
        return schedule
    return []


def main(argv):
    if len(argv) > 2:
        raise app.UsageError('Too many command-line arguments.')

    max_priority, tasks_d = parse_input(FLAGS.input)
    schedule = solve_schedule(tasks_d)
    write_schedule_csv(FLAGS.output, schedule)
    print(f"Wrote schedule to {FLAGS.output}")


if __name__ == '__main__':
    app.run(main)
