"""
Sales Data Analysis Project
============================
Steps:
  1. Load dataset from "data/raw_sales.csv"
  2. Display basic info
  3. Remove missing values
  4. Convert "Order Date" column to datetime
  5. Create Month and Year columns
  6. Save cleaned data to "data/cleaned_sales.csv"
"""

import pandas as pd
import os

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
RAW_DATA_PATH     = "data/raw_sales.csv"
CLEANED_DATA_PATH = "data/cleaned_sales.csv"


# ─────────────────────────────────────────────
# STEP 1 — Load Dataset
# ─────────────────────────────────────────────
def load_data(filepath: str) -> pd.DataFrame:
    """Load the raw sales CSV into a DataFrame."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath)
    print("=" * 50)
    print("✅  Dataset loaded successfully!")
    print(f"    Path  : {filepath}")
    print(f"    Shape : {df.shape[0]} rows × {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────
# STEP 2 — Display Basic Info
# ─────────────────────────────────────────────
def display_basic_info(df: pd.DataFrame) -> None:
    """Print a summary of the DataFrame."""
    print("\n" + "=" * 50)
    print("📋  BASIC DATASET INFO")
    print("=" * 50)

    print("\n── Column Names & Data Types ──")
    print(df.dtypes.to_string())

    print("\n── First 5 Rows ──")
    print(df.head().to_string(index=False))

    print("\n── Missing Values per Column ──")
    missing = df.isnull().sum()
    print(missing.to_string())

    print("\n── Descriptive Statistics ──")
    print(df.describe().to_string())


# ─────────────────────────────────────────────
# STEP 3 — Remove Missing Values
# ─────────────────────────────────────────────
def remove_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that contain any missing values."""
    before = len(df)
    df_clean = df.dropna()
    after = len(df_clean)

    print("\n" + "=" * 50)
    print("🧹  Missing Value Removal")
    print(f"    Rows before : {before}")
    print(f"    Rows removed: {before - after}")
    print(f"    Rows after  : {after}")
    return df_clean


# ─────────────────────────────────────────────
# STEP 4 — Convert "Order Date" to datetime
# ─────────────────────────────────────────────
def convert_order_date(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the 'Order Date' column as datetime."""
    df = df.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    # Drop rows where date parsing failed
    invalid = df["Order Date"].isna().sum()
    if invalid > 0:
        print(f"\n⚠️   {invalid} row(s) had unparseable dates and were removed.")
        df = df.dropna(subset=["Order Date"])

    print("\n" + "=" * 50)
    print("📅  'Order Date' converted to datetime successfully.")
    return df


# ─────────────────────────────────────────────
# STEP 5 — Create Month and Year Columns
# ─────────────────────────────────────────────
def add_month_year_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Extract Month number and Year from 'Order Date'."""
    df = df.copy()
    df["Year"]       = df["Order Date"].dt.year
    df["Month"]      = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%B")   # e.g., "January"

    print("\n" + "=" * 50)
    print("📆  Month and Year columns added.")
    print(f"    Columns now: {list(df.columns)}")
    return df


# ─────────────────────────────────────────────
# STEP 6 — Save Cleaned Data
# ─────────────────────────────────────────────
def save_cleaned_data(df: pd.DataFrame, filepath: str) -> None:
    """Save the cleaned DataFrame to a CSV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)

    print("\n" + "=" * 50)
    print("💾  Cleaned data saved successfully!")
    print(f"    Path  : {filepath}")
    print(f"    Shape : {df.shape[0]} rows × {df.shape[1]} columns")
    print("=" * 50)


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def main():
    # 1. Load
    df = load_data(RAW_DATA_PATH)

    # 2. Display info
    display_basic_info(df)

    # 3. Remove missing values
    df = remove_missing_values(df)

    # 4. Convert Order Date to datetime
    df = convert_order_date(df)

    # 5. Add Month and Year columns
    df = add_month_year_columns(df)

    # 6. Save cleaned data
    save_cleaned_data(df, CLEANED_DATA_PATH)

    print("\n✅  Pipeline completed successfully!\n")


if __name__ == "__main__":
    main()
