import tempfile
import unittest
from pathlib import Path

from data_interfaces import (
    GoogleCalendarInterface,
    GoogleTasksInterface,
    KanboardInterface,
    SqliteDataInterface,
    connect_sqlite,
    load_calendar_events,
    load_task_records,
    load_tasks,
    save_calendar_events,
    save_tasks,
)


class ExecuteResponse:
    def __init__(self, response):
        self.response = response

    def execute(self):
        return self.response


class FakeTaskService:
    def __init__(self, responses):
        self.responses = responses if isinstance(responses, list) else [responses]
        self.list_kwargs = []

    def tasks(self):
        return self

    def list(self, **kwargs):
        self.list_kwargs.append(kwargs)
        return ExecuteResponse(self.responses.pop(0))


class FakeCalendarEvents:
    def __init__(self, responses):
        self.responses = responses if isinstance(responses, list) else [responses]
        self.list_kwargs = []
        self.inserted = []

    def list(self, **kwargs):
        self.list_kwargs.append(kwargs)
        return ExecuteResponse(self.responses.pop(0))

    def insert(self, **kwargs):
        self.inserted.append(kwargs)
        return ExecuteResponse({"id": "created"})


class FakeCalendarService:
    def __init__(self, events):
        self.events_resource = events

    def events(self):
        return self.events_resource


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

    def test_sqlite_interface_loads_full_task_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            interface = SqliteDataInterface(Path(tmp) / "tasks.db")
            interface.save_tasks(
                [
                    {
                        "id": 2,
                        "title": "Call doctor",
                        "priority": 1,
                        "time_required": 1,
                        "description": "foot doctor",
                        "link": "https://example.com",
                    }
                ]
            )

            self.assertEqual(load_task_records(interface.connection)[0]["source"], "")
            self.assertEqual(interface.load_tasks()[0]["link"], "https://example.com")

    def test_sourced_numeric_task_ids_do_not_overwrite_local_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            connection = connect_sqlite(Path(tmp) / "tasks.db")
            save_tasks(
                connection,
                [
                    {
                        "id": 42,
                        "title": "Local task",
                        "priority": 3,
                        "time_required": 1,
                    },
                    {
                        "id": "42",
                        "title": "Kanboard task",
                        "priority": 2,
                        "time_required": 2,
                        "source": "kanboard",
                        "external_id": "42",
                    },
                ],
            )

            self.assertEqual(len(load_task_records(connection)), 2)

    def test_save_and_load_calendar_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            connection = connect_sqlite(Path(tmp) / "tasks.db")
            save_calendar_events(
                connection,
                [
                    {
                        "id": "event-1",
                        "summary": "Homework",
                        "start": "2026-07-14T09:00:00Z",
                        "end": "2026-07-14T09:30:00Z",
                        "task_id": 1,
                    }
                ],
            )

            self.assertEqual(
                load_calendar_events(connection),
                [
                    {
                        "id": "event-1",
                        "summary": "Homework",
                        "start": "2026-07-14T09:00:00Z",
                        "end": "2026-07-14T09:30:00Z",
                        "description": "",
                        "link": "",
                        "task_id": 1,
                    }
                ],
            )


class KanboardInterfaceTest(unittest.TestCase):
    def test_load_tasks_maps_kanboard_tasks(self):
        calls = []

        def rpc_call(method, params):
            calls.append((method, params))
            return [
                {
                    "id": "42",
                    "title": "Review board",
                    "priority": "2",
                    "time_estimated": "1.5",
                    "description": "triage",
                    "url": "https://kanboard/task/42",
                    "date_due": "1800000000",
                }
            ]

        tasks = KanboardInterface(rpc_call, project_id=7).load_tasks()

        self.assertEqual(calls, [("getAllTasks", {"project_id": 7})])
        self.assertNotEqual(tasks[0]["id"], 42)
        self.assertEqual(tasks[0]["external_id"], "42")
        self.assertEqual(tasks[0]["time_required"], 6)
        self.assertEqual(tasks[0]["source"], "kanboard")


class GoogleTasksInterfaceTest(unittest.TestCase):
    def test_load_tasks_maps_google_tasks(self):
        service = FakeTaskService(
            [
                {
                    "items": [
                        {
                            "id": "google-task-1",
                            "title": "Inbox task",
                            "notes": "from Google Tasks",
                            "selfLink": "https://tasks/task/1",
                            "due": "2026-07-14T00:00:00.000Z",
                        }
                    ],
                    "nextPageToken": "page-2",
                },
                {
                    "items": [
                        {
                            "id": "google-task-2",
                            "title": "Second task",
                        }
                    ]
                },
            ]
        )

        tasks = GoogleTasksInterface(service, tasklist="work").load_tasks()

        self.assertEqual(service.list_kwargs[0], {"tasklist": "work", "showCompleted": False})
        self.assertEqual(service.list_kwargs[1]["pageToken"], "page-2")
        self.assertEqual([task["title"] for task in tasks], ["Inbox task", "Second task"])
        self.assertEqual(tasks[0]["source"], "google_tasks")
        self.assertEqual(tasks[0]["external_id"], "google-task-1")
        self.assertGreater(tasks[0]["due_date"], 0)


class GoogleCalendarInterfaceTest(unittest.TestCase):
    def test_load_and_save_events(self):
        events = FakeCalendarEvents(
            [
                {
                    "items": [
                        {
                            "id": "event-1",
                            "summary": "Focus block",
                            "start": {"dateTime": "2026-07-14T09:00:00Z"},
                            "end": {"dateTime": "2026-07-14T09:30:00Z"},
                            "htmlLink": "https://calendar/event/1",
                        }
                    ],
                    "nextPageToken": "page-2",
                },
                {
                    "items": [
                        {
                            "id": "event-2",
                            "summary": "Second block",
                            "start": {"date": "2026-07-15"},
                            "end": {"date": "2026-07-16"},
                        }
                    ]
                },
            ]
        )
        interface = GoogleCalendarInterface(FakeCalendarService(events), calendar_id="work")

        loaded = interface.load_events(time_min="2026-07-14T00:00:00Z")
        saved = interface.save_events(
            [
                {
                    "summary": "Task block",
                    "start": "2026-07-14T10:00:00Z",
                    "end": "2026-07-14T10:30:00Z",
                },
                {
                    "summary": "All-day block",
                    "start": "2026-07-15",
                    "end": "2026-07-16",
                },
            ]
        )

        self.assertEqual(events.list_kwargs[0]["calendarId"], "work")
        self.assertEqual(events.list_kwargs[1]["pageToken"], "page-2")
        self.assertEqual(loaded[0]["start"], "2026-07-14T09:00:00Z")
        self.assertEqual(loaded[1]["start"], "2026-07-15")
        self.assertEqual(
            events.inserted[0]["body"]["start"],
            {"dateTime": "2026-07-14T10:00:00Z"},
        )
        self.assertEqual(events.inserted[1]["body"]["start"], {"date": "2026-07-15"})
        self.assertEqual(saved, [{"id": "created"}, {"id": "created"}])


if __name__ == "__main__":
    unittest.main()
