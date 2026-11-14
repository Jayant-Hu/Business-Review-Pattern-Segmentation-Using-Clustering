"""
Global Configuration and Project Constants
"""
import os

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATASET_RAW_ZIP = os.path.join(PROJECT_ROOT, "dataset", "raw", "combined2_dataset.csv.zip")
DATASET_RAW_CSV = os.path.join(PROJECT_ROOT, "data", "combined2_dataset.csv")
SAMPLE_CSV_PATH = os.path.join(PROJECT_ROOT, "dataset", "sample", "sample_10k_reviews.csv")
PROCESSED_REVIEWS_CSV = os.path.join(PROJECT_ROOT, "dataset", "processed", "cleaned_reviews.csv")
BUSINESS_FEATURES_CSV = os.path.join(PROJECT_ROOT, "output", "results", "business_features.csv")
CLUSTERED_BUSINESSES_CSV = os.path.join(PROJECT_ROOT, "output", "results", "clustered_businesses.csv")
CLUSTER_PROFILES_CSV = os.path.join(PROJECT_ROOT, "output", "results", "cluster_profiles.csv")
EVALUATION_RESULTS_CSV = os.path.join(PROJECT_ROOT, "output", "results", "evaluation_results.csv")

OUTPUT_GRAPHS_DIR = os.path.join(PROJECT_ROOT, "output", "graphs")
OUTPUT_REPORTS_DIR = os.path.join(PROJECT_ROOT, "output", "reports")
OUTPUT_RESULTS_DIR = os.path.join(PROJECT_ROOT, "output", "results")

# Sampling & Reproducibility
RANDOM_STATE = 42
SAMPLE_SIZE = 10000
K_RANGE = [2, 3, 4, 5, 6, 7]
N_INIT = 15

# Review and Rating Parameters
MIN_RATING = 1.0
MAX_RATING = 5.0
