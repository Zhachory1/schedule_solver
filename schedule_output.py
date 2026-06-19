import csv


def contiguous_schedule_rows(schedule):
    rows = []
    current_task = None
    start_index = None

    for index, task_id in enumerate(list(schedule) + [None]):
        if task_id == current_task:
            continue
        if current_task not in (None, -1, ""):
            rows.append(
                {
                    "task": current_task,
                    "start_index": start_index,
                    "end_index": index,
                }
            )
        current_task = task_id
        start_index = index

    return rows


def write_schedule_csv(output_path, schedule):
    rows = contiguous_schedule_rows(schedule)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["task", "start_index", "end_index"])
        writer.writeheader()
        writer.writerows(rows)
    return rows
