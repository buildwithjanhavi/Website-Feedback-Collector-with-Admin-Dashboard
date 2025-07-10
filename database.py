import sqlite3

# Connect to SQLite database (will create feedback.db if it doesn't exist)
conn = sqlite3.connect('feedback.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the feedback table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        comment TEXT NOT NULL,
        sentiment TEXT NOT NULL
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully!")

