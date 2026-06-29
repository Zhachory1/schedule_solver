"""
Main function to run the schedule solver with genetic algorithms

TODO(zhach):
1) change parse_input to output a list of protos
2) Implement main genetic algorithm code
3) Improve population selection/stopping criteria
"""

from absl import app
from absl import flags

import tasks_pb2

import matplotlib.pyplot as plt
import pandas as pd

import solve_schedule_ga as ssg
from schedule_output import write_schedule_csv

FLAGS = flags.FLAGS
flags.DEFINE_string('input', 'tasks.csv', 'CSV file with tasks, priority and '
                    'time they take in units of 30 minutes')
flags.DEFINE_string('output', 'schedule.csv', 'CSV file with schedule with the '
                    'task, the start index, and the end index.')


def parse_input(file_name):
    tasks = pd.read_csv(FLAGS.input)
    # Parse the tasks into a hash
    tasks_list = []
    for index, task in tasks.iterrows():
        temp_task = tasks_pb2.Task()
        temp_task.priority = task['Priority']
        temp_task.time_required = task['Time (15min)']
        temp_task.id = task['Index']
        tasks_list.append(temp_task)
    return tasks_list


def genes_to_task_ids(genes, tasks):
    return [tasks[gene].id if gene != -1 else -1 for gene in genes]


def main(argv):
    if len(argv) > 2:
        raise app.UsageError('Too many command-line arguments.')

    tasks = parse_input(FLAGS.input)
    genes = ssg.solve_schedule(tasks, schedule_size=8)
    write_schedule_csv(FLAGS.output, genes_to_task_ids(genes, tasks))
    print(f"Wrote schedule to {FLAGS.output}")

    return 0


if __name__ == '__main__':
    app.run(main)
