"""
Robust data loader for raw review records with chunked uniform sampling.
"""
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path
from src.utils.paths import settings
from src.utils.logging import logger
from src.utils.exceptions import DataLoadingError
from src.data.schema import validate_raw_dataframe

def get_raw_stream():
    """Returns a file-like stream to the raw dataset, prioritizing zip archive."""
    if settings.DATA_RAW_ZIP.exists():
        logger.info(f"Opening raw dataset from ZIP: {settings.DATA_RAW_ZIP}")
        zf = zipfile.ZipFile(settings.DATA_RAW_ZIP)
        name = zf.namelist()[0]
        return zf.open(name)
    elif settings.DATA_RAW_CSV.exists():
        logger.info(f"Opening raw dataset from CSV: {settings.DATA_RAW_CSV}")
        return open(settings.DATA_RAW_CSV, 'rb')
    else:
        raise DataLoadingError("Neither dataset/raw/combined2_dataset.csv.zip nor data/combined2_dataset.csv was found.")

def load_or_create_sample(sample_size: int = settings.SAMPLE_SIZE, random_state: int = settings.RANDOM_STATE, force_recompute: bool = False) -> pd.DataFrame:
    """
    Loads pre-sampled review dataframe or samples uniformly in chunks from 1.17M raw records.
    """
    if settings.DATA_SAMPLE_CSV.exists() and not force_recompute:
        logger.info(f"Loading existing sample from {settings.DATA_SAMPLE_CSV}")
        df = pd.read_csv(settings.DATA_SAMPLE_CSV, low_memory=False)
        validate_raw_dataframe(df)
        return df

    logger.info(f"Sampling {sample_size} records from raw dataset (random_state={random_state})...")
    chunksize = 100000
    sample_dfs = []
    stream = get_raw_stream()
    
    np.random.seed(random_state)
    for chunk in pd.read_csv(stream, chunksize=chunksize, low_memory=False):
        # sample ~1.5x expected rate per chunk to ensure enough records
        frac = (sample_size * 1.5) / 1170000.0
        sampled_chunk = chunk.sample(frac=min(frac, 1.0), random_state=random_state)
        sample_dfs.append(sampled_chunk)
        
    combined = pd.concat(sample_dfs, ignore_index=True)
    if len(combined) > sample_size:
        combined = combined.sample(n=sample_size, random_state=random_state).reset_index(drop=True)
        
    settings.DATA_SAMPLE_CSV.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(settings.DATA_SAMPLE_CSV, index=False)
    logger.info(f"Successfully saved {len(combined)} sampled records to {settings.DATA_SAMPLE_CSV}")
    validate_raw_dataframe(combined)
    return combined
