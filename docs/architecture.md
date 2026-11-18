# UrbanPulse AI: Architecture & System Design

## 1. Overview
UrbanPulse AI is an unsupervised machine learning and civic intelligence platform that analyzes commercial business reviews from Google Local / Maps, segments businesses according to behavioral signatures, and provides targeted city-service recommendations and spatial geospatial exploration.

---

## 2. Architecture Diagram

```mermaid
flowchart TD
    subgraph DataIngestion ["Data Ingestion & Sanitization"]
        RawZip["combined2_dataset.csv.zip (1.17M)"] --> ChunkSampler["Chunked Uniform Sampler (10k)"]
        ChunkSampler --> Sanitizer["PII Removal & Deduplication"]
        Sanitizer --> CompositeKey["Composite Key: (place, address)"]
    end

    subgraph FeatureEngineering ["Feature Engineering Layer"]
        CompositeKey --> Aggregator["10-D Feature Aggregator"]
        Aggregator --> SkewTransforms["Log Transforms (Counts, Length)"]
        SkewTransforms --> Scaler["StandardScaler"]
    end

    subgraph MLCore ["Machine Learning & Clustering Core"]
        Scaler --> KMeansPipeline["K-Means Clustering (K=2..7, Selected K=4)"]
        Scaler --> Hierarchical["Agglomerative Hierarchical (Ward Linkage)"]
        Scaler --> PCAModel["2D PCA Projection (53.63% Variance)"]
        KMeansPipeline --> DynamicNaming["Data-Driven Segment Naming Engine"]
    end

    subgraph GeospatialLayer ["Geospatial & Geocoding Layer"]
        CompositeKey --> CityParser["Address & City Parser (GCC/Intl)"]
        CityParser --> GeoCache["SQLite Geocode Cache"]
        GeoCache --> PrimaryGoogle["Google Maps Geocoding API"]
        GeoCache --> CentroidFallback["Centroid Spatial Jitter Engine"]
    end

    subgraph PresentationLayer ["Streamlit UI & Visualization"]
        DynamicNaming --> SaaSApp["UrbanPulse Streamlit Dashboard"]
        PCAModel --> SaaSApp
        PrimaryGoogle --> MapExplorer["Interactive Map Explorer (JS API + PyDeck)"]
        CentroidFallback --> MapExplorer
    end
```

---

## 3. Core Modules

| Module Path | Responsibility |
|:---|:---|
| `src/data/` | Chunked raw streaming, schema validation, deduplication, and PII sanitization. |
| `src/features/` | Aggregation from review transactions to business profiles. |
| `src/models/` | K-Means sklearn pipeline, Ward agglomerative clustering, PCA, stability analysis (ARI). |
| `src/geo/` | Multilevel geocoding (Google Maps API + SQLite cache + city centroid jitter). |
| `src/services/` | Data-driven cluster naming, real-time KPI aggregations, and city hotspot ranking. |
| `src/ui/` | Glassmorphism components, dark navy styles, and responsive Plotly visual builders. |
| `src/pages/` | Modular page renderers (Overview, Dataset, Review Analytics, Models, PCA, Metrics, Segmentation, Recommendations, Map Explorer). |
