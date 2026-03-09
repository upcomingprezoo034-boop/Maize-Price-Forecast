import streamlit as st
import pandas as pd
import numpy as np
import pickle
import datetime
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA AND MODEL
# -----------------------------
data = pd.read_excel("maize_dataset.xlsx")

model = pickle.load(open("price_prediction_model.pkl","rb"))

# -----------------------------
# APP TITLE
# -----------------------------
st.set_page_config(page_title="Maize Price Advisory System")

st.title("Kenya Maize Market Advisory System")

# -----------------------------
# SIMPLE FARMER LOGIN SYSTEM
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in == False:

    st.header("Farmer Registration")

    name = st.text_input("Farmer Name")
    crop = st.selectbox("Crop Produced", ["Maize","Beans","Green grams"])
    password = st.text_input("Create Password", type="password")

    if st.button("Register / Login"):

        if name != "" and password != "":
            st.session_state.logged_in = True
            st.success("Welcome " + name)

else:

    # -----------------------------
    # PAGE NAVIGATION
    # -----------------------------
    page = st.sidebar.selectbox(
        "Navigation",
        ["Predict Maize Price","Market Trends"]
    )

    # -----------------------------
    # PAGE 1: PRICE PREDICTION
    # -----------------------------
    if page == "Predict Maize Price":

        st.header("Maize Price Prediction")

        markets = sorted(data["Market"].unique())

        market = st.selectbox(
            "Select Market",
            markets
        )

        duration = st.selectbox(
            "Prediction Timeline",
            [
            "1 Week",
            "2 Weeks",
            "1 Month",
            "2 Months",
            "3 Months"
            ]
        )

        if st.button("Predict Price"):

            # Example feature extraction
            market_data = data[data["Market"]==market]

            avg_price = market_data["Retail"].mean()

            # convert duration to numeric
            timeline_map = {
                "1 Week":1,
                "2 Weeks":2,
                "1 Month":4,
                "2 Months":8,
                "3 Months":12
            }

            duration_value = timeline_map[duration]

            # Example prediction
            prediction = model.predict([[avg_price,duration_value]])

            st.success(
                f"Expected maize price in {market} after {duration} is approximately **{prediction[0]:.2f} KSh/kg**"
            )

    # -----------------------------
    # PAGE 2: MARKET TRENDS
    # -----------------------------
    if page == "Market Trends":

        st.header("Market Price Trends")

        market = st.selectbox(
            "Select Market for Trend Analysis",
            sorted(data["Market"].unique())
        )

        market_data = data[data["Market"]==market]

        market_data["Date"] = pd.to_datetime(market_data["Date"])

        market_data = market_data.sort_values("Date")

        # Price Trend Graph
        st.subheader("Retail Price Trend")

        fig, ax = plt.subplots()

        ax.plot(
            market_data["Date"],
            market_data["Retail"]
        )

        ax.set_xlabel("Date")
        ax.set_ylabel("Price (KSh/kg)")
        ax.set_title("Historical Price Trend")

        st.pyplot(fig)

        # Seasonal Pattern
        st.subheader("Seasonal Pattern")

        market_data["Month"] = market_data["Date"].dt.month

        seasonal = market_data.groupby("Month")["Retail"].mean()

        fig2, ax2 = plt.subplots()

        ax2.bar(seasonal.index, seasonal.values)

        ax2.set_xlabel("Month")
        ax2.set_ylabel("Average Price")

        st.pyplot(fig2)

        st.info(
        "Prices usually rise during planting seasons when supply is low and fall during harvest periods."
        )
