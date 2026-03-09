import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt

# Set page config FIRST (before any other st commands)
st.set_page_config(page_title="Maize Price Advisory System")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "farmer_name" not in st.session_state:
    st.session_state.farmer_name = None
if "crop_produced" not in st.session_state:
    st.session_state.crop_produced = None

# Load data and model only after set_page_config
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

st.title("Kenya Maize Market Advisory System")

# Login/Registration System
if not st.session_state.logged_in:
    st.header("Farmer Registration")
    
    name = st.text_input("Farmer Name")
    crop_produced = st.selectbox("Crop Produced", ["Maize", "Beans", "Green grams"])
    password = st.text_input("Create Password", type="password")
    
    if st.button("Register / Login"):
        if name and password:
            st.session_state.logged_in = True
            st.session_state.farmer_name = name
            st.session_state.crop_produced = crop_produced
            st.success(f"Welcome {name}!")
            st.rerun()
        else:
            st.warning("Please enter both name and password.")
else:
    # Sidebar with user info and logout
    with st.sidebar:
        st.write(f"**Logged in as:** {st.session_state.farmer_name}")
        st.write(f"**Crop:** {st.session_state.crop_produced}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.farmer_name = None
            st.session_state.crop_produced = None
            st.rerun()
    
    # Page Navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Predict Maize Price", "Market Trends"]
    )
    
    # PAGE 1: PRICE PREDICTION
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
                market_data = data[data["Market"] == market]
                
                if market_data.empty:
                    st.warning(f"No data available for market: {market}")
                else:
                    avg_price = market_data["Retail"].mean()
                    
                    timeline_map = {
                        "1 Week": 1,
                        "2 Weeks": 2,
                        "1 Month": 4,
                        "2 Months": 8,
                        "3 Months": 12
                    }
                    
                    duration_value = timeline_map[duration]
                    
                    try:
                        prediction = model.predict([[avg_price, duration_value]])
                        st.success(
                            f"Expected maize price in {market} after {duration} is approximately **{prediction[0]:.2f} KSh/kg**"
                        )
                    except Exception as e:
                        st.error(f"Error making prediction: {str(e)}")
    
    # PAGE 2: MARKET TRENDS
    elif page == "Market Trends":
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