import sqlite3

# Connect to SQLite database
connection = sqlite3.connect('feedback.db')

# Execute schema from schema.sql file
with open('schema.sql', 'r') as f:
    connection.executescript(f.read())

# Save changes and close connection
connection.commit()
connection.close()

print("✅ Database created successfully!")


