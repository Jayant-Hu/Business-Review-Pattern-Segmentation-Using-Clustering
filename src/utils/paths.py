"""
Centralized Configuration and Settings.
Uses pydantic-settings to validate environment variables, .env, and Streamlit secrets.
"""
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base Directory Resolution (parent.parent.parent of src/utils/paths.py is project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application configuration with default fallbacks and environment support."""
    
    # Environment & App Identity
    APP_NAME: str = "UrbanPulse AI"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Paths
    ROOT_DIR: Path = PROJECT_ROOT
    DATA_RAW_DIR: Path = PROJECT_ROOT / "dataset" / "raw"
    DATA_RAW_ZIP: Path = PROJECT_ROOT / "dataset" / "raw" / "combined2_dataset.csv.zip"
    DATA_RAW_CSV: Path = PROJECT_ROOT / "data" / "combined2_dataset.csv"
    DATA_SAMPLE_CSV: Path = PROJECT_ROOT / "dataset" / "sample" / "sample_10k_reviews.csv"
    DATA_PROCESSED_CSV: Path = PROJECT_ROOT / "dataset" / "processed" / "cleaned_reviews.csv"
    
    OUTPUT_DIR: Path = PROJECT_ROOT / "output"
    OUTPUT_GRAPHS_DIR: Path = PROJECT_ROOT / "output" / "graphs"
    OUTPUT_REPORTS_DIR: Path = PROJECT_ROOT / "output" / "reports"
    OUTPUT_RESULTS_DIR: Path = PROJECT_ROOT / "output" / "results"
    OUTPUT_MODELS_DIR: Path = PROJECT_ROOT / "output" / "models"
    
    GEO_CACHE_DIR: Path = PROJECT_ROOT / "data" / "geo_cache"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    # Model Artifacts
    KMEANS_MODEL_PATH: Path = PROJECT_ROOT / "output" / "models" / "kmeans_pipeline.joblib"
    PCA_MODEL_PATH: Path = PROJECT_ROOT / "output" / "models" / "pca_model.joblib"
    
    # Results CSV Files
    BUSINESS_FEATURES_CSV: Path = PROJECT_ROOT / "output" / "results" / "business_features.csv"
    CLUSTERED_BUSINESSES_CSV: Path = PROJECT_ROOT / "output" / "results" / "clustered_businesses.csv"
    CLUSTER_PROFILES_CSV: Path = PROJECT_ROOT / "output" / "results" / "cluster_profiles.csv"
    EVALUATION_RESULTS_CSV: Path = PROJECT_ROOT / "output" / "results" / "evaluation_results.csv"
    STABILITY_RESULTS_CSV: Path = PROJECT_ROOT / "output" / "results" / "stability_results.csv"
    ALGORITHM_COMPARISON_CSV: Path = PROJECT_ROOT / "output" / "results" / "algorithm_comparison.csv"
    PCA_PROJECTIONS_CSV: Path = PROJECT_ROOT / "output" / "results" / "pca_projections.csv"
    CITY_HOTSPOTS_CSV: Path = PROJECT_ROOT / "output" / "results" / "city_hotspots.csv"
    
    # Hyperparameters & ML Config
    RANDOM_STATE: int = 42
    SAMPLE_SIZE: int = 10000
    K_RANGE: List[int] = Field(default_factory=lambda: [2, 3, 4, 5, 6, 7])
    SELECTED_K: int = 4
    N_INIT: int = 15
    MIN_RATING: float = 1.0
    MAX_RATING: float = 5.0
    
    # Google Maps & Geocoding
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, validation_alias="GOOGLE_MAPS_API_KEY")
    GEOCODE_BATCH_SIZE: int = 50
    NOMINATIM_USER_AGENT: str = "urbanpulse-geocoder"
    NOMINATIM_RATE_LIMIT_SEC: float = 1.1

    # Profit Potential Index (PPI) Default Weights
    PPI_WEIGHT_SATISFACTION: float = 0.35
    PPI_WEIGHT_DEMAND: float = 0.30
    PPI_WEIGHT_COMPETITION: float = 0.20
    PPI_WEIGHT_RISK: float = 0.15
    BAYESIAN_PRIOR_WEIGHT: float = 5.0
    GLOBAL_MEAN_RATING: float = 4.0

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_google_maps_key(self) -> Optional[str]:
        """Safely fetch Google Maps Key from env or streamlit secrets without crashing."""
        if self.GOOGLE_MAPS_API_KEY and self.GOOGLE_MAPS_API_KEY.strip():
            return self.GOOGLE_MAPS_API_KEY.strip()
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GOOGLE_MAPS_API_KEY" in st.secrets:
                return st.secrets["GOOGLE_MAPS_API_KEY"]
        except Exception:
            pass
        return None

# Singleton settings instance
settings = Settings()
