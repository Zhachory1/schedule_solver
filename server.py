import csv
from pathlib import Path

from flask import Flask, render_template

from schedule_output import contiguous_schedule_rows

app = Flask(__name__)


def read_tasks(path="tasks.csv"):
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))


def build_preview_schedule(tasks, num_time_units=16):
    schedule = []
    for task in tasks:
        task_id = int(task["Index"])
        task_time = int(task["Time (15min)"])
        open_slots = num_time_units - len(schedule)
        if open_slots == 0:
            break
        schedule.extend([task_id] * min(task_time, open_slots))
    schedule.extend([-1] * (num_time_units - len(schedule)))
    return schedule


def remaining_tasks(tasks, schedule):
    remaining = []
    for task in tasks:
        task_id = int(task["Index"])
        original_time = int(task["Time (15min)"])
        remaining_time = max(0, original_time - schedule.count(task_id))
        remaining.append({**task, "Remaining (15min)": remaining_time})
    return remaining


@app.route('/')
def index():
    tasks = read_tasks()
    schedule = build_preview_schedule(tasks)
    return render_template(
        'index.html',
        tasks=tasks,
        schedule_rows=contiguous_schedule_rows(schedule),
        remaining_tasks=remaining_tasks(tasks, schedule),
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
