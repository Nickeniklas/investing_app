import streamlit as st
import sqlite3
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

# SQLite db connection and table creation
conn = sqlite3.connect("investments.db")
conn.execute("CREATE TABLE IF NOT EXISTS investments (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, ticker TEXT, amount INT, price REAL, date TEXT)")

# Function to insert data into the investments table
def insert_investment(user, ticker, amount, price, date):
    conn.execute("INSERT INTO investments (user, ticker, amount, price, date) VALUES (?, ?, ?, ?, ?)", (user, ticker, amount, price, date))
    conn.commit()

# Function to fetch all investments
def fetch_investments():
    cursor = conn.execute("SELECT * FROM investments")
    investments = cursor.fetchall()
    return investments

# Streamlit Page setup
st.set_page_config(page_title="MY INVESTER", page_icon=":bar_chart:", layout="wide")  # page configuration
st.title(" 📊 MY INVESTER")  # title of the web page
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)  

name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}! Let's invest.")

    # Input form for investment details
    with st.form(key='investment_form'):
        ticker = st.text_input("Ticker Symbol:")
        amount = st.number_input("Amount of Stock:", min_value=0, step=1)
        date = st.date_input("Investment Date:")

        # Fetching the latest stock price using yfinance
        if ticker:
            try:
                df = yf.Ticker(ticker).history(period="1d", interval="1d")
                price = df['Close'].iloc[-1]
            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {e}")
                price = 0.0

        submit_button = st.form_submit_button(label='Add Investment')
        
        if submit_button:
            insert_investment(name, ticker, amount, price, str(date))
            st.success(f"{amount} shares of {ticker} added successfully!")

conn.close()