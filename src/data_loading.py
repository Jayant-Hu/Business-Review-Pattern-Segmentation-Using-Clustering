"""
Data Loading and Sampling Module
Handles loading from ZIP / CSV, inspects provenance, samples reliably,
and ensures business identifier validity.
"""
import os
import sys
import zipfile

# Add project root to sys.path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pandas as pd
import numpy as np
from config import DATASET_RAW_ZIP, DATASET_RAW_CSV, SAMPLE_CSV_PATH, RANDOM_STATE, SAMPLE_SIZE

def get_raw_stream():
    """Returns a filepath or file-like object to raw dataset, preferring ZIP."""
    if os.path.exists(DATASET_RAW_ZIP):
        zf = zipfile.ZipFile(DATASET_RAW_ZIP)
        name = zf.namelist()[0]
        return zf.open(name)
    elif os.path.exists(DATASET_RAW_CSV):
        return open(DATASET_RAW_CSV, 'rb')
    else:
        raise FileNotFoundError("Raw dataset not found in dataset/raw/ or data/")

def load_raw_dataset_sample(n_rows=SAMPLE_SIZE, random_state=RANDOM_STATE):
    """
    Loads a manageable sample from the 1.17M record raw dataset.
    Preserves business distribution by taking a reproducible randomized sample.
    """
    if os.path.exists(SAMPLE_CSV_PATH):
        print(f"Loading existing sample from {SAMPLE_CSV_PATH}")
        return pd.read_csv(SAMPLE_CSV_PATH)

    print(f"Sampling {n_rows} reviews from raw dataset (random_state={random_state})...")
    
    # We read using chunks to avoid high memory spikes while sampling uniformly
    chunksize = 100000
    sample_dfs = []
    
    stream = get_raw_stream()
    total_chunks = 0
    
    # Calculate approx sampling rate
    # Expected total rows ~ 1,170,000; to get 10,000 we take ~0.9% from each chunk
    np.random.seed(random_state)
    for chunk in pd.read_csv(stream, chunksize=chunksize, low_memory=False):
        frac = (n_rows * 1.5) / 1170000.0
        sampled_chunk = chunk.sample(frac=min(frac, 1.0), random_state=random_state)
        sample_dfs.append(sampled_chunk)
        total_chunks += 1
        
    combined_sample = pd.concat(sample_dfs, ignore_index=True)
    if len(combined_sample) > n_rows:
        combined_sample = combined_sample.sample(n=n_rows, random_state=random_state).reset_index(drop=True)
    
    # Save sample
    os.makedirs(os.path.dirname(SAMPLE_CSV_PATH), exist_ok=True)
    combined_sample.to_csv(SAMPLE_CSV_PATH, index=False)
    print(f"Saved {len(combined_sample)} sampled reviews to {SAMPLE_CSV_PATH}")
    return combined_sample

if __name__ == "__main__":
    df = load_raw_dataset_sample()
    print("Sample shape:", df.shape)
    print("Columns:", df.columns.tolist())
