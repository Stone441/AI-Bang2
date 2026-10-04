"""SQLite local store; serial transaction boundaries, not a production DB role boundary."""
import copy
import json
import sqlite3
import threading
from contextlib import contextmanager
from .contracts import now


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


class Store:
    def __init__(self, path=':memory:'):
        self.lock=threading.RLock()
        self.db=sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS resources(id TEXT PRIMARY KEY, version INTEGER, active INTEGER, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS versions(id TEXT, version INTEGER, body TEXT NOT NULL, PRIMARY KEY(id,version));
        CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, actor TEXT NOT NULL, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(event_id INTEGER PRIMARY KEY, state TEXT, attempts INTEGER, body TEXT);
        CREATE TABLE IF NOT EXISTS sync(source TEXT PRIMARY KEY, cursor INTEGER, checked_at TEXT, health TEXT);
        CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'append only'); END;
        CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'append only'); END;
        ''')
        self.db.set_authorizer(self._authorize_sql)

    @staticmethod
    def _authorize_sql(action, arg1, arg2, database, trigger):
        if action in (sqlite3.SQLITE_DROP_TABLE,sqlite3.SQLITE_DROP_TRIGGER,sqlite3.SQLITE_ALTER_TABLE,sqlite3.SQLITE_ATTACH):
            return sqlite3.SQLITE_DENY
        if arg1=='audit' and action in (sqlite3.SQLITE_UPDATE,sqlite3.SQLITE_DELETE):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    @contextmanager
    def transaction(self):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                yield self.db
                self.db.execute('COMMIT')
            except BaseException:
                self.db.execute('ROLLBACK')
                raise

    def initialize(self, world):
        with self.transaction() as db:
            if db.execute('SELECT count(*) FROM resources').fetchone()[0]:
                return
            for raw in world.resources.values():
                r=copy.deepcopy(raw); r['indexed_at']=now()
                db.execute('INSERT INTO resources VALUES(?,?,?,?)',(r['id'],r['version'],r['active'],canonical(r)))
                db.execute('INSERT INTO versions VALUES(?,?,?)',(r['id'],r['version'],canonical(r)))
            for source in ('confluence','jira','slack','drive'):
                db.execute('INSERT INTO sync VALUES(?,?,?,?)',(source,0,now(),'ready'))

    def resources(self):
        with self.lock:
            return [json.loads(r[0]) for r in self.db.execute('SELECT body FROM resources WHERE active=1 ORDER BY id')]

    def get(self, rid):
        with self.lock:
            row=self.db.execute('SELECT body FROM resources WHERE id=? AND active=1',(rid,)).fetchone()
            return json.loads(row[0]) if row else None

    def save_run(self, rid, actor, response):
        with self.transaction() as db:
            db.execute('INSERT INTO runs VALUES(?,?,?)',(rid,actor,canonical(response)))

    def run(self, rid, actor):
        with self.lock:
            r=self.db.execute('SELECT body FROM runs WHERE id=? AND actor=?',(rid,actor)).fetchone()
            return json.loads(r[0]) if r else None

    def history(self, actor):
        with self.lock:
            return [json.loads(r[0]) for r in self.db.execute('SELECT body FROM runs WHERE actor=? ORDER BY rowid DESC LIMIT 20',(actor,))]
