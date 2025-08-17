import sqlite3

conn = sqlite3.connect("investing_app.db")
c = conn.cursor()

# Create tables
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    ticker TEXT,
    amount REAL,
    price REAL,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()
print("Database initialized ✅")
