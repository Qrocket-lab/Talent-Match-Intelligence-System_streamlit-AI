
# Phase 2: SQL Database & Matching Algorithm

## Objective
Implement the Success Formula as a scalable, maintainable SQL pipeline for enterprise-wide talent scoring.

## Database Architecture

### Tables Created
1. **`employee_assessments`**: Raw talent assessment data
2. **`talent_success_scores`**: Calculated scores and percentiles
3. **`performance_history`**: Historical performance ratings

### Core SQL Function: `calculate_talent_success_scores()`

```sql
WITH raw_data AS (
    SELECT 
        employee_id,
        SEA,
        CEX, 
        QDD,
        iq,
        Papi_T,
        Papi_G,
        performance_rating
    FROM employee_assessments
    WHERE assessment_date IS NOT NULL
),

calculated_scores AS (
    SELECT *,
        -- Success Formula Implementation
        (0.30 * SEA) + (0.20 * CEX) + (0.15 * QDD) + 
        (0.15 * iq) - (0.10 * Papi_T) - (0.10 * Papi_G) AS raw_success_score
    FROM raw_data
),

score_percentiles AS (
    SELECT *,
        -- Normalize scores for comparative ranking
        NTILE(100) OVER (ORDER BY raw_success_score) AS success_percentile
    FROM calculated_scores
)

SELECT 
    employee_id,
    raw_success_score AS talent_success_score,
    success_percentile,
    CASE 
        WHEN performance_rating = 5 THEN TRUE 
        ELSE FALSE 
    END AS is_high_performer,
    CURRENT_TIMESTAMP AS calculated_at
FROM score_percentiles;