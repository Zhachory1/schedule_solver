# Lint as: python3
"""
Simple schedule creator with a genetic algorithm

TODO(zhach):
1) Make random valid genes
2) Implement crossover
3) Implement conception
4) Implement fitness score
5) Implement selection
6) Implement stopping criteria
7) Change task cotainer to a dictionary
7) Tests
"""

from collections import Counter
import numpy as np
import functools


def is_schedule_possible(schedule, tasks):
    # Make sure of the following things:
    # 1) Make sure there are no invalid tasks
    # 2) Make sure no task is scheduled for more time units than it should take
    cnts = Counter(schedule)
    for idx, task_cnt in cnts.items():
        if idx > len(tasks):
            return False
        if idx < 0:
            continue
        if task_cnt > tasks[idx].time_required:
            return False
    return True


def get_counter_from_tasktime(tasks):
    # Converts the list of TASKS into a Counter object where the index is
    # the index of the task
    results = {}
    for idx, task in enumerate(tasks):
        results[idx] = task.time_required
    return results


def find_random_empty_unit(schedule):
    # To include randomness, we will choose a random starting point; then we
    # we will go through the array, wrapping to the beginning to find an empty
    # unit. Will return -1 if we can't find an empty slot
    start = int(np.floor(np.random.random() * (len(schedule) - 1)))
    pos = start + 1
    while pos != start:
        if pos >= len(schedule):
            pos = 0
        if schedule[pos] == -1:
            return pos
        pos += 1
    return -1


def find_random_filled_unit(schedule):
    # To include randomness, we will choose a random starting point; then we
    # we will go through the array, wrapping to the beginning to find an empty
    # unit. Will return -1 if there are no filled spots
    start = int(np.floor(np.random.random() * (len(schedule) - 1)))
    pos = start + 1
    while pos != start:
        if pos >= len(schedule):
            pos = 0
        if schedule[pos] != -1:
            return pos
        pos += 1
    return -1


def add_time_unit(schedule, tasks, index):
    time_units_left = Counter(schedule)
    time_units_left.subtract(get_counter_from_tasktime(tasks))
    for elem, cnt in time_units_left.items():
        if int(elem) > 0:
            schedule[index] = int(elem)
            break
    return schedule


def remove_time_unit(schedule, tasks, index):
    schedule[index] = -1
    return schedule


def mutate(schedule, tasks, force_add=None):
    if not schedule:
        return []
    # if force_add equals true, add task time unit; if false remove time
    # unit; randomly choose to add or remove tasks; add to empty slot; remove
    # random time slot for a random task
    force_on = type(force_add) == bool
    if (force_on and force_add) or \
       (not force_on and np.random.random() < 0.5):
        index = find_random_empty_unit(schedule)
        if index != -1:
            schedule = add_time_unit(schedule, tasks, index)
    else:
        index = find_random_filled_unit(schedule)
        if index != -1:
            schedule = remove_time_unit(schedule, tasks, index)
    return schedule


def make_random_genes(tasks, schedule_size):
    # for loop; get random task or -1; if we have more spaces in it, go ahead
    # and add it; keeping going until we get schedule_size
    rand_schedule = []
    # The idx here should just be from [0, num_of_tasks)
    time_units_left = dict(get_counter_from_tasktime(tasks))
    while len(rand_schedule) < schedule_size:
        if np.random.random() < 0.2 or time_units_left == {}:
            rand_schedule.append(-1)
        else:
            random_task = int(np.floor(np.random.random() * len(time_units_left)))
            rand_schedule.append(random_task)
            time_units_left[random_task] -= 1
            if time_units_left[random_task] == 0:
                del time_units_left[random_task]
    return rand_schedule


def crossover(genes_a, genes_b):
    # Go through the schedule in both schedules; start with a; go through
    # until we stop working on a task; switch to b; keep adding until we
    # stop working on a task; go back to a; repeat until we hit the end
    # of the schedule; if we run out of time for 1 task, just use the
    # other schedule; if the other schedule also uses the same task, set
    # units to -1
    return genes_a


class Citizen:
    def __init__(self, genes, c_limit):
        self._genes = genes
        self._concieve_limit = c_limit

    def get_genes(self):
        return self._genes

    def make_child(self, other_parent):
        pass


def fitness(X):
    # There's a few things I'm adding into this function:
    # 1) It's better to have a task completed
    # 2) I rather not context switch between tasks within a day
    # 3) I rather have a full day of things
    # 4) I prefer completed higher priorities before lower prioritys
    pass


def selection(population):
    pass


def stopping_criteria():
    pass
