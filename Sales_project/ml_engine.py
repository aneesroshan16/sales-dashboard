import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import streamlit as st

@st.cache_data
def prepare_data(df):
    """
    Standardize and clean data for analysis and ML.
    """
    required_cols = ['Year', 'Month', 'Region', 'Category', 'Sales']
    df = df[required_cols].copy()
    
    # Handle missing values
    df['Sales'] = df['Sales'].fillna(0)
    df['Region'] = df['Region'].fillna("Unknown")
    df['Category'] = df['Category'].fillna("General")
    
    # Group by time and categories
    df_grouped = df.groupby(['Year', 'Month', 'Region', 'Category'])['Sales'].sum().reset_index()
    
    # Sort for consistency
    df_grouped = df_grouped.sort_values(['Region', 'Category', 'Year', 'Month'])
    
    return df_grouped

@st.cache_resource
def train_model(df_grouped, timestamp):
    """
    Train an XGBoost model. The 'timestamp' forces retraining when data updates.
    """
    # Use only required features
    features_list = ['Year', 'Month', 'Region', 'Category']
    df_data = df_grouped[features_list + ['Sales']]
    
    # One-hot encoding for categorical variables
    ml_data = pd.get_dummies(df_data, columns=['Region', 'Category'])
    
    X = ml_data.drop('Sales', axis=1)
    y = ml_data['Sales']
    
    # Minimum rows for split
    if len(ml_data) > 2:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train, X_test, y_train, y_test = X, X, y, y
    
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.01,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='reg:squarederror'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    
    return model, X.columns, mae

def forecast_future(df, model, feature_columns, months_to_forecast=6):
    """
    Predict future sales trends using XGBoost.
    """
    last_year = df['Year'].max()
    last_month = df[df['Year'] == last_year]['Month'].max()
    
    regions = df['Region'].unique()
    categories = df['Category'].unique()
    
    curr_month = last_month
    curr_year = last_year
    
    forecast_results = []
    
    for _ in range(months_to_forecast):
        curr_month += 1
        if curr_month > 12:
            curr_month = 1
            curr_year += 1
            
        for reg in regions:
            for cat in categories:
                # Prepare input row
                row = {'Year': curr_year, 'Month': curr_month}
                input_df = pd.DataFrame([row])
                
                # Align with training One-Hot columns
                for col in feature_columns:
                    if col.startswith('Region_'):
                        input_df[col] = 1 if col == f'Region_{reg}' else 0
                    elif col.startswith('Category_'):
                        input_df[col] = 1 if col == f'Category_{cat}' else 0
                
                input_df = input_df.reindex(columns=feature_columns, fill_value=0)
                pred_sales = model.predict(input_df)[0]
                
                forecast_results.append({
                    'Date': pd.Timestamp(year=curr_year, month=curr_month, day=1),
                    'Year': curr_year,
                    'Month': curr_month,
                    'Region': reg,
                    'Category': cat,
                    'Predicted_Sales': max(0, float(pred_sales))
                })
                
    return pd.DataFrame(forecast_results)
