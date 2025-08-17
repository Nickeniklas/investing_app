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
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# (Optional) Insert sample data
c.execute("INSERT INTO users (name) VALUES (?)", ("Niklas",))
c.execute("INSERT INTO investments (user_id, ticker, amount) VALUES (?, ?, ?)", (1, "AAPL", 10))

conn.commit()
conn.close()
print("Database initialized ✅")
