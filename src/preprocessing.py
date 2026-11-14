"""
Data Preprocessing Module
Performs data cleaning, duplicate removal, invalid rating filtration,
placeholder handling, and preparation for feature aggregation.
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pandas as pd
import numpy as np
from config import PROCESSED_REVIEWS_CSV, MIN_RATING, MAX_RATING

def clean_reviews_data(df):
    """
    Cleans review records:
    - Removes exact duplicates and duplicate user reviews for the same business
    - Parses and filters valid numeric ratings (1.0 to 5.0)
    - Strips placeholders ('0', empty strings) from reviews and labels
    - Creates standard business composite key ('place' + 'address')
    - Strips personally identifying reviewer information (User_name, Id) from model scope
    """
    print("Beginning Preprocessing...")
    initial_len = len(df)
    
    # 1. Standardize business identifiers
    df['place'] = df['place'].fillna('Unknown Business').astype(str).str.strip()
    df['address'] = df['address'].fillna('Unknown Address').astype(str).str.strip()
    df['business_id'] = df['place'] + " || " + df['address']
    
    # 2. Standardize ratings
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    valid_rating_mask = (df['rating'] >= MIN_RATING) & (df['rating'] <= MAX_RATING)
    df = df[valid_rating_mask].copy()
    print(f"Filtered invalid ratings: {initial_len - len(df)} dropped. Remaining: {len(df)}")

    # 3. Clean Text & Placeholders
    # Replace '0' placeholder in review text with empty string
    for text_col in ['original review', 'en review']:
        if text_col in df.columns:
            df[text_col] = df[text_col].astype(str).str.strip()
            df[text_col] = df[text_col].replace({'0': '', 'nan': '', 'None': ''})
    
    # Text length feature for review text
    df['review_char_len'] = df['en review'].str.len()
    df['has_text_review'] = (df['review_char_len'] > 0).astype(int)

    # 4. Remove Duplicates
    # Check for same user posting same review to same business
    df.drop_duplicates(inplace=True)
    before_dedup = len(df)
    df.drop_duplicates(subset=['business_id', 'User_name', 'en review'], inplace=True)
    print(f"Dropped duplicate reviews: {before_dedup - len(df)}. Remaining reviews: {len(df)}")

    # 5. Clean Aspect/Service Indicators (food, service, atmosphere)
    # In raw dataset, values are '0' when aspect wasn't filled, or qualitative scores like '5' or text
    for aspect in ['food', 'service', 'atmosphere']:
        if aspect in df.columns:
            df[f'{aspect}_numeric'] = pd.to_numeric(df[aspect], errors='coerce').fillna(0)
            df[f'has_{aspect}_feedback'] = (df[f'{aspect}_numeric'] > 0).astype(int)

    # 6. Sanitize PII
    # Drop reviewer personal identifiers from processed dataset
    pii_cols = ['Unnamed: 0', 'User_name', 'Id']
    sanitized_cols = [c for c in df.columns if c not in pii_cols]
    cleaned_df = df[sanitized_cols].copy()

    # Save cleaned reviews
    os.makedirs(os.path.dirname(PROCESSED_REVIEWS_CSV), exist_ok=True)
    cleaned_df.to_csv(PROCESSED_REVIEWS_CSV, index=False)
    print(f"Cleaned dataset saved to {PROCESSED_REVIEWS_CSV} (Shape: {cleaned_df.shape})")

    return cleaned_df

if __name__ == "__main__":
    from data_loading import load_raw_dataset_sample
    raw_sample = load_raw_dataset_sample()
    cleaned = clean_reviews_data(raw_sample)
    print("Preprocessing completed successfully.")
