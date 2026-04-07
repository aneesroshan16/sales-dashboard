"""
Exploratory Data Analysis (EDA) — Cleaned Sales Dataset
=========================================================
Charts produced:
  1. Bar Chart  — Total Sales by Region
  2. Line Chart — Monthly Sales Trend
  3. Heatmap    — Region vs Category (total Sales)

Libraries : matplotlib, seaborn
Output dir : visuals/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─────────────────────────────────────────────
# GLOBAL STYLE SETUP
# Seaborn "whitegrid" gives clean backgrounds.
# A consistent color palette keeps charts
# visually cohesive.
# ─────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="Set2", font_scale=1.1)
OUTPUT_DIR = "visuals"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# LOAD CLEANED DATA
# ─────────────────────────────────────────────
def load_cleaned_data(path: str = "data/cleaned_sales.csv") -> pd.DataFrame:
    """
    Load the cleaned CSV produced by main.py.
    We parse 'Order Date' again so datetime operations work.
    """
    df = pd.read_csv(path, parse_dates=["Order Date"])
    print(f"✅  Loaded cleaned data → {df.shape[0]} rows × {df.shape[1]} cols\n")
    return df


# ─────────────────────────────────────────────
# CHART 1 — Bar Chart: Sales by Region
# ─────────────────────────────────────────────
def plot_sales_by_region(df: pd.DataFrame) -> None:
    """
    EXPLANATION
    -----------
    We group the DataFrame by 'Region' and sum up the 'Sales' column.
    A bar chart is perfect here because we're comparing discrete
    categories (regions) against a numeric value (total sales).

    Steps:
      • groupby('Region')['Sales'].sum()  → one total per region
      • sort_values()                     → tallest bar on the left
      • sns.barplot()                     → draw the chart
      • Annotate each bar with its value  → easier to read at a glance
    """
    region_sales = (
        df.groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = sns.barplot(
        data=region_sales,
        x="Region",
        y="Sales",
        palette="Set2",
        edgecolor="white",
        linewidth=0.8,
        ax=ax,
    )

    # Annotate each bar with its exact value
    for bar in bars.patches:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5,
            f"${bar.get_height():,.0f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#333333",
        )

    ax.set_title("💰  Total Sales by Region", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Region", fontsize=12)
    ax.set_ylabel("Total Sales ($)", fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_ylim(0, region_sales["Sales"].max() * 1.15)
    sns.despine()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "1_sales_by_region.png")
    plt.savefig(path, dpi=150)
    print(f"✅  Chart 1 saved → {path}")


# ─────────────────────────────────────────────
# CHART 2 — Line Chart: Monthly Sales Trend
# ─────────────────────────────────────────────
def plot_monthly_sales_trend(df: pd.DataFrame) -> None:
    """
    EXPLANATION
    -----------
    A line chart shows how a value changes over time — ideal for
    spotting seasonal patterns or growth trends in monthly sales.

    Steps:
      • groupby(['Year','Month'])['Sales'].sum() → one total per month
      • Create a readable 'Period' label (e.g. "Jan 2023")
      • sns.lineplot() with markers → each data point is visible
    """
    monthly = (
        df.groupby(["Year", "Month"])["Sales"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Month"])
    )

    # Build a human-readable period label for the x-axis
    monthly["Period"] = pd.to_datetime(
        monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
    ).dt.strftime("%b %Y")

    fig, ax = plt.subplots(figsize=(11, 5))

    sns.lineplot(
        data=monthly,
        x="Period",
        y="Sales",
        marker="o",
        markersize=8,
        linewidth=2.5,
        color="#2ecc71",
        ax=ax,
    )

    # Shade area under the line for visual emphasis
    ax.fill_between(
        range(len(monthly)),
        monthly["Sales"],
        alpha=0.12,
        color="#2ecc71",
    )

    # Annotate each point with its value
    for i, row in monthly.iterrows():
        idx = monthly.index.get_loc(i)
        ax.annotate(
            f"${row['Sales']:,.0f}",
            xy=(idx, row["Sales"]),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color="#1a7a45",
        )

    ax.set_title("📈  Monthly Sales Trend", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Total Sales ($)", fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(
        ticks=range(len(monthly)),
        labels=monthly["Period"].tolist(),
        rotation=45,
        ha="right",
        fontsize=9,
    )
    sns.despine()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "2_monthly_sales_trend.png")
    plt.savefig(path, dpi=150)
    print(f"✅  Chart 2 saved → {path}")


# ─────────────────────────────────────────────
# CHART 3 — Heatmap: Region vs Category
# ─────────────────────────────────────────────
def plot_region_category_heatmap(df: pd.DataFrame) -> None:
    """
    EXPLANATION
    -----------
    A heatmap uses color intensity to show where a metric (here: total
    Sales) is high or low across two dimensions simultaneously —
    in this case, Region (rows) vs Product Category (columns).

    Steps:
      • pivot_table() reshapes the data into a matrix form
        rows = Region, columns = Category, values = sum of Sales
      • sns.heatmap() colors each cell by its value
      • annot=True prints the number inside each cell
      • fmt='.0f' removes decimal places for cleaner display
    """
    pivot = df.pivot_table(
        index="Region",
        columns="Category",
        values="Sales",
        aggfunc="sum",
        fill_value=0,
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".0f",
        cmap="YlOrRd",           # Yellow → Orange → Red (low → high)
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Total Sales ($)", "shrink": 0.85},
        ax=ax,
    )

    ax.set_title(
        "🗺️  Sales Heatmap — Region vs Category",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Product Category", fontsize=12)
    ax.set_ylabel("Region", fontsize=12)
    ax.tick_params(axis="x", rotation=15)
    ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "3_region_category_heatmap.png")
    plt.savefig(path, dpi=150)
    print(f"✅  Chart 3 saved → {path}")


# ─────────────────────────────────────────────
# MAIN — Run all EDA charts
# ─────────────────────────────────────────────
def main():
    print("=" * 52)
    print("  📊  Sales EDA — Starting Analysis")
    print("=" * 52 + "\n")

    df = load_cleaned_data()

    print("── Chart 1: Sales by Region (Bar Chart) ──")
    plot_sales_by_region(df)

    print("\n── Chart 2: Monthly Sales Trend (Line Chart) ──")
    plot_monthly_sales_trend(df)

    print("\n── Chart 3: Region vs Category (Heatmap) ──")
    plot_region_category_heatmap(df)

    print("\n" + "=" * 52)
    print("  ✅  All charts saved to the 'visuals/' folder.")
    print("=" * 52)


if __name__ == "__main__":
    main()
