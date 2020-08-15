"""
Main function to run the schedule solver with genetic algorithms

TODO(zhach):
1) Create task proto
2) change parse_input to output a list of protos
3) Implement main genetic algorithm code
4) Output tasks and time units that are left
5) suck butts
"""

from absl import app
from absl import flags

import tasks_pb2

import pandas as pd

FLAGS = flags.FLAGS
flags.DEFINE_string('input', 'tasks.csv', 'CSV file with tasks, priority and'
                    ' time they take in units of 30 minutes')
flags.DEFINE_string('output', 'schedule.csv', 'CSV file with schedule with the'
                    ' task, the start index, and the end index.')


def parse_input(file_name):
    tasks = pd.read_csv(FLAGS.input)
    # Parse the tasks into a hash
    tasks_d = {}
    for index, task in tasks.iterrows():
        temp_task = tasks_pb2.Task()
        temp_task.priority = task['Priority']
        temp_task.time_required = task['Time (15 min)']
        temp_task.id = task['Index']
        tasks_d[task['Index']] = temp_task
    return tasks_d


def main(argv):
    if len(argv) > 2:
        raise app.UsageError('Too many command-line arguments.')

    # Parse the tasks into a hash
    tasks_d = parse_input(FLAGS.input)

    print("I'm working")
    return 0


if __name__ == '__main__':
    app.run(main)
