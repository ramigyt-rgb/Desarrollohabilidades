import sqlite3
from pathlib import Path
from datetime import datetime, date

DB_PATH = Path(__file__).with_name("learning_os.db")

def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with _conn() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS profiles(
            user_id INTEGER PRIMARY KEY,
            active_skill TEXT,
            daily_minutes INTEGER DEFAULT 30,
            target TEXT DEFAULT '',
            experience TEXT DEFAULT 'Principiante',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS lesson_progress(
            user_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            module_idx INTEGER NOT NULL,
            lesson_idx INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TEXT,
            PRIMARY KEY(user_id,skill,module_idx,lesson_idx)
        );
        CREATE TABLE IF NOT EXISTS sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            quality INTEGER NOT NULL,
            notes TEXT DEFAULT '',
            xp INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS exams(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            module_idx INTEGER NOT NULL,
            score REAL NOT NULL,
            xp INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS checkins(
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            skill TEXT NOT NULL,
            energy INTEGER NOT NULL,
            focus INTEGER NOT NULL,
            intention TEXT DEFAULT '',
            PRIMARY KEY(user_id, day, skill)
        );
        CREATE TABLE IF NOT EXISTS goals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            text TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tutor_messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

def create_user(username, display_name, password_hash):
    try:
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO users(username,display_name,password_hash,created_at) VALUES(?,?,?,?)",
                (username.strip().lower(), display_name.strip(), password_hash, datetime.now().isoformat())
            )
            uid = cur.lastrowid
            con.execute("INSERT INTO profiles(user_id) VALUES(?)", (uid,))
            return uid
    except sqlite3.IntegrityError:
        return None

def get_user(username):
    with _conn() as con:
        row = con.execute("SELECT * FROM users WHERE username=?", (username.strip().lower(),)).fetchone()
        return dict(row) if row else None

def get_profile(user_id):
    with _conn() as con:
        row = con.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else {}

def save_profile(user_id, skill, daily_minutes, target, experience):
    with _conn() as con:
        con.execute("""
        INSERT INTO profiles(user_id,active_skill,daily_minutes,target,experience)
        VALUES(?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            active_skill=excluded.active_skill,
            daily_minutes=excluded.daily_minutes,
            target=excluded.target,
            experience=excluded.experience
        """, (user_id, skill, daily_minutes, target, experience))

def set_active_skill(user_id, skill):
    with _conn() as con:
        con.execute("UPDATE profiles SET active_skill=? WHERE user_id=?", (skill, user_id))

def lesson_rows(user_id, skill):
    with _conn() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM lesson_progress WHERE user_id=? AND skill=?", (user_id, skill)
        ).fetchall()]

def set_lesson_completed(user_id, skill, module_idx, lesson_idx, completed=True):
    with _conn() as con:
        con.execute("""
        INSERT INTO lesson_progress(user_id,skill,module_idx,lesson_idx,completed,completed_at)
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(user_id,skill,module_idx,lesson_idx) DO UPDATE SET
            completed=excluded.completed,
            completed_at=excluded.completed_at
        """, (user_id, skill, module_idx, lesson_idx, int(completed),
              datetime.now().isoformat() if completed else None))

def add_session(user_id, skill, minutes, quality, notes, xp):
    with _conn() as con:
        con.execute("""
        INSERT INTO sessions(user_id,skill,minutes,quality,notes,xp,created_at)
        VALUES(?,?,?,?,?,?,?)
        """, (user_id, skill, minutes, quality, notes, xp, datetime.now().isoformat()))

def sessions(user_id, skill=None):
    with _conn() as con:
        if skill:
            rows = con.execute("SELECT * FROM sessions WHERE user_id=? AND skill=? ORDER BY created_at DESC",
                               (user_id, skill)).fetchall()
        else:
            rows = con.execute("SELECT * FROM sessions WHERE user_id=? ORDER BY created_at DESC",
                               (user_id,)).fetchall()
        return [dict(r) for r in rows]

def save_exam(user_id, skill, module_idx, score, xp):
    with _conn() as con:
        con.execute("INSERT INTO exams(user_id,skill,module_idx,score,xp,created_at) VALUES(?,?,?,?,?,?)",
                    (user_id, skill, module_idx, score, xp, datetime.now().isoformat()))

def exams(user_id, skill=None):
    with _conn() as con:
        if skill:
            rows = con.execute("SELECT * FROM exams WHERE user_id=? AND skill=? ORDER BY created_at DESC",
                               (user_id, skill)).fetchall()
        else:
            rows = con.execute("SELECT * FROM exams WHERE user_id=? ORDER BY created_at DESC",
                               (user_id,)).fetchall()
        return [dict(r) for r in rows]

def upsert_checkin(user_id, skill, energy, focus, intention):
    with _conn() as con:
        con.execute("""
        INSERT INTO checkins(user_id,day,skill,energy,focus,intention)
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(user_id,day,skill) DO UPDATE SET
            energy=excluded.energy, focus=excluded.focus, intention=excluded.intention
        """, (user_id, date.today().isoformat(), skill, energy, focus, intention))

def checkins(user_id, skill=None):
    with _conn() as con:
        if skill:
            rows = con.execute("SELECT * FROM checkins WHERE user_id=? AND skill=? ORDER BY day DESC",
                               (user_id, skill)).fetchall()
        else:
            rows = con.execute("SELECT * FROM checkins WHERE user_id=? ORDER BY day DESC",
                               (user_id,)).fetchall()
        return [dict(r) for r in rows]

def add_goal(user_id, skill, text):
    with _conn() as con:
        con.execute("INSERT INTO goals(user_id,skill,text,created_at) VALUES(?,?,?,?)",
                    (user_id, skill, text.strip(), datetime.now().isoformat()))

def goals(user_id, skill):
    with _conn() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM goals WHERE user_id=? AND skill=? ORDER BY done, id DESC", (user_id, skill)
        ).fetchall()]

def toggle_goal(goal_id, done):
    with _conn() as con:
        con.execute("UPDATE goals SET done=? WHERE id=?", (int(done), goal_id))

def tutor_history(user_id, skill, limit=16):
    with _conn() as con:
        rows = con.execute("""
            SELECT role,content,created_at FROM tutor_messages
            WHERE user_id=? AND skill=? ORDER BY id DESC LIMIT ?
        """, (user_id, skill, limit)).fetchall()
        return [dict(r) for r in reversed(rows)]

def save_tutor_message(user_id, skill, role, content):
    with _conn() as con:
        con.execute("INSERT INTO tutor_messages(user_id,skill,role,content,created_at) VALUES(?,?,?,?,?)",
                    (user_id, skill, role, content, datetime.now().isoformat()))
