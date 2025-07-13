import sqlite3

# Connect to SQLite DB (creates the file if it doesn't exist)
conn = sqlite3.connect('feedback.db')

# Create cursor
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create feedback table
cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    feedback TEXT NOT NULL,
    rating INTEGER NOT NULL,
    category TEXT NOT NULL
)
''')

# Commit and close
conn.commit()
conn.close()
print("✅ Database and tables created successfully!")



