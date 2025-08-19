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
    cursor.close()
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

# Function to delete an investment
def delete_investment(investment_id):
    conn.execute("DELETE FROM investments WHERE id = ?", (investment_id,))
    conn.commit()

# Function to fetch all investments
def fetch_investments():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM investments WHERE user_id = ?", (get_user_id(current_user),))
    investments = cursor.fetchall()
    cursor.close()
    return investments

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
        # input fields
        ticker = st.text_input("Ticker Symbol:")
        amount = st.number_input("Amount of Stock:", min_value=0, step=1)
        date = st.date_input("Investment Date:")
        #submit button
        submit_button = st.form_submit_button(label='Add Investment')
        if submit_button:
            #get latest price, else cancel order
            price = fetch_latest_price(ticker)
            if price is not None:            
                insert_investment(current_user, ticker, amount, price, str(date))
                st.success(f"{amount} shares of {ticker} added successfully!")

# Display / Visualize owned stocks
investments = fetch_investments()
if investments:
    df_investmentes = pd.DataFrame(investments, columns=["ID", "User ID", "Ticker", "Amount", "Price", "Date"])
    # create column to display total value of each stock
    df_investmentes["Total Value"] = (df_investmentes["Amount"] * df_investmentes["Price"]).round(2)
    st.write(f"### Investments for {current_user}")
    st.dataframe(df_investmentes)

# Display total investment value
total_investment = df_investmentes["Total Value"].sum()
st.write(f"Total Investment Value: ${total_investment}")

# Line chart of selected ticker
if not df_investmentes.empty:
    selected_ticker = st.selectbox("Select a ticker to view its performance", df_investmentes["Ticker"].unique())
    if selected_ticker:
        ticker_data = yf.Ticker(selected_ticker).history(period="3mo")
        st.line_chart(ticker_data["Close"])

conn.close()