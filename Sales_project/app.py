import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from firebase_config import auth
import ml_engine

# MUST BE FIRST
st.set_page_config(page_title="Advanced Sales Dashboard", layout="wide")

# ---------------- FIREBASE AUTHENTICATION ----------------
def login_signup():
    st.sidebar.title("🔐 Authentication")
    auth_mode = st.sidebar.radio("Choose Mode", ["Login", "Sign Up"])

    if auth_mode == "Login":
        st.title("👤 User Login")
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state["logged_in"] = True
                st.session_state["user_info"] = user
                st.success("✅ Logged in successfully!")
                st.rerun()
            except:
                st.error("❌ Login Failed: Incorrect email or password")

    else:
        st.title("📝 User Registration")
        new_email = st.text_input("Email Address", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Create Account"):
            if new_password != confirm_password:
                st.warning("⚠️ Passwords do not match")
            elif len(new_password) < 6:
                st.warning("⚠️ Password should be at least 6 characters")
            else:
                try:
                    auth.create_user_with_email_and_password(new_email, new_password)
                    st.success("✅ Account created! You can now log in.")
                except Exception as e:
                    st.error(f"❌ Sign Up Failed: {e}")

# Session control
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_signup()
    st.stop()

# ---------------- DASHBOARD ----------------

st.title("📊 Advanced Sales Analytics Dashboard")
st.markdown("Interactive dashboard for analyzing sales performance.")

@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_sales.csv")

df = load_data()

# Sidebar Filters
st.sidebar.header("🔎 Filters")

# Logout logic
if st.sidebar.button("🚪 Log Out"):
    st.session_state["logged_in"] = False
    st.session_state["user_info"] = None
    st.rerun()

region = st.sidebar.multiselect("Region", df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("Category", df["Category"].unique(), default=df["Category"].unique())
year = st.sidebar.multiselect("Year", df["Year"].unique(), default=df["Year"].unique())

filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Year"].isin(year))
]

# KPI Section
st.subheader("📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Sales", f"{filtered_df['Sales'].sum():,.0f}")
col2.metric("📈 Profit", f"{filtered_df['Profit'].sum():,.0f}")
col3.metric("🧾 Orders", filtered_df.shape[0])
col4.metric("📊 Avg Sales", f"{filtered_df['Sales'].mean():,.2f}")

# Download
st.download_button("📥 Download Data", filtered_df.to_csv(index=False), "sales.csv")

# Data Preview
with st.expander("📄 View Data"):
    st.dataframe(filtered_df)

if not filtered_df.empty:
    # Charts
    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        sns.barplot(x='Region', y='Sales', data=filtered_df, ax=ax1)
        ax1.set_title("Sales by Region")
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        sns.barplot(x='Category', y='Sales', data=filtered_df, ax=ax2)
        ax2.set_title("Sales by Category")
        st.pyplot(fig2)

    # Monthly Trend
    st.subheader("📈 Monthly Trend")
    monthly = filtered_df.groupby("Month")["Sales"].sum()

    fig3, ax3 = plt.subplots()
    monthly.plot(marker='o', ax=ax3)
    ax3.set_title("Monthly Sales Trend")
    st.pyplot(fig3)

    # Heatmap
    st.subheader("🔥 Heatmap")
    pivot = filtered_df.pivot_table(values='Sales', index='Region', columns='Category')

    fig4, ax4 = plt.subplots()
    sns.heatmap(pivot, annot=True, cmap='coolwarm', ax=ax4)
    st.pyplot(fig4)

    # ---------------- ADVANCED ML (XGBOOST FORECASTING) ----------------
    st.markdown("---")
    st.subheader("🤖 Advanced AI Sales Forecasting")
    st.info("Using XGBoost to predict future trends based on seasonality and historical patterns.")

    # Prepare data and model
    ml_df_prepped = ml_engine.prepare_data(df)
    model, features, mae = ml_engine.train_model(ml_df_prepped)

    # Forecast Section
    colA, colB = st.columns([1, 2])
    
    with colA:
        st.write("### ⚙️ Forecast Settings")
        forecast_months = st.slider("Select Forecast Horizon (Months)", 1, 12, 6)
        st.metric("Model Precision (MAE)", f"{mae:,.2f}")
        
    with colB:
        st.write("### 📈 Future Sales Projection")
        # Run forecast
        future_forecast = ml_engine.forecast_future(ml_df_prepped, model, features, forecast_months)
        
        # Combine historical and future for plotting
        hist_trend = df.groupby(['Year', 'Month'])['Sales'].sum().reset_index()
        hist_trend['Date'] = pd.to_datetime(hist_trend[['Year', 'Month']].assign(Day=1))
        
        # Aggregated future trend
        future_trend = future_forecast.groupby('Date')['Predicted_Sales'].sum().reset_index()
        
        fig_fore, ax_fore = plt.subplots(figsize=(10, 4))
        ax_fore.plot(hist_trend['Date'], hist_trend['Sales'], label='Historical Sales', color='blue', marker='o')
        ax_fore.plot(future_trend['Date'], future_trend['Predicted_Sales'], label='AI Forecast', color='orange', linestyle='--', marker='s')
        
        ax_fore.set_title(f"Next {forecast_months} Months Forecast")
        ax_fore.legend()
        st.pyplot(fig_fore)

    # Individual Prediction
    with st.expander("🔍 Deep Dive: Predict Specific Item/Region"):
        colX, colY = st.columns(2)
        with colX:
            input_region = st.selectbox("Region", df["Region"].unique(), key="ml_reg")
            input_category = st.selectbox("Category", df["Category"].unique(), key="ml_cat")
        with colY:
            input_year = st.number_input("Year", 2023, 2030, 2025, key="ml_yr")
            input_month = st.slider("Month", 1, 12, 6, key="ml_mo")

        # Prep manual input
        manual_row = {
            'Year': input_year,
            'Month': input_month,
            'Quarter': (input_month - 1) // 3 + 1,
            'IsMonthsEnd': 1 if input_month in [3, 6, 9, 12] else 0,
            'Prev_Month_Sales': df['Sales'].median()
        }
        manual_df = pd.DataFrame([manual_row])
        manual_df[f'Region_{input_region}'] = 1
        manual_df[f'Category_{input_category}'] = 1
        manual_df = manual_df.reindex(columns=features, fill_value=0)
        
        indiv_pred = model.predict(manual_df)[0]
        st.success(f"📊 Predicted Sales for {input_region} - {input_category}: **{int(indiv_pred):,}**")

else:
    st.warning("⚠ No data available for selected filters.")

# Footer
st.markdown("---")
st.markdown("🚀 Advanced Project with Random Forest ML")