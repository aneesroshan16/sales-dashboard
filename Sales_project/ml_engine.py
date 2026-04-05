import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import streamlit as st

@st.cache_data
def prepare_data(df):
    """
    Advanced preprocessing for the sales data.
    """
    # Group by time and categories
    df_grouped = df.groupby(['Year', 'Month', 'Region', 'Category'])['Sales'].sum().reset_index()
    
    # Add Seasonality Features
    df_grouped['Quarter'] = (df_grouped['Month'] - 1) // 3 + 1
    
    # Simple Seasonal indicators
    df_grouped['IsMonthsEnd'] = df_grouped['Month'].isin([3, 6, 9, 12]).astype(int)
    
    # Sort for lag creation
    df_grouped = df_grouped.sort_values(['Region', 'Category', 'Year', 'Month'])
    
    # Add Lag features (Previous Month Sales for the same Region/Category)
    df_grouped['Prev_Month_Sales'] = df_grouped.groupby(['Region', 'Category'])['Sales'].shift(1)
    
    # Fill missing lags with median
    df_grouped['Prev_Month_Sales'] = df_grouped['Prev_Month_Sales'].fillna(df_grouped['Sales'].median())
    
    return df_grouped

@st.cache_resource
def train_model(df_grouped):
    """
    Train an XGBoost model on the data.
    """
    # Features & Target
    # Convert categorical variables to dummies
    ml_data = pd.get_dummies(df_grouped, columns=['Region', 'Category'])
    
    X = ml_data.drop('Sales', axis=1)
    y = ml_data['Sales']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    
    return model, X.columns, mae

def forecast_future(df, model, feature_columns, months_to_forecast=6):
    """
    Predict future sales trends.
    """
    last_year = df['Year'].max()
    last_month = df[df['Year'] == last_year]['Month'].max()
    
    future_data = []
    
    # We'll forecast for each unique combination of Region and Category
    regions = df['Region'].unique()
    categories = df['Category'].unique()
    
    curr_month = last_month
    curr_year = last_year
    
    # Using a simplified forecasting approach for local estimation
    forecast_results = []
    
    for m in range(1, months_to_forecast + 1):
        curr_month += 1
        if curr_month > 12:
            curr_month = 1
            curr_year += 1
            
        for reg in regions:
            for cat in categories:
                # Prepare input row
                row = {
                    'Year': curr_year,
                    'Month': curr_month,
                    'Quarter': (curr_month - 1) // 3 + 1,
                    'IsMonthsEnd': 1 if curr_month in [3, 6, 9, 12] else 0,
                    'Prev_Month_Sales': df['Sales'].median() # Simplified lag for simplicity in demo
                }
                
                # Create dummy structure
                input_df = pd.DataFrame([row])
                
                # Add Region & Category columns
                input_df[f'Region_{reg}'] = 1
                input_df[f'Category_{cat}'] = 1
                
                # Reindex to match training columns
                input_df = input_df.reindex(columns=feature_columns, fill_value=0)
                
                pred_sales = model.predict(input_df)[0]
                
                # Collect result
                forecast_results.append({
                    'Date': pd.Timestamp(year=curr_year, month=curr_month, day=1),
                    'Year': curr_year,
                    'Month': curr_month,
                    'Region': reg,
                    'Category': cat,
                    'Predicted_Sales': max(0, pred_sales)
                })
                
    return pd.DataFrame(forecast_results)
