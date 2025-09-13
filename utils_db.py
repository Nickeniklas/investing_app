import streamlit as st
import sqlite3
import pandas as pd
import yfinance as yf

# Function to create user
def create_user(name, conn=sqlite3.connect("investing_app.db")):
    cursor = conn.execute("SELECT id FROM users WHERE name = ?", (name,))
    user_id = cursor.fetchone()
    if not user_id:
        conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        st.success(f"User {name} created successfully!")
    else:
        st.warning(f"User {name} already exists.")

# Function to get user ID
def get_user_id(name, conn=sqlite3.connect("investing_app.db")):
    cursor = conn.execute("SELECT id FROM users WHERE name = ?", (name,))
    user_id = cursor.fetchone()
    cursor.close()
    if user_id:
        return user_id[0]
    else:
        st.error("User not found")
        return None

# Function to insert data into the investments table
def insert_investment(user, ticker, amount, price, date, conn=sqlite3.connect("investing_app.db")):
    user_id = get_user_id(user, conn)
    if user_id:
        conn.execute("INSERT INTO investments (user_id, ticker, amount, price, date) VALUES (?, ?, ?, ?, ?)", (user_id, ticker, amount, price, date))
        conn.commit()
    else:
        st.error("User not found")

# Function to delete an investment
def delete_investment(investment_id, conn=sqlite3.connect("investing_app.db")):
    conn.execute("DELETE FROM investments WHERE id = ?", (investment_id,))
    conn.commit()

# Function to fetch all investments
def fetch_investments(conn=sqlite3.connect("investing_app.db")):
    username = st.session_state.user
    query = """
    SELECT i.*
    FROM investments i
    JOIN users u ON i.user_id = u.id
    WHERE u.name = ?
    """
    return pd.read_sql(query, conn, params=(username,))


# Fetching the latest stock price using yfinance
def fetch_latest_price(ticker):
        if ticker:
            try:
                df = yf.Ticker(ticker).history(period="1d", interval="1d")
                if df.empty:  # ticker exists but no data
                    st.error(f"No data found for {ticker}")
                    return None
                price = df['Close'].iloc[-1]
                return price
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {e}")
                return None
            
            