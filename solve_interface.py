from collections import Counter
import random


class SolverInterface:
    # Tasks are a list of tasks defined in tasks.proto.
    # The schedule is a list of task ids, one per time increment.
    def __init__(self, tasks=None, num_of_increments=24):
        self.tasks = tasks or []
        self.schedule = [-1] * num_of_increments

    def get_schedule(self):
        return self.schedule

    def set_tasks(self, tasks):
        self.tasks = tasks or []

    def solve_schedule(self):
        self.schedule = self._solve_impl()
        return self.schedule

    def _solve_impl(self):
        raise NotImplementedError

    def update_tasks(self):
        schedule_counter = Counter(x for x in self.schedule if x != -1)
        for task in self.tasks:
            task.time_required = max(0, task.time_required - schedule_counter.get(task.id, 0))

    def _get_counter_from_tasktime(self):
        return Counter({task.id: task.time_required for task in self.tasks})

    def _add_time_unit(self, task_id, index):
        task_counter = self._get_counter_from_tasktime()
        if task_counter[task_id] > self.schedule.count(task_id) and self.schedule[index] == -1:
            self.schedule[index] = task_id
        return self.schedule

    def _remove_time_unit(self, index):
        self.schedule[index] = -1
        return self.schedule

    @staticmethod
    def _find_random_filled_unit(schedule):
        if not schedule:
            return -1
        start = random.randrange(len(schedule))
        pos = start
        while True:
            if schedule[pos] != -1:
                return pos
            pos = (pos + 1) % len(schedule)
            if pos == start:
                return -1

    @staticmethod
    def _find_random_empty_unit(schedule):
        if not schedule:
            return -1
        start = random.randrange(len(schedule))
        pos = start
        while True:
            if schedule[pos] == -1:
                return pos
            pos = (pos + 1) % len(schedule)
            if pos == start:
                return -1
