import sqlite3

DB_NAME = "wellness.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT
)
""")

# Mood
cur.execute("""
CREATE TABLE IF NOT EXISTS mood(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    mood_score INTEGER,
    date TEXT
)
""")

# Meditation
cur.execute("""
CREATE TABLE IF NOT EXISTS meditation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    duration INTEGER,
    date TEXT
)
""")

# Sleep
cur.execute("""
CREATE TABLE IF NOT EXISTS sleep(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    hours INTEGER,
    quality TEXT,
    reflection TEXT,
    date TEXT
)
""")

# Water
cur.execute("""
CREATE TABLE IF NOT EXISTS water(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    glasses INTEGER,
    date TEXT
)
""")

# Habit
cur.execute("""
CREATE TABLE IF NOT EXISTS habit(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    habit_name TEXT,
    done INTEGER,
    date TEXT
)
""")

# Journal
cur.execute("""
CREATE TABLE IF NOT EXISTS journal(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    thoughts TEXT,
    gratitude TEXT,
    mood TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()
print("✅ Database initialized successfully!")