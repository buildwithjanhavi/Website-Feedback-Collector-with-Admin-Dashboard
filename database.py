import sqlite3

def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            user TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_feedbacks():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback')
    feedbacks = cursor.fetchall()
    conn.close()
    return feedbacks

init_db()



