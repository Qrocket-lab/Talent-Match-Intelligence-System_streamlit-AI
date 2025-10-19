# Phase 1: Data Preparation & Success Formula Discovery

## Objective
Analyze employee assessment data to identify the psychological traits that consistently predict high performance (Rating 5) and derive a quantifiable Success Formula.

## Data Sources
- Employee talent assessment scores (30+ psychological variables)
- Performance ratings (1-5 scale)
- Historical employment data

## Analytical Approach

### 1. Correlation Analysis
We examined the relationships between all talent variables and performance ratings:

**Key Positive Correlations:**
- SEA (Self-Efficacy & Achievement): 0.77
- CEX (Stakeholder Focus): 0.68
- QDD (Conscientiousness & Reliability): 0.81
- iq (Cognitive Complexity): 0.77

**Key Negative Correlations:**
- Papi_T (Theoretical/Strategic Focus): -0.83
- Papi_G (Need for Group Belonging): -0.77

### 2. Performance Gap Analysis
Compared median scores between high performers (Rating 5) and all other employees:

**Largest Performance Gaps:**
- SEA: 42-point difference (largest gap)
- CEX: 35-point difference
- Papi_T: High performers score 38% lower

### 3. Success Formula Derivation
Based on statistical evidence, we created a weighted formula:

```python
def calculate_success_score(SEA, CEX, QDD, iq, Papi_T, Papi_G):
    return (0.30 * SEA) + (0.20 * CEX) + (0.15 * QDD) + (0.15 * iq) - (0.10 * Papi_T) - (0.10 * Papi_G)