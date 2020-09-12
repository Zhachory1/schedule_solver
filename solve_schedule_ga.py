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
import tasks_pb2

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
    return Counter(results)


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
            random_task = np.random.choice(list(time_units_left.keys()))
            rand_schedule.append(random_task)
            time_units_left[random_task] -= 1
            if time_units_left[random_task] == 0:
                del time_units_left[random_task]
    return rand_schedule


def crossover(genes_a, genes_b):
    # Go through both genes. If values at the same index are the same, keep.
    # Else, pass.
    crossover = []
    for idx in range(len(genes_a)):
        if genes_b[idx] == genes_a[idx]:
            crossover.append(genes_a[idx])
        else:
            crossover.append(-1)
    return crossover


class Citizen:
    def __init__(self, genes, c_limit):
        self._genes = genes
        self._concieve_limit = c_limit

    def get_genes(self):
        return self._genes

    def make_child(self, other_parent):
        pass


def fitness(schedule, tasks, coeff=[1.0, 1.0, 1.0, 1.0]):
    fitness = 0
    fitness_vals = fitness_impl(schedule, tasks)
    for idx, val in enumerate(fitness_vals):
        fitness += coeff[idx] * val
    return fitness

def fitness_impl(schedule, tasks):
    '''Finding the fitness of a schedule
    There's a few things I'm adding into this function:
    1) It's better to have a task completed
    2) I rather not context switch between tasks within a day
    3) I rather have a full day of things
    4) I prefer completed higher priorities before lower priorities

    The function will be an additive score where each function will return a
    value from [0, 1]

    Args:
        X: the schedule; an array of numbers where the value corresponds to an
            index in the tasks dictionary
        tasks: dict hold task index and task proto for quick access to data
    Returns:
        A double score of how fit the schedule it
    '''
    final_fitness = []

    # First make completed tasks value. sum(completed_tasks)/sum(tasks_done)
    schedule_counter = Counter(schedule)
    sum_completed = 0
    for task in schedule_counter:
        if task != -1 and schedule_counter[task] == tasks[task].time_required:
            sum_completed +=1
    final_fitness.append(float(sum_completed)/len(schedule_counter))

    # Next, context switches. This can be a negative exponential function, where
    # x [0, inf) is the number of context switches.
    #   f(x) =  2^(-x/10)
    context_switches = 0
    last_task = schedule[0]
    for slot in range(1, len(schedule)):
        current_task = schedule[slot]
        if current_task == -1:
            continue
        elif last_task != current_task:
            context_switches += 1
        last_task = current_task
    final_fitness.append(pow(2, -context_switches/float(10)))

    # Next, I penalize for not having a full day. So I just count empty slots
    # in my schedule
    final_fitness.append(1-(schedule_counter[-1]/len(schedule)))

    # Finally, I add up the priotiies of my tasks, and divide by the worst case,
    # all my tasks having low priority. Then I push that through my 1-g(x)
    sum_priorities = 0
    for task in schedule_counter:
        if task == -1:
            sum_priorities += tasks_pb2.Task.Priority.LOW
        else:
            sum_priorities += tasks[task].priority
    final_fitness.append(1 - (\
        sum_priorities/float(tasks_pb2.Task.Priority.LOW*len(schedule_counter))
    ))

    return final_fitness


def selection(population):
    pass


def stopping_criteria():
    pass
