import sqlite3

conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    feedback TEXT NOT NULL,
    rating INTEGER NOT NULL,
    category TEXT NOT NULL
)
''')

conn.commit()
conn.close()



