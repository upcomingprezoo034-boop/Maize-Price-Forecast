import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA AND MODEL
# -----------------------------
try:
    data = pd.read_excel("maize_dataset.xlsx")
except FileNotFoundError:
    st.error("Error: maize_dataset.xlsx file not found. Please ensure the file exists in the app directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {str(e)}")
    st.stop()

try:
    with open("price_prediction_model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    st.error("Error: price_prediction_model.pkl file not found. Please ensure the model file exists in the app directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Validate required columns
required_columns = ["Market", "Retail", "Date"]
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    st.error(f"Error: Missing required columns in dataset: {', '.join(missing_columns)}")
    st.stop()

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
    st.selectbox("Crop Produced", ["Maize", "Beans", "Green grams"])
    password = st.text_input("Create Password", type="password")

    if st.button("Register / Login"):

        if name != "" and password != "":
            st.session_state.logged_in = True
            st.success("Welcome " + name)
        else:
            st.warning("Please enter both name and password.")

else:

    # -----------------------------
    # PAGE NAVIGATION
    # -----------------------------
    page = st.sidebar.selectbox(
        "Navigation",
        ["Predict Maize Price", "Market Trends"]
    )

    # -----------------------------
    # PAGE 1: PRICE PREDICTION
    # -----------------------------
    if page == "Predict Maize Price":

        st.header("Maize Price Prediction")

        markets = sorted(data["Market"].unique())

        if len(markets) == 0:
            st.warning("No markets found in the dataset.")
        else:
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
                market_data = data[data["Market"] == market]

                if market_data.empty:
                    st.warning(f"No data available for market: {market}")
                else:
                    avg_price = market_data["Retail"].mean()

                    # convert duration to numeric
                    timeline_map = {
                        "1 Week": 1,
                        "2 Weeks": 2,
                        "1 Month": 4,
                        "2 Months": 8,
                        "3 Months": 12
                    }

                    duration_value = timeline_map[duration]

                    try:
                        # Example prediction
                        prediction = model.predict([[avg_price, duration_value]])

                        st.success(
                            f"Expected maize price in {market} after {duration} is approximately **{prediction[0]:.2f} KSh/kg**"
                        )
                    except Exception as e:
                        st.error(f"Error making prediction: {str(e)}")

    # -----------------------------
    # PAGE 2: MARKET TRENDS
    # -----------------------------
    if page == "Market Trends":

        st.header("Market Price Trends")

        markets = sorted(data["Market"].unique())

        if len(markets) == 0:
            st.warning("No markets found in the dataset.")
        else:
            market = st.selectbox(
                "Select Market for Trend Analysis",
                markets
            )

            market_data = data[data["Market"] == market].copy()

            if market_data.empty:
                st.warning(f"No data available for market: {market}")
            else:
                try:
                    market_data["Date"] = pd.to_datetime(market_data["Date"])
                    market_data = market_data.sort_values("Date")

                    # Price Trend Graph
                    st.subheader("Retail Price Trend")

                    fig, ax = plt.subplots(figsize=(10, 5))

                    ax.plot(
                        market_data["Date"],
                        market_data["Retail"],
                        linewidth=2
                    )

                    ax.set_xlabel("Date")
                    ax.set_ylabel("Price (KSh/kg)")
                    ax.set_title("Historical Price Trend")
                    fig.autofmt_xdate()

                    st.pyplot(fig)

                    # Seasonal Pattern
                    st.subheader("Seasonal Pattern")

                    market_data["Month"] = market_data["Date"].dt.month

                    seasonal = market_data.groupby("Month")["Retail"].mean()

                    fig2, ax2 = plt.subplots(figsize=(10, 5))

                    ax2.bar(seasonal.index, seasonal.values, color="steelblue")

                    ax2.set_xlabel("Month")
                    ax2.set_ylabel("Average Price (KSh/kg)")
                    ax2.set_title("Average Price by Month")

                    st.pyplot(fig2)

                    st.info(
                        "Prices usually rise during planting seasons when supply is low and fall during harvest periods."
                    )
                except Exception as e:
                    st.error(f"Error processing market data: {str(e)}")
