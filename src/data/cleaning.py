"""
Data Cleaning & PII Sanitization.
Constructs composite business keys, cleans ratings, and removes reviewer identifiers.
"""
import pandas as pd
import numpy as np
from src.utils.paths import settings
from src.utils.logging import logger
from src.data.schema import validate_raw_dataframe

def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw review transactions:
    - Normalizes composite business identifier: (place, address)
    - Validates ratings in [1.0, 5.0]
    - Removes duplicate reviews
    - Strips placeholders ('0', empty strings)
    - Sanitizes PII ('Unnamed: 0', 'User_name', 'Id')
    """
    validate_raw_dataframe(df)
    logger.info(f"Initiating data cleaning on {len(df)} review records...")
    
    clean_df = df.copy()
    
    # 1. Composite business identifier
    clean_df['place'] = clean_df['place'].fillna('Unknown Business').astype(str).str.strip()
    clean_df['address'] = clean_df['address'].fillna('Unknown Address').astype(str).str.strip()
    clean_df['place type'] = clean_df['place type'].fillna('General').astype(str).str.strip()
    clean_df['business_id'] = clean_df['place'] + " || " + clean_df['address']
    
    # 2. Rating validation
    clean_df['rating'] = pd.to_numeric(clean_df['rating'], errors='coerce')
    valid_mask = (clean_df['rating'] >= settings.MIN_RATING) & (clean_df['rating'] <= settings.MAX_RATING)
    clean_df = clean_df[valid_mask].copy()
    
    # 3. Clean text fields
    for col in ['original review', 'en review']:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].astype(str).str.strip()
            clean_df[col] = clean_df[col].replace({'0': '', 'nan': '', 'None': ''})
            
    clean_df['review_char_len'] = clean_df['en review'].str.len()
    clean_df['has_text_review'] = (clean_df['review_char_len'] > 0).astype(int)
    
    # 4. Deduplication
    clean_df = clean_df.drop_duplicates()
    if 'User_name' in clean_df.columns:
        clean_df = clean_df.drop_duplicates(subset=['business_id', 'User_name', 'en review'])
        
    # 5. Aspect indicators (food, service, atmosphere)
    for aspect in ['food', 'service', 'atmosphere']:
        if aspect in clean_df.columns:
            clean_df[f'{aspect}_numeric'] = pd.to_numeric(clean_df[aspect], errors='coerce').fillna(0)
            clean_df[f'has_{aspect}_feedback'] = (clean_df[f'{aspect}_numeric'] > 0).astype(int)
            
    # 6. Sanitize PII
    pii_cols = ['Unnamed: 0', 'User_name', 'Id']
    sanitized_cols = [c for c in clean_df.columns if c not in pii_cols]
    sanitized_df = clean_df[sanitized_cols].copy()
    
    # Save cleaned reviews
    settings.DATA_PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    sanitized_df.to_csv(settings.DATA_PROCESSED_CSV, index=False)
    logger.info(f"Saved cleaned and sanitized reviews to {settings.DATA_PROCESSED_CSV} (Shape: {sanitized_df.shape})")
    
    return sanitized_df

def sanitize_review_text(text: str, max_len: int = 180) -> str:
    """
    Sanitizes review excerpt text by stripping PII:
    - Removes emails
    - Removes phone numbers
    - Removes web URLs and social handles
    - Caps string length cleanly with an ellipsis
    """
    import re
    if not text or not isinstance(text, str):
        return ""
    
    cleaned = text.strip()
    # Mask email addresses
    cleaned = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[email]', cleaned)
    # Mask phone numbers
    cleaned = re.sub(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', '[phone]', cleaned)
    # Mask web links
    cleaned = re.sub(r'https?://\S+|www\.\S+', '[link]', cleaned)
    # Mask social @handles
    cleaned = re.sub(r'@\w+', '[user]', cleaned)
    # Normalize multiple whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    if len(cleaned) > max_len:
        return cleaned[:max_len].rsplit(' ', 1)[0] + "..."
    return cleaned
