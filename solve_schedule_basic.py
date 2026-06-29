import random


def solve_random(tasks_d, num_time_units=16, seed=None):
    task_slots = []
    for task_id, task in tasks_d.items():
        task_slots.extend([task_id] * task["time"])

    rng = random.Random(seed)
    rng.shuffle(task_slots)
    schedule = task_slots[:num_time_units]
    schedule.extend([-1] * (num_time_units - len(schedule)))
    return schedule


def solve_priority_first(tasks_d, num_time_units=16):
    schedule = []
    sorted_tasks = sorted(
        tasks_d.items(),
        key=lambda item: (item[1]["priority"], item[1]["time"], item[0]),
        reverse=True,
    )

    for task_id, task in sorted_tasks:
        open_slots = num_time_units - len(schedule)
        if open_slots == 0:
            break
        schedule.extend([task_id] * min(task["time"], open_slots))

    schedule.extend([-1] * (num_time_units - len(schedule)))
    return schedule
