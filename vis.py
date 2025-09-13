import streamlit as st
import sqlite3
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from utils_db import (
    create_user,
    get_user_id,
    insert_investment,
    delete_investment,
    fetch_investments,
    fetch_latest_price
)

# SQLite db connection and table creation
conn = sqlite3.connect("investing_app.db")

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
        user_id = get_user_id(name_input, conn)
        if not user_id:
            create_user(name_input, conn)
            st.success(f"Hello {name_input}! Your account was created.")
        else:
            st.info(f"Welcome back, {name_input}!")
        # Store in session
        st.session_state.user = name_input
        current_user = name_input

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
                insert_investment(current_user, ticker, amount, price, str(date), conn)
                st.success(f"{amount} shares of {ticker} added successfully!")


# Fetch investments if user is logged in and has investments
if 'user' in st.session_state:
    # Initialize view mode
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    # Toggle button
    if st.button("Toggle Edit Mode"):
        st.session_state.edit_mode = not st.session_state.edit_mode

    try:
        # Fetch user investments
        investments = fetch_investments(conn)
        # Create column to display total value of each stock
        investments["total value"] = (investments["amount"] * investments["price"]).round(2)
    except Exception as e:
        print(f"Error fetching investments: {e}")

    # Display depending on mode
    if st.session_state.edit_mode and not investments.empty:
        st.write(f"### Edit Investments for {current_user}")
        for _, row in investments.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])
            col1.write(row["id"])
            col2.write(row["ticker"])
            col3.write(int(row["amount"]))
            col4.write(round(row["price"], 2))
            if col5.button("❌", key=f"del_{row['id']}"):
                delete_investment(row["id"], conn)
                st.success(f"Deleted {row['ticker']}")
                st.rerun()
    elif not st.session_state.edit_mode and not investments.empty:
        st.write(f"### {current_user} Investments")
        # Default view
        # only keep certain columns
        investments_subset = investments[["ticker", "amount", "price"]]
        # Add total value column
        investments_subset["total value"] = (investments_subset["amount"] * investments_subset["price"]).round(2)
        # rename columns
        investments_subset = investments_subset.rename(columns={
            "id": "ID",
            "ticker": "Ticker",
            "amount": "Amount",
            "price": "Price (€)",
            "total value": "Total Value (€)"
        })
        # Display investments table
        st.dataframe(investments_subset)
        # Display total investment value
        total_investment = investments["total value"].sum()
        st.write(f"Total Investment Value: ${total_investment}")
    else:
        st.info("No investments yet.")




# Line chart of selected ticker
#if not df_investmentes.empty:
#    selected_ticker = st.selectbox("Select a ticker to view its performance", df_investmentes["Ticker"].unique())
#    if selected_ticker:
#        ticker_data = yf.Ticker(selected_ticker).history(period="3mo")
#        st.line_chart(ticker_data["Close"])

conn.close()