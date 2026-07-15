import math
import sqlite3
import hashlib
from datetime import datetime, timezone


CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL,
    time_required INTEGER NOT NULL,
    notes TEXT DEFAULT '',
    link TEXT DEFAULT '',
    description TEXT DEFAULT '',
    preference INTEGER DEFAULT 0,
    due_date INTEGER DEFAULT 0,
    source TEXT DEFAULT '',
    external_id TEXT DEFAULT ''
)
"""

CREATE_CALENDAR_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS calendar_events (
    id TEXT PRIMARY KEY,
    summary TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    description TEXT DEFAULT '',
    link TEXT DEFAULT '',
    task_id INTEGER
)
"""

TASK_COLUMNS = {
    "notes": "TEXT DEFAULT ''",
    "link": "TEXT DEFAULT ''",
    "description": "TEXT DEFAULT ''",
    "preference": "INTEGER DEFAULT 0",
    "due_date": "INTEGER DEFAULT 0",
    "source": "TEXT DEFAULT ''",
    "external_id": "TEXT DEFAULT ''",
}


def connect_sqlite(path):
    connection = sqlite3.connect(path)
    init_sqlite(connection)
    return connection


def init_sqlite(connection):
    connection.execute(CREATE_TASKS_TABLE)
    connection.execute(CREATE_CALENDAR_EVENTS_TABLE)
    _ensure_task_columns(connection)
    connection.commit()


def _ensure_task_columns(connection):
    existing = {row[1] for row in connection.execute("PRAGMA table_info(tasks)")}
    for column, definition in TASK_COLUMNS.items():
        if column not in existing:
            connection.execute(f"ALTER TABLE tasks ADD COLUMN {column} {definition}")


def save_tasks(connection, tasks):
    connection.executemany(
        """
        INSERT INTO tasks (
            id, title, priority, time_required, notes, link, description,
            preference, due_date, source, external_id
        )
        VALUES (
            :id, :title, :priority, :time_required, :notes, :link, :description,
            :preference, :due_date, :source, :external_id
        )
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            priority = excluded.priority,
            time_required = excluded.time_required,
            notes = excluded.notes,
            link = excluded.link,
            description = excluded.description,
            preference = excluded.preference,
            due_date = excluded.due_date,
            source = excluded.source,
            external_id = excluded.external_id
        """,
        [task_record(task) for task in tasks],
    )
    connection.commit()


def load_tasks(connection):
    rows = connection.execute(
        "SELECT id, title, priority, time_required, notes FROM tasks ORDER BY id"
    ).fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "priority": row[2],
            "time_required": row[3],
            "notes": row[4],
        }
        for row in rows
    ]


def load_task_records(connection):
    rows = connection.execute(
        """
        SELECT id, title, priority, time_required, notes, link, description,
               preference, due_date, source, external_id
        FROM tasks
        ORDER BY id
        """
    ).fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "priority": row[2],
            "time_required": row[3],
            "notes": row[4],
            "link": row[5],
            "description": row[6],
            "preference": row[7],
            "due_date": row[8],
            "source": row[9],
            "external_id": row[10],
        }
        for row in rows
    ]


def save_calendar_events(connection, events):
    connection.executemany(
        """
        INSERT INTO calendar_events (id, summary, start, end, description, link, task_id)
        VALUES (:id, :summary, :start, :end, :description, :link, :task_id)
        ON CONFLICT(id) DO UPDATE SET
            summary = excluded.summary,
            start = excluded.start,
            end = excluded.end,
            description = excluded.description,
            link = excluded.link,
            task_id = excluded.task_id
        """,
        [calendar_event_record(event) for event in events],
    )
    connection.commit()


def load_calendar_events(connection):
    rows = connection.execute(
        """
        SELECT id, summary, start, end, description, link, task_id
        FROM calendar_events
        ORDER BY start, id
        """
    ).fetchall()
    return [
        {
            "id": row[0],
            "summary": row[1],
            "start": row[2],
            "end": row[3],
            "description": row[4],
            "link": row[5],
            "task_id": row[6],
        }
        for row in rows
    ]


class SqliteDataInterface:
    def __init__(self, path_or_connection):
        if isinstance(path_or_connection, sqlite3.Connection):
            self.connection = path_or_connection
            init_sqlite(self.connection)
        else:
            self.connection = connect_sqlite(path_or_connection)

    def save_tasks(self, tasks):
        return save_tasks(self.connection, tasks)

    def load_tasks(self):
        return load_task_records(self.connection)

    def save_calendar_events(self, events):
        return save_calendar_events(self.connection, events)

    def load_calendar_events(self):
        return load_calendar_events(self.connection)


class KanboardInterface:
    def __init__(self, rpc_call, project_id=None):
        self.rpc_call = rpc_call
        self.project_id = project_id

    def load_tasks(self, project_id=None):
        target_project = self.project_id if project_id is None else project_id
        params = {} if target_project is None else {"project_id": target_project}
        return [kanboard_task_record(task) for task in self.rpc_call("getAllTasks", params)]


class GoogleTasksInterface:
    def __init__(self, service, tasklist="@default"):
        self.service = service
        self.tasklist = tasklist

    def load_tasks(self):
        items = []
        page_token = None
        while True:
            request = {
                "tasklist": self.tasklist,
                "showCompleted": False,
            }
            if page_token is not None:
                request["pageToken"] = page_token
            response = self.service.tasks().list(**request).execute()
            items.extend(response.get("items", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return [google_task_record(task) for task in items]


class GoogleCalendarInterface:
    def __init__(self, service, calendar_id="primary"):
        self.service = service
        self.calendar_id = calendar_id

    def load_events(self, time_min=None, time_max=None):
        request = {
            "calendarId": self.calendar_id,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        if time_min is not None:
            request["timeMin"] = time_min
        if time_max is not None:
            request["timeMax"] = time_max
        items = []
        page_token = None
        while True:
            page_request = dict(request)
            if page_token is not None:
                page_request["pageToken"] = page_token
            response = self.service.events().list(**page_request).execute()
            items.extend(response.get("items", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return [google_calendar_event_record(event) for event in items]

    def save_events(self, events):
        saved = []
        for event in events:
            saved.append(
                self.service.events().insert(
                    calendarId=self.calendar_id,
                    body=google_calendar_event_body(event),
                ).execute()
            )
        return saved


def task_record(task):
    raw_id = _value(task, "id", _value(task, "external_id", None))
    if raw_id in (None, ""):
        raise ValueError("task requires id or external_id")
    source = str(_value(task, "source", ""))
    external_id = str(_value(task, "external_id", raw_id))
    id_seed = f"{source}:{external_id}" if source else raw_id
    return {
        "id": _id_value(id_seed),
        "title": str(_value(task, "title", "")),
        "priority": _int_value(_value(task, "priority", 3), 3),
        "time_required": _int_value(_value(task, "time_required", 1), 1),
        "notes": str(_value(task, "notes", "")),
        "link": str(_value(task, "link", "")),
        "description": str(_value(task, "description", "")),
        "preference": _int_value(_value(task, "preference", 0), 0),
        "due_date": _int_value(_value(task, "due_date", 0), 0),
        "source": source,
        "external_id": external_id,
    }


def calendar_event_record(event):
    start = _event_time(_value(event, "start", ""))
    end = _event_time(_value(event, "end", ""))
    event_id = _value(event, "id", "") or _value(event, "external_id", "")
    if not event_id:
        event_id = f"{_value(event, 'summary', '')}:{start}:{end}"
    return {
        "id": str(event_id),
        "summary": str(_value(event, "summary", "")),
        "start": start,
        "end": end,
        "description": str(_value(event, "description", "")),
        "link": str(_value(event, "link", "")),
        "task_id": _nullable_int(_value(event, "task_id", None)),
    }


def kanboard_task_record(task):
    external_id = _value(task, "id", "")
    return task_record(
        {
            "id": external_id,
            "title": _value(task, "title", ""),
            "priority": _int_value(_value(task, "priority", 3), 3),
            "time_required": _time_units_from_hours(_value(task, "time_estimated", None)),
            "notes": _value(task, "description", ""),
            "description": _value(task, "description", ""),
            "link": _value(task, "url", ""),
            "due_date": _int_value(_value(task, "date_due", 0), 0),
            "source": "kanboard",
            "external_id": external_id,
        }
    )


def google_task_record(task):
    external_id = _value(task, "id", "")
    return task_record(
        {
            "id": external_id,
            "title": _value(task, "title", ""),
            "priority": 3,
            "time_required": 1,
            "notes": _value(task, "notes", ""),
            "description": _value(task, "notes", ""),
            "link": _value(task, "selfLink", ""),
            "due_date": _epoch_from_rfc3339(_value(task, "due", None)),
            "source": "google_tasks",
            "external_id": external_id,
        }
    )


def google_calendar_event_record(event):
    return calendar_event_record(
        {
            "id": _value(event, "id", ""),
            "summary": _value(event, "summary", ""),
            "start": _event_time(_value(event, "start", {})),
            "end": _event_time(_value(event, "end", {})),
            "description": _value(event, "description", ""),
            "link": _value(event, "htmlLink", ""),
        }
    )


def google_calendar_event_body(event):
    summary = _value(event, "summary", "")
    description = _value(event, "description", "")
    return {
        "summary": summary,
        "description": description,
        "start": _google_event_time_body(_value(event, "start", "")),
        "end": _google_event_time_body(_value(event, "end", "")),
    }


def _value(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _int_value(value, default):
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _nullable_int(value):
    if value in (None, ""):
        return None
    return _int_value(value, 0)


def _id_value(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        digest = hashlib.sha256(str(value).encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def _time_units_from_hours(value):
    if value in (None, ""):
        return 1
    try:
        return max(1, int(math.ceil(float(value) * 4)))
    except (TypeError, ValueError):
        return 1


def _epoch_from_rfc3339(value):
    if not value:
        return 0
    text = str(value).replace("Z", "+00:00")
    if len(text) == 10:
        text = f"{text}T00:00:00+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return 0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


def _event_time(value):
    if isinstance(value, dict):
        return value.get("dateTime") or value.get("date") or ""
    return str(value or "")


def _google_event_time_body(value):
    if isinstance(value, dict):
        return value
    text = str(value or "")
    if len(text) == 10 and text.count("-") == 2:
        return {"date": text}
    return {"dateTime": text}
