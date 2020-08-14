# Lint as: python3
"""Simple schedule creator with Google's OrTools

Simple case of using a hammer to paint. But it was fun learning how it
works and it's limitations.

The main function is within the file so you can run via

python3 solve_schedule_ortools.py
"""

from absl import app
from absl import flags

import pandas as pd
from ortools.sat.python import cp_model
import pprint

FLAGS = flags.FLAGS
flags.DEFINE_string('input', 'tasks.csv', 'CSV file with tasks, priority and'
                    ' time they take in units of 30 minutes')
flags.DEFINE_string('output', 'schedule.csv', 'CSV file with schedule with the'
                    ' task, the start index, and the end index.')


def parse_input(file_name):
    tasks = pd.read_csv(FLAGS.input)
    # Parse the tasks into a hash
    tasks_d = {}
    max_priority = 0.0
    for index, task in tasks.iterrows():
        tasks_d[task['Index']] = {
            'priority': task['Priority'],
            'time': task['Time (30min)'],
        }
        max_priority = max(max_priority, float(task['Priority']))
    return max_priority, tasks_d


def print_schedule(solver, X):
    if len(X) == 0:
        raise Exception("Empty variable set")
    num_tasks = len(X)
    num_time_units = len(X[0])

    schedule = [0] * num_time_units
    for task in range(num_tasks):
        for unit in range(num_time_units):
            value = solver.Value(X[task][unit])
            if value != 0:
                if schedule[unit] != 0:
                    raise Exception("This unit is already scheduled")
                else:
                    schedule[unit] = task + 1
    return schedule


def main(argv):
    if len(argv) > 2:
        raise app.UsageError('Too many command-line arguments.')

    # Parse the tasks into a hash
    max_priority, tasks_d = parse_input(FLAGS.input)

    # Let's make these variables
    num_tasks = len(tasks_d)
    num_time_units = 16  # 8 hours of 30 min intervals

    # Model
    model = cp_model.CpModel()

    # Variables
    X = []  # variable is a list of indices to the tasks: [0, num_time_units]
    for task in range(num_tasks):
        t = []
        for time_unit in range(num_time_units):
            t.append(model.NewIntVar(0, 1, "X[{},{}]".format(task, time_unit)))
        X.append(t)

    # Constraints
    # For each task, we can't assign more than the number of units they would
    # take
    for idx, task_id in enumerate(tasks_d):
        model.Add(sum(X[idx][unit] for unit in
                      range(num_time_units)) <= tasks_d[task_id]['time'])
    # For each time unit, we can't assign more than 1 task at a time
    for unit in range(num_time_units):
        model.Add(sum(X[task][unit] for task in range(num_tasks)) <= 1)

    # Objective
    # So we want to minimize the amount of time units we have left to schedule,
    # the sum of priority we get when we do stuff, the amount of spaces left in
    # my agenda and we want to minimize switching tasks. To get that term, we
    # just count how many contiguous tasks we work on in X.
    objective_terms = []
    for idx, task_id in enumerate(tasks_d):
        slots_for_task = sum(X[idx][unit] for unit in range(num_time_units))
        # How many units of time are left
        objective_terms.append(3 * (tasks_d[task_id]['time'] - slots_for_task))
        # Sum of priorities
        objective_terms.append(slots_for_task * tasks_d[task_id]['priority'])

    # NOT POSSIBLE Number of contiguous tasks
    # for idx, task_id in enumerate(tasks_d):
    #   objective_terms.append(2*sum(1 if X[idx][unit] != X[idx][unit+1] \
    #                           else 0 for unit in range(0, num_time_units-1)))

    pprint.pprint(objective_terms)
    model.Minimize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Total cost = %i' % solver.ObjectiveValue())
        print(solver.ResponseStats())
        print(print_schedule(solver, X))


if __name__ == '__main__':
    app.run(main)
