# 📊 Advanced Sales Data Analytics & Prediction Project

A comprehensive data analysis and machine learning pipeline designed to process, clean, and visualize sales performance. This project features an interactive Streamlit dashboard with secure admin access and a Random Forest predictive model for sales forecasting.

---

## 🌟 Key Features

- **🔐 Secure Admin Login**: Integrated authentication for dashboard access.
- **🧹 Automated Data Pipeline**: Cleans raw CSV data, handles missing values, and prepares time-series features.
- **📊 Interactive Dashboard**: Built with Streamlit, offering dynamic filters for Region, Category, and Year.
- **📈 Advanced ML Predictions**: Uses a **Random Forest Regressor** to predict future sales based on Year, Month, Region, and Category.
- **🔥 Visual Analytics**: Includes Sales by Region, Monthly Trends, and Regional Category Heatmaps.
- **🔍 Static EDA Reports**: Generates high-quality charts for offline presentations.

---

## 📂 Project Structure

```text
Sales_project/
├── main.py                 # Data Cleaning & Feature Engineering Pipeline
├── eda.py                  # Static Exploratory Data Analysis (Generates Visuals)
├── app.py                  # Interactive Streamlit Dashboard (Main App)
├── data/
│   ├── raw_sales.csv       # Original dataset (Input)
│   └── cleaned_sales.csv   # Processed dataset (Output for ML/Dashboard)
├── visuals/                # Automatically generated PNG charts
├── report/
│   └── insights.txt        # Business takeaways and analysis summary
├── dashboards/
│   └── sales_dashboard.pbix # Optional Power BI Dashboard file
└── requirements.txt        # List of Python dependencies
```

---

## 🛠️ Setup & Installation

Ensure you have Python 3.8+ installed. Clone the repository and install the dependencies:

```bash
pip install pandas matplotlib seaborn streamlit scikit-learn pyrebase4
```

---

## 🚀 How to Run the Project

Follow these steps in order to process the data and launch the analytics suite:

### 1. Data Cleaning
Prepares the data by cleaning and extracting time features (Month, Year).
```bash
python main.py
```
*Output: Generates `data/cleaned_sales.csv`*

### 2. Static Analysis (Optional)
Generates high-resolution charts for your reports.
```bash
python eda.py
```
*Output: Saves 3 charts to the `visuals/` folder.*

### 3. Launch the Dashboard
Start the interactive Streamlit application.
```bash
streamlit run app.py (or)
python -m streamlit run app.py
```
*   **Login Credentials**: 
    - **Username**: `admin`
    - **Password**: `1234`

---

## 🤖 Machine Learning Sales Prediction

The project now utilizes a **Random Forest Regressor** for more accurate and granular sales forecasting. Unlike simple linear models, this model considers:
- **Year & Month**: Captures seasonal trends and growth.
- **Region**: Accounts for geographic performance variations.
- **Category**: factors in product-specific demand.

**To use predictions**: Navigate to the "🤖 Advanced Sales Prediction" section in the dashboard, select your parameters, and get an instant sales forecast.

---

## 📈 Dashboard Insights

- **📌 Key Metrics**: Real-time KPIs for Total Sales, Profit, Order Count, and Average Sales.
- **🗺️ Regional heatmap**: Identifies high-demand categories across different territories.
- **📅 Trend Analysis**: Tracks sales performance over time to spot growth patterns.

---

🚀 **Developed for High-Performance Business Intelligence and Forecasting.**
