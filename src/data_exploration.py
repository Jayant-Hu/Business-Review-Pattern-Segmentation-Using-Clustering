"""
Data Exploration and Visualization Module
Analyzes shapes, placeholder values, duplicates, distributions,
and generates academic-quality figures saved in output/graphs/.
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from config import OUTPUT_GRAPHS_DIR, OUTPUT_REPORTS_DIR

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.family': 'sans-serif'})

def perform_eda(df):
    """Executes statistical summary and visualizations."""
    os.makedirs(OUTPUT_GRAPHS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_REPORTS_DIR, exist_ok=True)

    print("=" * 60)
    print("DATA EXPLORATION REPORT")
    print("=" * 60)
    print(f"Total Review Sample Records: {len(df)}")
    print(f"Number of Columns: {df.shape[1]}")
    
    # 1. Identifier checks
    unique_ids = df['Id'].nunique()
    unique_users = df['User_name'].nunique()
    unique_places = df['place'].nunique()
    
    # Composite business identifier
    df['business_key'] = df['place'].astype(str).str.strip() + " || " + df['address'].astype(str).str.strip()
    unique_businesses = df['business_key'].nunique()

    print(f"Unique 'Id' values: {unique_ids}")
    print(f"Unique 'User_name' values: {unique_users}")
    print(f"Unique 'place' values: {unique_places}")
    print(f"Unique composite 'place + address' businesses: {unique_businesses}")
    print("Critical Architectural Validation: 'Id' represents Google Local reviewers, NOT businesses.")

    # 2. Placeholder Analysis: Count explicit '0' placeholders
    placeholder_counts = {}
    for col in df.columns:
        p_count = ((df[col] == 0) | (df[col] == '0') | (df[col].isnull())).sum()
        if p_count > 0:
            placeholder_counts[col] = p_count

    placeholder_df = pd.DataFrame(list(placeholder_counts.items()), columns=['Feature', 'Placeholder/Null Count'])
    placeholder_df['Percentage (%)'] = (placeholder_df['Placeholder/Null Count'] / len(df)) * 100
    placeholder_df.sort_values(by='Placeholder/Null Count', ascending=False, inplace=True)
    print("\nPlaceholder '0' & Missing Values:")
    print(placeholder_df)
    
    # 3. Duplicate Analysis
    dup_rows = df.duplicated().sum()
    dup_reviews = df.duplicated(subset=['business_key', 'User_name', 'en review']).sum()
    print(f"\nExact duplicate rows: {dup_rows}")
    print(f"Duplicate reviews (same user, business, and text): {dup_reviews}")

    # Visualizations
    # Chart 1: Placeholder / Missing values bar chart
    plt.figure(figsize=(10, 5))
    sns.barplot(data=placeholder_df.head(10), x='Percentage (%)', y='Feature', palette='Reds_r')
    plt.title("Proportion of Missing/Placeholder '0' Values (%)", fontsize=14, fontweight='bold')
    plt.xlabel("Percentage (%)")
    plt.ylabel("Dataset Feature")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "missing_values.png"), dpi=300)
    plt.close()

    # Chart 2: Rating distribution
    df['rating_numeric'] = pd.to_numeric(df['rating'], errors='coerce')
    plt.figure(figsize=(8, 5))
    order = sorted([r for r in df['rating_numeric'].dropna().unique() if r > 0])
    sns.countplot(data=df[df['rating_numeric'] > 0], x='rating_numeric', order=order, palette="Blues_r")
    plt.title("Customer Rating Distribution (1 to 5 Stars)", fontsize=14, fontweight='bold')
    plt.xlabel("Rating (Stars)")
    plt.ylabel("Number of Reviews")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "rating_distribution.png"), dpi=300)
    plt.close()

    # Chart 3: Top Business Categories
    plt.figure(figsize=(10, 6))
    top_categories = df['place type'].value_counts().head(10)
    sns.barplot(x=top_categories.values, y=top_categories.index, palette="viridis")
    plt.title("Top 10 Business Categories by Review Volume", fontsize=14, fontweight='bold')
    plt.xlabel("Number of Reviews")
    plt.ylabel("Place Type / Category")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "top_categories.png"), dpi=300)
    plt.close()

    # Chart 4: Business Review Frequency Distribution (log scale)
    reviews_per_biz = df['business_key'].value_counts()
    plt.figure(figsize=(8, 5))
    sns.histplot(reviews_per_biz, bins=30, kde=True, color='#2ecc71', log_scale=(True, False))
    plt.title("Sample Review Count per Business (Log-Scale Frequency)", fontsize=14, fontweight='bold')
    plt.xlabel("Reviews in Sample per Business")
    plt.ylabel("Number of Businesses")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "business_review_frequency.png"), dpi=300)
    plt.close()

    # Chart 5: Review Count Boxplot
    plt.figure(figsize=(8, 5))
    sns.boxplot(x=reviews_per_biz, color='#e74c3c')
    plt.title("Distribution of Sample Reviews per Business", fontsize=14, fontweight='bold')
    plt.xlabel("Review Count in Sample")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_GRAPHS_DIR, "review_count_distribution.png"), dpi=300)
    plt.close()

    print(f"All EDA visualizations successfully generated in {OUTPUT_GRAPHS_DIR}")
    return df

if __name__ == "__main__":
    from data_loading import load_raw_dataset_sample
    df = load_raw_dataset_sample()
    perform_eda(df)
