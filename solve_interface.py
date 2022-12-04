from collections import Counter
import numpy as np
import tasks_pb2

class SolverInterface:
    # Tasks are a list of tasks defined in the tasks.proto file.
    # The schedule will be defined by a list of task ids, where each 
    # element is a 30 minute increment. 
    # num_of_increments = default 12 hours
    def __init__(self, tasks=None, num_of_increments=24):
        self.tasks = tasks
        self.schedule = [-1]*num_of_increments

    def get_schedule(self):
        return self.schedule

    def set_tasks(self, tasks):
        self.tasks = tasks

    def solve_schedule(self):
        self.schedule = self.__solve_impl()
    
    # Please implement for your classes
    def __solve_impl(self):
        raise NotImplementedError
    
    # Update the task list with the tasks you have done with the schedule.
    # If the schedule is not filled, it does nothing.
    def update_tasks(self):
        schedule_counter = Counter(self.schedule)
        task_counter = self.__get_counter_from_tasktime()
        task_counter.subtract(schedule_counter)
        for task in self.tasks:
            if task.id in task_counter
                task.time_required -= task_counter[task.id]


    def __find_random_filled_unit(schedule):
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
    
    def __get_counter_from_tasktime(self):
        # Converts the list of TASKS into a Counter object where the index is
        # the index of the task
        results = {}
        for _, task in enumerate(self.tasks):
            results[task.id] = task.time_required
        return Counter(results)


    def __add_time_unit(self, task_id, index):
        task_counter = self.get_counter_from_tasktime()
        if task_counter[task_id] > 0 and schedule[index] == -1:
            schedule[index] = task_id


    def __remove_time_unit(schedule, tasks, index):
        schedule[index] = -1
        return schedule
    
    def __find_random_empty_unit(schedule):
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