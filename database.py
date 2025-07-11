import sqlite3

def get_feedbacks():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('SELECT * FROM feedback')
    feedbacks = c.fetchall()
    conn.close()
    return feedbacks

def save_feedback(user, content):
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (user, content) VALUES (?, ?)', (user, content))
    conn.commit()
    conn.close()


