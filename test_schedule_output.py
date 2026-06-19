import csv
import tempfile
import unittest
from pathlib import Path

from schedule_output import contiguous_schedule_rows, write_schedule_csv


class ScheduleOutputTest(unittest.TestCase):
    def test_contiguous_rows_collapse_runs_and_skip_empty(self):
        rows = contiguous_schedule_rows([10, 10, -1, 20, 20, 10])

        self.assertEqual(
            rows,
            [
                {"task": 10, "start_index": 0, "end_index": 2},
                {"task": 20, "start_index": 3, "end_index": 5},
                {"task": 10, "start_index": 5, "end_index": 6},
            ],
        )

    def test_write_schedule_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "schedule.csv"
            write_schedule_csv(output, [1, 1, -1, 2])

            with output.open(newline="") as f:
                rows = list(csv.DictReader(f))

        self.assertEqual(rows[0], {"task": "1", "start_index": "0", "end_index": "2"})
        self.assertEqual(rows[1], {"task": "2", "start_index": "3", "end_index": "4"})


if __name__ == "__main__":
    unittest.main()
