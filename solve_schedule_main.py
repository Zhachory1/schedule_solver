"""
Main function to run the schedule solver with genetic algorithms

TODO(zhach):
1) change parse_input to output a list of protos
2) Implement main genetic algorithm code
3) Output tasks and time units that are left
4) suck butts
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
    tasks = []
    for index, task in tasks.iterrows():
        temp_task = tasks_pb2.Task()
        temp_task.priority = task['Priority']
        temp_task.time_required = task['Time (15 min)']
        temp_task.id = task['Index']
        tasks.append(temp_task)
    return tasks


def main(argv):
    if len(argv) > 2:
        raise app.UsageError('Too many command-line arguments.')

    # Parse the tasks into a hash
    _ = parse_input(FLAGS.input)

    print("I'm working")
    return 0


if __name__ == '__main__':
    app.run(main)
