import tempfile
import unittest
from pathlib import Path

from data_interfaces import connect_sqlite, load_tasks, save_tasks


class SqliteTaskInterfaceTest(unittest.TestCase):
    def test_save_and_load_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            connection = connect_sqlite(Path(tmp) / "tasks.db")
            save_tasks(
                connection,
                [
                    {
                        "id": 1,
                        "title": "Homework",
                        "priority": 2,
                        "time_required": 6,
                        "notes": "chapter 1",
                    }
                ],
            )

            self.assertEqual(
                load_tasks(connection),
                [
                    {
                        "id": 1,
                        "title": "Homework",
                        "priority": 2,
                        "time_required": 6,
                        "notes": "chapter 1",
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
