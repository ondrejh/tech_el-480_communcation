"""SQLite storage: latest value of everything, plus a history of changes.

Only changes are written to the history, and writes are batched to limit SD card
wear. A power cut can lose up to one flush interval of data.
"""

import sqlite3
from collections import Counter

SCHEMA = """
CREATE TABLE IF NOT EXISTS current_values (
    source       TEXT    NOT NULL,
    address      INTEGER NOT NULL,
    selector     INTEGER NOT NULL,
    param        INTEGER NOT NULL,
    value        INTEGER NOT NULL,
    first_seen   REAL    NOT NULL,
    last_seen    REAL    NOT NULL,
    last_changed REAL    NOT NULL,
    PRIMARY KEY (source, address, selector, param)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS value_changes (
    id       INTEGER PRIMARY KEY,
    ts       REAL    NOT NULL,
    source   TEXT    NOT NULL,
    address  INTEGER NOT NULL,
    selector INTEGER NOT NULL,
    param    INTEGER NOT NULL,
    value    INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS value_changes_key
    ON value_changes (param, source, address, selector, ts);

CREATE TABLE IF NOT EXISTS reader_stats (
    hour  INTEGER NOT NULL,
    kind  TEXT    NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (hour, kind)
) WITHOUT ROWID;
"""


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.db.executescript(SCHEMA)
        self.db.commit()

        # key -> [value, first_seen, last_seen, last_changed]
        self.current = {
            tuple(row[:4]): list(row[4:])
            for row in self.db.execute("""
                SELECT source, address, selector, param,
                       value, first_seen, last_seen, last_changed
                FROM current_values""")
        }
        self.dirty = set()
        self.changes = []
        self.stats = Counter()

    def record_frame(self, frame, ts):
        self.count(f"ok_{frame.source}", ts)
        for selector, param, value in frame.values:
            key = (frame.source, frame.address, selector, param)
            entry = self.current.get(key)
            if entry is None:
                self.current[key] = [value, ts, ts, ts]
                self.changes.append((ts, *key, value))
            else:
                if entry[0] != value:
                    entry[0] = value
                    entry[3] = ts
                    self.changes.append((ts, *key, value))
                entry[2] = ts
            self.dirty.add(key)

    def count(self, kind, ts):
        self.stats[(int(ts // 3600) * 3600, kind)] += 1

    def flush(self):
        with self.db:
            self.db.executemany(
                """INSERT INTO value_changes (ts, source, address, selector, param, value)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                self.changes)
            self.db.executemany(
                """INSERT OR REPLACE INTO current_values
                   (source, address, selector, param,
                    value, first_seen, last_seen, last_changed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [(*key, *self.current[key]) for key in self.dirty])
            self.db.executemany(
                """INSERT INTO reader_stats (hour, kind, count) VALUES (?, ?, ?)
                   ON CONFLICT (hour, kind) DO UPDATE SET count = count + excluded.count""",
                [(hour, kind, n) for (hour, kind), n in self.stats.items()])
        self.changes.clear()
        self.dirty.clear()
        self.stats.clear()

    def close(self):
        self.flush()
        self.db.close()
