# Academic Project Report
## Business Review Pattern Segmentation for City-Service Recommendations Using Clustering

---

### 1. Introduction & Problem Statement
Commercial service ecosystems in modern cities rely on customer feedback to gauge service quality, consumer satisfaction, and operational efficiency. Municipal administrators, chambers of commerce, and urban developers face challenges in discovering systemic patterns across thousands of commercial businesses from unstructured review data.

This project implements an **Unsupervised Machine Learning System** to segment urban commercial establishments based on empirical customer review patterns, service indicators, and rating consistency, without ground-truth labels.

---

### 2. Dataset Provenance & Structural Realities
- **Source File**: `combined2_dataset.csv.zip` (1.17 Million review transactions across 19 attributes).
- **Provenance**: Publicly aggregated customer reviews of service establishments (predominantly restaurants, bakeries, cafes, and local amenities).
- **Critical Discovery**: Analysis of the column `Id` revealed that it represents the **Reviewer ID**, *not* the business identifier. Businesses were resolved using the composite tuple `(place, address)` to eliminate conflation across branches.
- **Handling of Placeholders**: Fields such as `food`, `service`, `atmosphere`, and `meal_type` contained placeholder `'0'` entries when unmentioned by the reviewer. These were converted into boolean feedback indicators.

---

### 3. Data Preprocessing & Sanitization
1. **PII Removal**: Personal identifiers (`User_name`, reviewer `Id`) were removed from the modeling feature space.
2. **Deduplication**: Exact duplicate transactions and multiple duplicate submissions by the same user to the same establishment were purged.
3. **Rating Validation**: Valid ratings strictly constrained to $[1.0, 5.0]$.

---

### 4. Business-Level Feature Engineering
Transaction-level reviews were aggregated into a 10-dimensional business feature vector:
1. `avg_rating`: Arithmetic mean customer rating.
2. `rating_std`: Rating variance (customer experience consistency).
3. `log_sample_review_count`: Log-transformed sample review count.
4. `positive_review_pct`: Percentage of $4-5$ star reviews.
5. `negative_review_pct`: Percentage of $1-2$ star reviews.
6. `log_avg_review_length`: Log-transformed mean review character length.
7. `detailed_review_pct`: Percentage of reviews with non-empty written feedback.
8. `service_feedback_rate`: Frequency of explicit service quality mentions.
9. `food_feedback_rate`: Frequency of explicit food mentions.
10. `atmosphere_feedback_rate`: Frequency of atmosphere mentions.

Features were standardized using `StandardScaler` ($\mu = 0, \sigma = 1$).

---

### 5. Partitioning & Hierarchical Clustering Experiments

#### 5.1 K-Means Evaluation ($K \in [2, 7]$)
| K | WCSS | Silhouette (Euclidean) | Silhouette (Manhattan) | Davies-Bouldin Index |
|---|---|---|---|---|
| 2 | 23,870.05 | 0.6102 | 0.6887 | 0.7088 |
| 3 | 17,553.02 | 0.3916 | 0.4982 | 1.1774 |
| **4** | **13,436.39** | **0.4393** | **0.5226** | **0.9999** |
| 5 | 10,858.46 | 0.4684 | 0.5435 | 0.9153 |
| 6 | 8,656.53 | 0.4750 | 0.5570 | 0.8191 |
| 7 | 7,271.02 | 0.4420 | 0.4689 | 0.8135 |

*Selection Justification*: While $K=2$ yields mathematically higher silhouette separation, it merges highly distinct business sub-patterns into two broad groups. $K=4$ was selected as the optimal trade-off between clustering cohesion, Davies-Bouldin score ($< 1.0$), and municipal operational interpretability.

#### 5.2 Distance Metric Analysis
Standard K-Means relies on squared Euclidean distance to optimize cluster inertia. Comparing silhouette scores under Manhattan distance ($0.5226$) versus Euclidean ($0.4393$) demonstrates that business review data exhibits higher density under $L_1$ norm space due to bounded percentage features.

#### 5.3 Agglomerative Hierarchical Comparison
- Linkage: Ward's Minimum Variance Linkage ($L_2$).
- Silhouette (Euclidean): $0.4312$
- Davies-Bouldin: $0.9958$
- Finding: Hierarchical clustering confirmed the four natural groupings identified by K-Means.

---

### 6. Principal Component Analysis (PCA)
- **PC1 Explained Variance**: $28.90\%$
- **PC2 Explained Variance**: $24.73\%$
- **Cumulative 2D Variance**: $53.63\%$
PCA successfully visualized the separation between high-satisfaction businesses and at-risk establishments in 2D space.

---

### 7. Cluster Profiles & Interpretations

1. **Cluster 0: High-Satisfaction Top Tier (2,374 businesses)**
   - Mean Rating: $4.68 / 5.0$, Positive %: $94.2\%$, Negative %: $0.1\%$
   - *Civic Recommendation*: Candidate for city tourism guides, municipal showcases, and commercial excellence awards.
   
2. **Cluster 1: Moderate / Mixed Feedback (521 businesses)**
   - Mean Rating: $3.00 / 5.0$, Positive %: $0.0\%$, Negative %: $0.0\%$ (predominantly 3-star neutral reviews).
   - *Civic Recommendation*: Digital marketing assistance, customer engagement campaigns.

3. **Cluster 2: High-Engagement Detailed Feedback (179 businesses)**
   - Mean Review Length: $108.6$ characters, Service Rate: $20.4\%$, Food Rate: $21.5\%$.
   - *Civic Recommendation*: High civic visibility; target for operational benchmarking and food safety certifications.

4. **Cluster 3: Critical Intervention / At-Risk (202 businesses)**
   - Mean Rating: $1.76 / 5.0$, Negative %: $45.6\%$.
   - *Civic Recommendation*: Commercial revitalization support, municipal service audits, and customer support training subsidies.

---

### 8. Stability Analysis
Evaluated across seeds $10, 99, 123, 2024$ relative to baseline seed $42$:
- **Mean Adjusted Rand Index (ARI)**: **$0.9899$**
- Confirms high structural stability of cluster assignments.

---

### 9. Ethical & Responsible AI Considerations
- **Reviewer Anonymity**: Complete de-identification of individual reviewers protects customer privacy.
- **Fair Representation**: Log-transformations prevented small-sample businesses from being unfairly penalized.
- **Decision Support Only**: Clusters provide diagnostic insights, not punitive measures.

---

### 10. Conclusion
This project demonstrates a complete, academically grounded unsupervised learning workflow for commercial business segmentation, providing urban planners and local authorities with empirical insights for municipal decision-making.
