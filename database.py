import sqlite3

def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            feedback TEXT NOT NULL,
            rating INTEGER,
            category TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database and tables created successfully!")

if __name__ == '__main__':
    init_db()



