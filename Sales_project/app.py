import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from firebase_config import auth
import ml_engine
import os
import datetime
from streamlit_autorefresh import st_autorefresh

# Project Root for robust path handling
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT_DIR, "data", "cleaned_sales.csv")

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
            user = None
            try:
                user = auth.sign_in_with_email_and_password(email, password)
            except Exception:
                st.error("❌ Login Failed: Incorrect email or password")
            
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_info"] = user
                st.rerun()

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
                    st.info("💡 Switch to 'Login' mode in the sidebar to enter.")
                except Exception as e:
                    # Clean the error message from Firebase
                    error_msg = str(e)
                    if "EMAIL_EXISTS" in error_msg:
                        st.error("❌ This email is already registered. Please go to 'Login' mode instead.")
                    elif "INVALID_EMAIL" in error_msg:
                        st.error("❌ The email address is badly formatted.")
                    elif "WEAK_PASSWORD" in error_msg:
                        st.error("❌ The password is too weak.")
                    else:
                        st.error(f"❌ Sign Up Failed: {error_msg}")

# Session control
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_signup()
    st.stop()

# Initialize session state for real-time updates
if "last_updated" not in st.session_state:
    st.session_state["last_updated"] = datetime.datetime.now().timestamp()

if "show_success" not in st.session_state:
    st.session_state["show_success"] = False

if "success_msg" not in st.session_state:
    st.session_state["success_msg"] = ""

# Show success message if a record was just added
if st.session_state["show_success"]:
    st.success(st.session_state["success_msg"])
    st.session_state["show_success"] = False

# Auto-refresh only runs for logged-in users
st_autorefresh(interval=5000, key="datarefresh")

# ---------------- DASHBOARD ----------------

st.title("📊 Professional Sales Analytics Dashboard")
st.markdown("""
Welcome to the **Advanced Sales Analytics Suite**.  
Analyze historical trends, monitor real-time performance, and use AI to forecast future growth.
""")

# ---------------- DATA LOADING AND VALIDATION ----------------

st.markdown("---")
st.subheader("📂 Upload and Validate Dataset")
st.info("💡 **Dataset Requirement:** For the AI model to work, your dataset MUST contain these columns: `Year`, `Month`, `Region`, `Category`, and `Sales`.")

uploaded_file = st.file_uploader("📂 Upload New Dataset", type=["csv"], help="Upload a CSV with Year, Month, Region, Category, and Sales columns.")

def load_and_validate_data():
    """
    Load data from upload or default, and validate specific columns.
    """
    required_columns = ['Year', 'Month', 'Region', 'Category', 'Sales']
    
    if uploaded_file is not None:
        try:
            temp_df = pd.read_csv(uploaded_file)
            missing = [col for col in required_columns if col not in temp_df.columns]
            
            if missing:
                st.error(f"❌ Missing required columns: {', '.join(missing)}")
                st.info("💡 Please upload a CSV containing: Year, Month, Region, Category, Sales")
                st.stop()
            
            # Update session state to trigger retraining for custom data
            if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
                st.session_state["last_updated"] = datetime.datetime.now().timestamp()
                st.session_state["last_uploaded_file"] = uploaded_file.name
            
            # Use uploaded data
            st.toast("✅ Custom dataset uploaded successfully!")
            return temp_df[required_columns], True
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.stop()
    
    # Fallback to default
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ Default dataset not found at {DATA_PATH}")
        st.stop()
        
    return pd.read_csv(DATA_PATH), False

df, uses_custom = load_and_validate_data()

# ---------------- DATASET OVERVIEW ----------------
st.markdown("---")
st.subheader("📊 Dataset Overview")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    st.metric("📊 Average Sales", f"${df['Sales'].mean():,.2f}")
with col_s2:
    st.metric("📈 Max Sales", f"${df['Sales'].max():,.2f}")
with col_s3:
    st.metric("📉 Min Sales", f"${df['Sales'].min():,.2f}")

with st.expander("📄 View Full Dataset Preview"):
    st.dataframe(df.head(100), use_container_width=True)

# ---------------- DASHBOARD FILTERS ----------------
st.sidebar.header("🔎 Filters")

# Logout logic
if st.sidebar.button("🚪 Log Out"):
    st.session_state["logged_in"] = False
    st.session_state["user_info"] = None
    st.rerun()

region = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=df["Region"].unique())
category = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=df["Category"].unique())
year = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=df["Year"].unique())

filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(category)) &
    (df["Year"].isin(year))
]

# ---------------- 📌 KEY METRICS SECTION ----------------
st.markdown("---")
st.subheader("📌 Business Performance Overview")
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Sales", f"{filtered_df['Sales'].sum():,.0f}")
profit_val = filtered_df['Profit'].sum() if 'Profit' in filtered_df.columns else 0
col2.metric("📈 Profit", f"{profit_val:,.0f}")
col3.metric("🧾 Orders", filtered_df.shape[0])
col4.metric("📊 Avg Sales", f"{filtered_df['Sales'].mean():,.2f}")

# Download
st.download_button("📥 Download Data", filtered_df.to_csv(index=False), "sales.csv")

# Data Preview
with st.expander("📄 View Data"):
    st.dataframe(filtered_df)

if not filtered_df.empty:
    # ---------------- 📈 VISUAL ANALYTICS SECTION ----------------
    st.markdown("---")
    st.subheader("📈 Visual Data Analytics")
    
    # Row 1: Regional & Category Breakdown
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write("#### 🌎 Sales by Region")
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.barplot(x='Region', y='Sales', data=filtered_df, ax=ax1, palette="viridis")
        st.pyplot(fig1)

    with col_c2:
        st.write("#### 📁 Sales by Category")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.barplot(x='Category', y='Sales', data=filtered_df, ax=ax2, palette="magma")
        st.pyplot(fig2)

    # Row 2: Trends & Correlations
    col_c3, col_c4 = st.columns(2)
    with col_c3:
        st.write("#### 📅 Monthly Sales Trend")
        monthly = filtered_df.groupby("Month")["Sales"].sum()
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        monthly.plot(marker='o', color='#1f77b4', ax=ax3)
        ax3.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig3)

    with col_c4:
        st.write("#### 🔥 Region-Category Heatmap")
        pivot = filtered_df.pivot_table(values='Sales', index='Region', columns='Category')
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        sns.heatmap(pivot, annot=True, cmap='YlGnBu', ax=ax4, fmt=".0f")
        st.pyplot(fig4)

    # ----------------🤖 MACHINE LEARNING TRAINING ----------------
    # Prepare data and model dynamically based on current dataset
    ml_df_prepped = ml_engine.prepare_data(df)
    model, features, mae = ml_engine.train_model(ml_df_prepped, st.session_state["last_updated"])

    # ----------------🤖 SALES PREDICTION SECTION ----------------
    st.markdown("---")
    st.subheader("🤖 Sales Prediction")
    st.info("Use the trained XGBoost model to predict sales based on: `Year`, `Month`, `Region`, and `Category`.")
    
    with st.container():
        pred_col1, pred_col2 = st.columns(2)
        
        with pred_col1:
            input_region = st.selectbox("🎯 Select Region", df["Region"].unique(), key="ml_reg")
            input_category = st.selectbox("📦 Select Category", df["Category"].unique(), key="ml_cat")
        
        with pred_col2:
            input_year = st.number_input("📅 Select Year", min_value=2020, max_value=2035, value=2025, key="ml_yr")
            input_month = st.slider("🗓️ Select Month", 1, 12, 6, key="ml_mo")

        # Prep manual input
        manual_row = {
            'Year': input_year,
            'Month': input_month
        }
        manual_df = pd.DataFrame([manual_row])
        
        # Align with training One-Hot columns
        for col in features:
            if col.startswith('Region_'):
                manual_df[col] = 1 if col == f'Region_{input_region}' else 0
            elif col.startswith('Category_'):
                manual_df[col] = 1 if col == f'Category_{input_category}' else 0
        
        manual_df = manual_df.reindex(columns=features, fill_value=0)

        # --- Prediction Result ---
        st.markdown("### 📊 Prediction Summary")
        
        indiv_pred = model.predict(manual_df)[0]
        
        # Display inputs and prediction in a grid
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        res_col1.metric("📍 Region", input_region)
        res_col2.metric("📦 Category", input_category)
        res_col3.metric("📅 Year", input_year)
        res_col4.metric("🗓️ Month", input_month)
        
        st.markdown("---")
        
        final_col1, final_col2 = st.columns([2, 1])
        with final_col1:
            if indiv_pred > 10000:
                st.warning(f"⚠️ **High Sales Alert:** Predicted sales `${int(indiv_pred):,}` exceed $10,000.")
            elif indiv_pred < 3000:
                st.error(f"📉 **Low Sales Alert:** Predicted sales `${int(indiv_pred):,}` are below $3,000.")
            else:
                st.success(f"💰 **Estimated Predicted Sales:** `${int(indiv_pred):,}`")
                st.info("✅ **Status:** Prediction is within normal expected range.")
            st.caption("✨ Prediction based on currently active dataset and XGBoost training.")
        with final_col2:
            st.metric("Model Confidence (MAE)", f"{mae:,.2f}")

else:
    st.warning("⚠ No data available for selected filters.")

# Footer
st.markdown("---")
st.markdown("🚀 Advanced Project with XGBoost ML")

# ---------------- ADD NEW SALES DATA ----------------
st.markdown("---")
st.subheader("➕ Add New Sales Data")
st.markdown("Submit new sales records — data updates instantly on the dashboard.")

with st.form("add_sales_form", clear_on_submit=True):
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        new_region = st.selectbox(
            "Region",
            sorted(df["Region"].unique()),
            key="form_region"
        )
        new_sales = st.number_input(
            "Sales ($)",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            key="form_sales"
        )

    with col_f2:
        new_category = st.selectbox(
            "Category",
            sorted(df["Category"].unique()),
            key="form_category"
        )
        new_profit = st.number_input(
            "Profit ($)",
            min_value=0.0,
            step=5.0,
            format="%.2f",
            key="form_profit"
        )
        st.caption("ℹ️ **Deployment Note:** On Streamlit Cloud, local file updates are temporary and will reset on app reboot.")

    with col_f3:
        new_year = st.number_input(
            "Year",
            min_value=2020,
            max_value=2035,
            value=2025,
            step=1,
            key="form_year"
        )
        new_month = st.selectbox(
            "Month",
            list(range(1, 13)),
            format_func=lambda m: [
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ][m - 1],
            key="form_month"
        )

    submitted = st.form_submit_button("✅ Add Record", use_container_width=True)

    if submitted:
        if new_sales == 0.0:
            st.warning("⚠️ Sales value cannot be zero.")
        else:
            import calendar, datetime

            month_names = [
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ]
            month_name = month_names[int(new_month) - 1]
            order_date  = datetime.date(int(new_year), int(new_month), 1).strftime("%Y-%m-%d")

            # Build new row matching existing CSV columns
            existing_df  = pd.read_csv("data/cleaned_sales.csv")
            new_order_id = int(existing_df["Order ID"].max()) + 1 if "Order ID" in existing_df.columns else 1

            new_row = {col: "" for col in existing_df.columns}
            new_row.update({
                "Order ID":   new_order_id,
                "Order Date": order_date,
                "Region":     new_region,
                "Category":   new_category,
                "Sales":      new_sales,
                "Profit":     new_profit,
                "Year":       int(new_year),
                "Month":      int(new_month),
                "Month Name": month_name,
            })

            updated_df = pd.concat(
                [existing_df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            updated_df.to_csv(DATA_PATH, index=False)

            # Update session state to trigger cache refresh and show success
            st.session_state["last_updated"] = datetime.datetime.now().timestamp()
            st.session_state["show_success"] = True
            st.session_state["success_msg"] = f"✅ New record added! {new_region} | {new_category} | ${new_sales:,.2f} | {month_name} {int(new_year)}"
            
            st.rerun()
