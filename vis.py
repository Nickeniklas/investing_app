import streamlit as st
import sqlite3
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

# SQLite db connection and table creation
conn = sqlite3.connect("investing_app.db")

# Function to create user
def create_user(name):
    cursor = conn.execute("SELECT id FROM users WHERE name = ?", (name,))
    user_id = cursor.fetchone()
    if not user_id:
        conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        st.success(f"User {name} created successfully!")
    else:
        st.warning(f"User {name} already exists.")

# Function to get user ID
def get_user_id(name):
    cursor = conn.execute("SELECT id FROM users WHERE name = ?", (name,))
    user_id = cursor.fetchone()
    if user_id:
        return user_id[0]
    else:
        st.error("User not found")
        return None

# Function to insert data into the investments table
def insert_investment(user, ticker, amount, price, date):
    user_id = get_user_id(user)
    if user_id:
        conn.execute("INSERT INTO investments (user_id, ticker, amount, price, date) VALUES (?, ?, ?, ?, ?)", (user_id, ticker, amount, price, date))
        conn.commit()
    else:
        st.error("User not found")

# Function to fetch all investments
def fetch_investments():
    cursor = conn.execute("SELECT * FROM investments")
    investments = cursor.fetchall()
    return investments

# Streamlit Page setup
st.set_page_config(page_title="MY INVESTER", page_icon=":bar_chart:", layout="wide")  # page configuration
st.title(" 📊 MY INVESTER")  # title of the web page
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)  

# Check if user is logged in
current_user = st.session_state.get('user', None)

# Show name input if no user is logged in
if 'user' not in st.session_state:
    name_input = st.text_input("Enter your name:")

    if name_input:
        # Check if user exists in DB
        user_id = get_user_id(name_input)
        if not user_id:
            create_user(name_input)
            st.success(f"Hello {name_input}! Your account was created.")
        else:
            st.info(f"Welcome back, {name_input}!")
        # Store in session
        st.session_state.user = name_input

# Logged-in logic
if 'user' in st.session_state:
    st.write(f"Logged in as {st.session_state.user}")
    if st.button("Log out"):
        del st.session_state.user
        st.success("You have been logged out ✅")
        st.rerun()

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
            insert_investment(current_user, ticker, amount, price, str(date))
            st.success(f"{amount} shares of {ticker} added successfully!")

conn.close()