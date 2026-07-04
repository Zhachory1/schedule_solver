import sqlite3


CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL,
    time_required INTEGER NOT NULL,
    notes TEXT DEFAULT ''
)
"""


def connect_sqlite(path):
    connection = sqlite3.connect(path)
    init_sqlite(connection)
    return connection


def init_sqlite(connection):
    connection.execute(CREATE_TASKS_TABLE)
    connection.commit()


def save_tasks(connection, tasks):
    connection.executemany(
        """
        INSERT INTO tasks (id, title, priority, time_required, notes)
        VALUES (:id, :title, :priority, :time_required, :notes)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            priority = excluded.priority,
            time_required = excluded.time_required,
            notes = excluded.notes
        """,
        tasks,
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
